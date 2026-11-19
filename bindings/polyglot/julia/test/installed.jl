# Install a staged copy of the package, with the host library beside it, and
# compare every prepared case to the CLI bytes. This file is not part of Pkg.test.

using Pkg

length(ARGS) == 4 || error("Usage: installed.jl STAGE DEPOT CASES LIBRARY")
const stage, depot, cases, library = abspath.(ARGS)
const repo = normpath(joinpath(@__DIR__, "..", "..", "..", ".."))
for path in (stage, depot)
    startswith(path, repo * "/") && error("Install paths must be outside the checkout: $path")
    ispath(path) && error("Refusing to reuse $path")
end
isfile(library) || error("Missing library $library")
isfile(joinpath(cases, "cases.tsv")) || error("Missing prepared cases in $cases")

mkpath(joinpath(stage, "src"))
mkpath(joinpath(stage, "artifacts"))
cp(joinpath(@__DIR__, "..", "Project.toml"), joinpath(stage, "Project.toml"))
cp(joinpath(@__DIR__, "..", "src", "Dapane.jl"), joinpath(stage, "src", "Dapane.jl"))
cp(library, joinpath(stage, "artifacts", basename(library)))

ENV["JULIA_DEPOT_PATH"] = depot
Pkg.activate(joinpath(depot, "env"); io = devnull)
Pkg.develop(path = stage; io = devnull)

using Dapane
using Test

@testset "installed artifact" begin
    resolved = Dapane.resolve_library()
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
