# Install the archive or stage the package beside its host library, then compare
# every prepared case to the CLI bytes. This file is outside Pkg.test.

const isolated = !isempty(ARGS) && first(ARGS) == "--isolated"
isolated && popfirst!(ARGS)
const from_archive = !isempty(ARGS) && first(ARGS) == "--archive"
from_archive && popfirst!(ARGS)
length(ARGS) == 4 || error("Usage: installed.jl [--archive] STAGE DEPOT CASES LIBRARY_OR_ARCHIVE")
const stage, depot, cases, source = abspath.(ARGS)
const repo = normpath(joinpath(@__DIR__, "..", "..", "..", ".."))
if !isolated
    for path in (stage, depot)
        startswith(relpath(path, repo), ".." * (Sys.iswindows() ? "\\" : "/")) ||
            error("Install paths must be outside the checkout: $path")
        ispath(path) && error("Refusing to reuse $path")
    end
    separator = Sys.iswindows() ? ";" : ":"
    mode = from_archive ? ["--archive"] : String[]
    cmd = `$(Base.julia_cmd()) --startup-file=no $(@__FILE__) --isolated $mode $stage $depot $cases $source`
    run(addenv(cmd, "JULIA_DEPOT_PATH" => depot * separator, "JULIA_LOAD_PATH" => "@" * separator * "@stdlib"))
    exit()
end
first(DEPOT_PATH) == depot || error("Julia did not initialize the requested depot")
isfile(source) || error("Missing library or archive $source")
isfile(joinpath(cases, "cases.tsv")) || error("Missing prepared cases in $cases")

using Pkg
using Tar

if from_archive
    Sys.isapple() && Sys.ARCH == :aarch64 || error("Archive qualification is for macOS arm64")
    expected = [
        "LICENSE", "NOTICE", "Project.toml", "THIRD_PARTY_NOTICES.txt",
        "artifacts/libdapane_abi.dylib", "src/Dapane.jl",
    ]
    members = Tar.list(source)
    all(entry -> entry.type == :file, members) || error("Archive must contain regular files")
    sort([entry.path for entry in members]) == expected || error("Unexpected package members")
    Tar.extract(source, stage)
else
    mkpath(joinpath(stage, "src"))
    mkpath(joinpath(stage, "artifacts"))
    cp(joinpath(@__DIR__, "..", "Project.toml"), joinpath(stage, "Project.toml"))
    cp(joinpath(@__DIR__, "..", "src", "Dapane.jl"), joinpath(stage, "src", "Dapane.jl"))
    cp(source, joinpath(stage, "artifacts", basename(source)))
end

Pkg.activate(joinpath(depot, "env"); io = devnull)
Pkg.develop(path = stage; io = devnull)

using Dapane
using Test

@testset "installed artifact" begin
    resolved = Dapane.resolve_library()
    @test realpath(pathof(Dapane)) == realpath(joinpath(stage, "src", "Dapane.jl"))
    @test Base.active_project() == joinpath(depot, "env", "Project.toml")
    @test resolved == abspath(joinpath(stage, "artifacts", Dapane.expected_library_name()))
    @test basename(resolved) == Dapane.expected_library_name()
end

rows = readlines(joinpath(cases, "cases.tsv"))
@testset "installed shared cases" begin
    @test length(rows) > 1
    checked = 0
    for row in rows[2:end]
        isempty(row) && continue
        name, operation, status = split(row, '\t')
        request = read(joinpath(cases, "$name.input.json"), String)
        expected = read(joinpath(cases, "$name.output.json"), String)
        opcode = operation == "point" ? :point : :interval
        if status == "ok"
            actual = evaluate_json(request; operation = opcode)
            @test actual == expected
            if checked == 0
                buffer = Vector{UInt8}(codeunits(request))
                code, body = Dapane.evaluate_bytes(buffer; operation = opcode)
                fill!(buffer, 0xff)
                GC.gc()
                @test code == Dapane.OK
                @test String(body) == expected
            end
        else
            caught = try
                evaluate_json(request; operation = opcode)
                nothing
            catch error
                error
            end
            @test caught isa Dapane.DapaneError
            @test caught.status == Dapane.CORE_ERROR
            @test caught.body == expected
        end
        checked += 1
    end
    @test checked == length(filter(!isempty, rows)) - 1
end
