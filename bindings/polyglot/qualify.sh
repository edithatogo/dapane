#!/usr/bin/env bash
# Complete local acceptance command. Failures are never converted to skips.
set -euo pipefail

LANE_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$LANE_ROOT/../.." && pwd)"
if [[ $# != 1 ]]; then
    echo "Usage: bash bindings/polyglot/qualify.sh /absolute/new-output-directory" >&2
    exit 2
fi
TASK_OUTPUT="$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve())' "$1")"
case "$TASK_OUTPUT" in
    "$REPO_ROOT"|"$REPO_ROOT/"*) echo "Output must be outside the source checkout" >&2; exit 2 ;;
esac
test ! -e "$TASK_OUTPUT"
test -z "$(git -C "$REPO_ROOT" status --porcelain --untracked-files=all)"
mkdir -p "$TASK_OUTPUT"
exec > >(tee "$TASK_OUTPUT/qualification.log") 2>&1

cd "$REPO_ROOT"
git rev-parse HEAD > "$TASK_OUTPUT/source-sha.txt"
rustc --version
cargo --version
Rscript --vanilla -e 'print(R.version.string); print(R.version$platform)'
gcc --version
for manifest in "$LANE_ROOT/r/src/rust/Cargo.toml" "$LANE_ROOT/abi/Cargo.toml"; do
    cargo fetch --locked --manifest-path "$manifest"
    cargo fmt --manifest-path "$manifest" --all --check
    cargo clippy --offline --locked --manifest-path "$manifest" --all-targets \
        --target-dir "$TASK_OUTPUT/cargo-check" -- -D warnings
    cargo test --offline --locked --manifest-path "$manifest" \
        --target-dir "$TASK_OUTPUT/cargo-check"
done

python3 -m unittest discover -s "$LANE_ROOT/tests" -p 'test_*.py' -v
cargo build --locked --release -p dapane-cli --target-dir "$TASK_OUTPUT/cargo-core"
python3 "$LANE_ROOT/tests/prepare_cases.py" \
    --cli "$TASK_OUTPUT/cargo-core/release/dapane" --output "$TASK_OUTPUT/cases"
python3 "$LANE_ROOT/stage_r.py" --output "$TASK_OUTPUT/stage/dapaneR"
mkdir "$TASK_OUTPUT/r-library"
cd "$TASK_OUTPUT"
R CMD build --no-build-vignettes --no-manual "$TASK_OUTPUT/stage/dapaneR"
R CMD INSTALL --preclean --library="$TASK_OUTPUT/r-library" dapaneR_0.1.0.tar.gz
Rscript --vanilla "$LANE_ROOT/tests/installed.R" "$TASK_OUTPUT/r-library" "$TASK_OUTPUT/cases"

cargo build --offline --locked --release --manifest-path "$LANE_ROOT/abi/Cargo.toml" \
    --target-dir "$TASK_OUTPUT/cargo-abi"
gcc -std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined \
    -fno-omit-frame-pointer -I "$LANE_ROOT/abi/include" "$LANE_ROOT/tests/c_consumer.c" \
    -L "$TASK_OUTPUT/cargo-abi/release" "-Wl,-rpath,$TASK_OUTPUT/cargo-abi/release" \
    -ldapane_abi -pthread -o "$TASK_OUTPUT/c-consumer"
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 \
    "$TASK_OUTPUT/c-consumer" "$TASK_OUTPUT/cases"
nm -D --defined-only "$TASK_OUTPUT/cargo-abi/release/libdapane_abi.so" > "$TASK_OUTPUT/exports.txt"
sha256sum "$TASK_OUTPUT/dapaneR_0.1.0.tar.gz" \
    "$TASK_OUTPUT/r-library/dapaneR/libs/dapaneR.so" \
    "$TASK_OUTPUT/cargo-abi/release/libdapane_abi.so" \
    "$TASK_OUTPUT/c-consumer" > "$TASK_OUTPUT/artifacts.sha256"
git -C "$REPO_ROOT" diff --exit-code
echo "Local Linux acceptance completed. Hosted/security/release gates remain separate."
