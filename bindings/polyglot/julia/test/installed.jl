# Install a staged copy of the package, with the host library beside it, and
# compare every prepared case to the CLI bytes. This file is not part of Pkg.test.

const isolated = !isempty(ARGS) && first(ARGS) == "--isolated"
isolated && popfirst!(ARGS)
length(ARGS) == 4 || error("Usage: installed.jl STAGE DEPOT CASES LIBRARY")
const stage, depot, cases, library = abspath.(ARGS)
const repo = normpath(joinpath(@__DIR__, "..", "..", "..", ".."))
if !isolated
    for path in (stage, depot)
        startswith(relpath(path, repo), ".." * (Sys.iswindows() ? "\\" : "/")) ||
            error("Install paths must be outside the checkout: $path")
        ispath(path) && error("Refusing to reuse $path")
    end
    separator = Sys.iswindows() ? ";" : ":"
    cmd = `$(Base.julia_cmd()) --startup-file=no $(@__FILE__) --isolated $stage $depot $cases $library`
    run(addenv(cmd, "JULIA_DEPOT_PATH" => depot * separator, "JULIA_LOAD_PATH" => "@" * separator * "@stdlib"))
    exit()
end
first(DEPOT_PATH) == depot || error("Julia did not initialize the requested depot")
isfile(library) || error("Missing library $library")
isfile(joinpath(cases, "cases.tsv")) || error("Missing prepared cases in $cases")

using Pkg

mkpath(joinpath(stage, "src"))
mkpath(joinpath(stage, "artifacts"))
cp(joinpath(@__DIR__, "..", "Project.toml"), joinpath(stage, "Project.toml"))
cp(joinpath(@__DIR__, "..", "src", "Dapane.jl"), joinpath(stage, "src", "Dapane.jl"))
cp(library, joinpath(stage, "artifacts", basename(library)))

Pkg.activate(joinpath(depot, "env"); io = devnull)
Pkg.develop(path = stage; io = devnull)

using Dapane
using Test

@testset "installed artifact" begin
    resolved = Dapane.resolve_library()
    @test realpath(pathof(Dapane)) == realpath(joinpath(stage, "src", "Dapane.jl"))
    @test Base.active_project() == joinpath(depot, "env", "Project.toml")
    @test resolved == abspath(joinpath(stage, "artifacts", Dapane.expected_library_name()))
    @test basename(resolved) == basename(library)
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
