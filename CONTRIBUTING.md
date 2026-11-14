# Contributing to dapane

Dapane provides an independent Rust microcosting and valuation core, a CLI and thin language bindings. Contributions should improve explicit resource-use contracts, numerical behaviour, synthetic reference cases or their documentation.

## Before you start

Start with [AGENTS.md](AGENTS.md), [the Conductor index](conductor/index.md), the existing track and [implemented contract](docs/contract-v0.1.md). For incomplete instrument capacity, also read [contract 0.2](docs/contract-v0.2.md). Keep arithmetic in Rust and specialist provider rules outside the minimal core. Preserve full-allocation compatibility and explicit unknown or unallocated capacity.

For bugs, provide the affected version or commit, environment, minimal reproduction, expected result and observed result. For a substantial proposal, describe the use case and compatibility impact in an issue before expanding implementation scope. Use existing issue templates when offered.

## Development and validation

Follow the pinned [Rust toolchain](rust-toolchain.toml), [quickstart](docs/quickstart.md) and [Runtime workflow](.github/workflows/runtime.yml). The established native checks include:

```sh
cargo fmt --all --check
cargo clippy --workspace --locked --all-targets -- -D warnings
cargo test --locked
cargo build --locked --release -p dapane-cli
python3 scripts/validate_conductor.py
```

For public-contract changes, install the documented development requirements and run `python scripts/validate_contract.py --cli target/release/dapane`. For Python changes, follow the quickstart's native-wheel build, installation and tests outside the source checkout; an import from the working tree is insufficient evidence.

Use independently calculated synthetic expectations, including invalid inputs and allocation conservation. Distinguish computational verification from empirical validation. Version incompatible contract semantics deliberately and update migration guidance.

## Pull requests

Create a focused branch from the current `main` branch and submit a pull request to this repository. Link the relevant issue or existing Conductor task, explain the resulting behaviour, and update affected examples, contracts and documentation. Keep unrelated changes in separate pull requests.

Report executed commands, outcomes and the commit they validate. Identify unavailable checks and remaining limitations explicitly. Follow the repository's existing review and automated-check requirements; retain required gates and current ownership. Address findings and verify the final head before integration. Repository changes do not themselves authorise a release or external operational action.

## Security, rights and conduct

Follow the [security policy](https://github.com/edithatogo/.github/blob/main/SECURITY.md). Use private vulnerability reporting if available; otherwise request a private contact without publishing vulnerability details. Keep credentials, personal information and restricted source material out of issues, fixtures, logs and artifacts.

Preserve existing attribution and third-party terms. This guide does not grant a licence; clarify any unclear redistribution rights before contributing external material. Follow the [code of conduct](https://github.com/edithatogo/.github/blob/main/CODE_OF_CONDUCT.md) and keep technical discussions respectful.

## Basis for this guide

This guide follows [GitHub's contribution-guideline guidance](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors) and the contribution-process and testing principles in [OpenSSF Best Practices](https://www.bestpractices.dev/en/criteria). It does not assert certification.
