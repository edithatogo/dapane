using Libdl
using Test
using Dapane

const ROOT = normpath(joinpath(@__DIR__, "..", "..", "..", ".."))
const LIBRARY = get(ENV, "DAPANE_ABI_LIBRARY", joinpath(ROOT, "bindings/polyglot/abi/target/release", Dapane.expected_library_name()))
const CLI = get(ENV, "DAPANE_CLI", joinpath(ROOT, "target/release/dapane"))

function cli_stdout(command, path)
    output = read(`$CLI $command $path`, String)
    chomp(output)
end

function cli_stderr(command, path)
    err = IOBuffer()
    process = run(pipeline(`$CLI $command $path`; stdout = devnull, stderr = err); wait = false)
    wait(process)
    success(process) && error("expected the CLI to fail")
    chomp(String(take!(err)))
end

@testset "target-native library name" begin
    @test_throws ArgumentError Dapane.resolve_library("")
    wrong = tempname() * (Sys.isapple() ? ".so" : ".dylib")
    write(wrong, "not a library")
    @test_throws ArgumentError Dapane.resolve_library(wrong)
    rm(wrong)
end

@testset "shared fixtures keep the kernel bytes" begin
    point = read(joinpath(ROOT, "fixtures/workforce.json"), String)
    @test Dapane.evaluate_json(point; library = LIBRARY) == cli_stdout("evaluate", joinpath(ROOT, "fixtures/workforce.json"))
    interval = read(joinpath(ROOT, "fixtures/intervals/rate-boundary.json"), String)
    @test Dapane.evaluate_json(interval; library = LIBRARY, operation = :interval) ==
          cli_stdout("evaluate-intervals", joinpath(ROOT, "fixtures/intervals/rate-boundary.json"))
end

@testset "errors, lifetime and collection" begin
    request = Vector{UInt8}(codeunits(read(joinpath(ROOT, "fixtures/workforce.json"), String)))
    status, body = Dapane.evaluate_bytes(request; library = LIBRARY)
    fill!(request, 0xff)
    GC.gc()
    @test status == Dapane.OK
    @test body == Vector{UInt8}(codeunits(cli_stdout("evaluate", joinpath(ROOT, "fixtures/workforce.json"))))

    empty_file = tempname()
    write(empty_file, "{}")
    error = try
        Dapane.evaluate_json("{}", library = LIBRARY)
    catch caught
        caught
    end
    @test error isa Dapane.DapaneError
    @test error.status == Dapane.CORE_ERROR
    @test error.body == cli_stderr("evaluate", empty_file)
    rm(empty_file)

    @test_throws ArgumentError Dapane.evaluate_json(missing; library = LIBRARY)
    status, body = Dapane.evaluate_bytes(UInt8[0xff]; library = LIBRARY)
    @test status == UInt32(6)
    @test isempty(body)

    status, body = Dapane.evaluate_bytes(UInt8[]; library = LIBRARY, requested_abi = UInt32(99))
    @test status == UInt32(3)
    @test isempty(body)

    library = Dapane.resolve_library(LIBRARY)
    opened = dlopen(library)
    handle = Ref{UInt64}(7)
    status = ccall(
        dlsym(opened, :dapane_v1_evaluate),
        UInt32,
        (UInt32, UInt32, Ptr{UInt8}, Csize_t, Ptr{UInt64}),
        Dapane.ABI_VERSION,
        Dapane.POINT,
        C_NULL,
        Csize_t(0),
        handle,
    )
    @test status == UInt32(2)
    @test handle[] == 7

    handle = Ref{UInt64}(0)
    status = ccall(
        dlsym(opened, :dapane_v1_evaluate),
        UInt32,
        (UInt32, UInt32, Ptr{UInt8}, Csize_t, Ptr{UInt64}),
        Dapane.ABI_VERSION,
        Dapane.POINT,
        C_NULL,
        Csize_t(0),
        handle,
    )
    @test status == Dapane.CORE_ERROR
    @test handle[] != 0
    @test ccall(dlsym(opened, :dapane_v1_result_free), UInt32, (UInt64,), handle[]) == Dapane.OK
    @test ccall(dlsym(opened, :dapane_v1_result_free), UInt32, (UInt64,), handle[]) == UInt32(8)
end
