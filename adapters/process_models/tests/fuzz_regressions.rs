//! Bounded mutation regression; ordinary process-model CI executes these tests.
#[path = "support/fuzz_contract.rs"]
mod contract;

const SEEDS: &[&[u8]] = &[
    b"",
    b"<root/>",
    b"<r a=\"&#x1F642;\">text &amp; more</r>",
    br#"{"integer":18446744073709551616,"unicode":"\uD83D\uDE42"}"#,
    include_bytes!("../fixtures/bpmn/sequential.bpmn"),
    include_bytes!("../fixtures/pnml/sequential-assay.pnml"),
    include_bytes!("../fixtures/pnml/sequential-assay.config.json"),
    include_bytes!("../fixtures/bpmn/sequential.config.json"),
];

#[test]
fn synthetic_seed_corpus_preserves_parser_invariants() {
    for seed in SEEDS {
        contract::check(seed);
    }
}

#[test]
fn truncation_bit_flip_and_token_mutations_preserve_parser_invariants() {
    let mut exercised = 0;
    for seed in SEEDS {
        let stride = (seed.len() / 64).max(1);
        for position in (0..=seed.len()).step_by(stride) {
            contract::check(&seed[..position]);
            exercised += 1;
            if position < seed.len() {
                for mask in [1_u8, 0x80, 0xff] {
                    let mut mutated = seed.to_vec();
                    mutated[position] ^= mask;
                    contract::check(&mutated);
                    exercised += 1;
                }
            }
        }
        for suffix in [b"\0".as_slice(), b"<", b"<!DOCTYPE x>", b"\xff", b"{}"] {
            let mut mutated = seed.to_vec();
            mutated.extend_from_slice(suffix);
            contract::check(&mutated);
            exercised += 1;
        }
    }
    assert!(
        exercised > 500,
        "mutation corpus must not be empty or silently skipped"
    );
}
