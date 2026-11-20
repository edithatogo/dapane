"""Julia caller for the versioned Dapane C ABI.

The wrapper copies request and result bytes into Julia memory and releases every
Rust handle before returning. It does not decode amounts or repeat the kernel's
arithmetic. BinaryBuilder/JLL packaging is not selected.
"""
module Dapane

using Libdl

export ABI_VERSION, CORE_ERROR, DapaneError, OK, evaluate_bytes, evaluate_json, resolve_library

const _loaded = Dict{String, Ptr{Cvoid}}()
const _load_lock = ReentrantLock()

function _symbol(library::AbstractString, name::Symbol)
    handle = lock(_load_lock) do
        get!(_loaded, library) do
            dlopen(library)
        end
    end
    dlsym(handle, name)
end

const ABI_VERSION = UInt32(1)
const OK = UInt32(0)
const CORE_ERROR = UInt32(1)
const INVALID_ARGUMENT = UInt32(2)
const ABI_MISMATCH = UInt32(3)
const POINT = UInt32(1)
const INTERVAL = UInt32(2)

struct DapaneError <: Exception
    status::UInt32
    body::String
end

Base.showerror(io::IO, error::DapaneError) = print(io, "Dapane ABI status ", error.status)

function expected_library_name()
    if Sys.iswindows()
        "dapane_abi.dll"
    elseif Sys.isapple()
        "libdapane_abi.dylib"
    else
        "libdapane_abi.so"
    end
end

"""Resolve one target-native `dapane-abi` library path.

`library` is required. A file whose name belongs to another platform is rejected
even when that file exists.
"""
function resolve_library(library::AbstractString)
    isempty(library) && throw(ArgumentError("Pass the target-native dapane-abi library path."))
    path = abspath(library)
    isfile(path) || throw(ArgumentError("Dapane ABI library does not exist: $path"))
    name = basename(path)
    expected = expected_library_name()
    name == expected || throw(ArgumentError("This host requires $expected, not $name."))
    path
end

function _operation(operation::Symbol)
    operation === :point && return POINT
    operation === :interval && return INTERVAL
    throw(ArgumentError("Operation must be :point or :interval."))
end

function _copy_result(library::AbstractString, handle::UInt64)
    length_out = Ref{Csize_t}(0)
    status = ccall(
        _symbol(library, :dapane_v1_result_length),
        UInt32,
        (UInt64, Ptr{Csize_t}),
        handle,
        length_out,
    )
    status == OK || return status, UInt8[]
    buffer = Vector{UInt8}(undef, length_out[])
    written = Ref{Csize_t}(0)
    status = GC.@preserve buffer ccall(
        _symbol(library, :dapane_v1_result_copy),
        UInt32,
        (UInt64, Ptr{UInt8}, Csize_t, Ptr{Csize_t}),
        handle,
        pointer(buffer),
        Csize_t(length(buffer)),
        written,
    )
    status == OK || return status, UInt8[]
    written[] == length(buffer) || error("Dapane returned an incomplete result buffer")
    OK, buffer
end

function _free(library::AbstractString, handle::UInt64)
    ccall(_symbol(library, :dapane_v1_result_free), UInt32, (UInt64,), handle)
end

"""Evaluate one borrowed byte buffer and return `(status, copied_bytes)`.

`OK` and `CORE_ERROR` include the complete UTF-8 JSON body. Every returned
handle is freed before this function returns. The input vector is preserved
across the foreign call and is not retained by Rust.
"""
function evaluate_bytes(
    request::AbstractVector{UInt8};
    library::AbstractString,
    operation::Symbol = :point,
    requested_abi::UInt32 = ABI_VERSION,
)
    library = resolve_library(library)
    opcode = _operation(operation)
    handle = Ref{UInt64}(0)
    # The C function consumes contiguous bytes, including when the caller supplies a view.
    input = request isa Vector{UInt8} ? request : collect(request)
    request_ptr = isempty(input) ? Ptr{UInt8}(C_NULL) : pointer(input)
    status = GC.@preserve input ccall(
        _symbol(library, :dapane_v1_evaluate),
        UInt32,
        (UInt32, UInt32, Ptr{UInt8}, Csize_t, Ptr{UInt64}),
        requested_abi,
        opcode,
        request_ptr,
        Csize_t(length(input)),
        handle,
    )
    if status != OK && status != CORE_ERROR
        handle[] == 0 || _free(library, handle[])
        return status, UInt8[]
    end
    local body = UInt8[]
    local copy_status = OK
    try
        copy_status, body = _copy_result(library, handle[])
    finally
        _free(library, handle[])
    end
    copy_status == OK || return copy_status, UInt8[]
    status, body
end

function evaluate_json(request::Missing; library::AbstractString, operation::Symbol = :point)
    throw(ArgumentError("Supply one non-missing JSON string."))
end

"""Evaluate one JSON string through the C ABI and return the kernel's JSON bytes as a `String`."""
function evaluate_json(
    request::AbstractString;
    library::AbstractString,
    operation::Symbol = :point,
)
    isvalid(request) || throw(ArgumentError("JSON input must be valid UTF-8."))
    status, body = evaluate_bytes(Vector{UInt8}(codeunits(request)); library, operation)
    text = status == OK || status == CORE_ERROR ? String(body) : ""
    status == OK && return text
    throw(DapaneError(status, text))
end

end
