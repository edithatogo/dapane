//! Synthetic contract cases, independent of any native-format decoder.

use dapane_observed_contracts::*;
use std::collections::BTreeSet;

fn at(seconds: i64) -> Instant {
    Instant {
        unix_seconds: 1_767_225_600 + seconds,
        nanosecond: 0,
    }
}

fn link(object_id: &str, qualifier: &str) -> ObjectLink {
    ObjectLink {
        object_id: object_id.into(),
        qualifier: qualifier.into(),
    }
}

fn event(id: &str, seconds: i64, objects: &[(&str, &str)]) -> EventRef {
    EventRef {
        id: id.into(),
        at: Some(at(seconds)),
        objects: objects.iter().map(|(id, role)| link(id, role)).collect(),
    }
}

fn baseline() -> Snapshot {
    let objects = [
        ("infant-a", "infant"),
        ("infant-b", "infant"),
        ("specimen-a", "specimen"),
        ("specimen-b", "specimen"),
        ("assay-a", "assay"),
        ("assay-b", "assay"),
        ("batch-1", "batch"),
        ("instrument-1", "instrument"),
    ]
    .into_iter()
    .map(|(id, kind)| ObjectRef {
        id: id.into(),
        kind: kind.into(),
    })
    .collect();
    let run_objects = [
        ("batch-1", "batch"),
        ("specimen-a", "input"),
        ("specimen-b", "input"),
        ("assay-a", "assay"),
        ("assay-b", "assay"),
        ("instrument-1", "resource"),
    ];
    let events = vec![
        event(
            "collect-a",
            0,
            &[("infant-a", "subject"), ("specimen-a", "output")],
        ),
        event(
            "collect-b",
            60,
            &[("infant-b", "subject"), ("specimen-b", "output")],
        ),
        event("run-start", 120, &run_objects),
        event("run-complete", 1920, &run_objects),
    ];
    let relations = [
        ("specimen-a", "infant-a", "collected-from"),
        ("specimen-b", "infant-b", "collected-from"),
        ("batch-1", "specimen-a", "contains"),
        ("batch-1", "specimen-b", "contains"),
        ("specimen-a", "assay-a", "tested-by"),
        ("specimen-a", "assay-b", "tested-by"),
        ("specimen-b", "assay-a", "tested-by"),
        ("specimen-b", "assay-b", "tested-by"),
    ]
    .into_iter()
    .map(|(from, to, qualifier)| ObjectRelation {
        from: from.into(),
        to: to.into(),
        qualifier: qualifier.into(),
    })
    .collect();
    let mut uses: Vec<UseAssertion> = ["a", "b"]
        .into_iter()
        .map(|suffix| UseAssertion {
            id: format!("collection-{suffix}"),
            resource_id: "collection-kit".into(),
            unit: "kit".into(),
            kind: UseKind::Consumption,
            basis: Basis::Observed,
            quantity: Some(Quantity {
                numerator: "1".into(),
                denominator: "1".into(),
            }),
            extent: Extent::Point {
                event_id: format!("collect-{suffix}"),
            },
            object_ids: vec![format!("infant-{suffix}"), format!("specimen-{suffix}")],
            correction: Correction::Original,
        })
        .collect();
    uses.push(UseAssertion {
        id: "batch-use".into(),
        resource_id: "instrument-1".into(),
        unit: "hour".into(),
        kind: UseKind::Occupancy,
        basis: Basis::Observed,
        // Explicit source assertion, not a calculation from the timestamps.
        quantity: Some(Quantity {
            numerator: "1".into(),
            denominator: "2".into(),
        }),
        extent: Extent::Interval {
            start_event_id: Some("run-start".into()),
            end_event_id: Some("run-complete".into()),
            censoring: Censoring::None,
        },
        object_ids: [
            "infant-a",
            "infant-b",
            "specimen-a",
            "specimen-b",
            "assay-a",
            "assay-b",
            "batch-1",
        ]
        .into_iter()
        .map(String::from)
        .collect(),
        correction: Correction::Original,
    });
    Snapshot {
        source: SourceIdentity {
            namespace: "synthetic-x1".into(),
            revision: "fixture-v1".into(),
            format: SourceFormat::Ocel2Json,
            // Deliberate sentinel: this API checks syntax, not source bytes.
            content_digest: format!("sha256:{}", "0".repeat(64)),
        },
        window: ObservationWindow {
            start: at(0),
            end: at(3600),
        },
        objects,
        events,
        relations,
        uses,
    }
}

fn error(snapshot: Snapshot, expected: ErrorCode) {
    assert_eq!(validate_contract(snapshot).unwrap_err().code, expected);
}

fn readiness_error(snapshot: Snapshot, expected: ErrorCode) {
    let result = validate_contract(snapshot).unwrap();
    assert_eq!(result.require_costing_ready().unwrap_err().code, expected);
}

#[test]
fn shared_batch_is_one_use_for_two_specimens_and_two_assays() {
    let checked = validate_contract(baseline()).unwrap();
    let uses = checked.require_costing_ready().unwrap();
    assert_eq!(uses.len(), 3);
    assert_eq!(uses[0].id, "batch-use");
    assert_eq!(uses[0].quantity.as_ref().unwrap().numerator, "1");
    assert_eq!(uses[0].quantity.as_ref().unwrap().denominator, "2");
    assert_eq!(uses[0].object_ids.len(), 7);
    assert_eq!(checked.snapshot().objects.len(), 8);
    assert_eq!(checked.snapshot().relations.len(), 8);
    assert_eq!(checked.snapshot().events.len(), 4);
}

#[test]
fn arbitrary_set_order_changes_neither_normalized_contract_nor_use_identity() {
    let expected = validate_contract(baseline()).unwrap();
    for shift in 0..8 {
        let mut input = baseline();
        input.objects.rotate_left(shift);
        input.events.rotate_left(shift % 4);
        input.uses.rotate_left(shift % 3);
        input.relations.rotate_left(shift);
        for event in &mut input.events {
            event.objects.reverse();
        }
        for usage in &mut input.uses {
            usage.object_ids.reverse();
        }
        assert_eq!(validate_contract(input).unwrap(), expected);
    }
}

#[test]
fn all_event_permutations_have_identical_contracts() {
    let expected = validate_contract(baseline()).unwrap();
    let mut count = 0;
    for a in 0..4 {
        for b in 0..4 {
            for c in 0..4 {
                for d in 0..4 {
                    let ids = [a, b, c, d];
                    if ids.into_iter().collect::<BTreeSet<_>>().len() != 4 {
                        continue;
                    }
                    let mut input = baseline();
                    input.events = ids.map(|i| input.events[i].clone()).to_vec();
                    assert_eq!(validate_contract(input).unwrap(), expected);
                    count += 1;
                }
            }
        }
    }
    assert_eq!(count, 24);
}

#[test]
fn duplicate_event_identity_is_rejected_even_when_identical() {
    let mut input = baseline();
    input.events.push(input.events[0].clone());
    error(input, ErrorCode::DuplicateIdentity);
}

#[test]
fn conflicting_duplicate_event_is_not_resolved_by_last_write() {
    let mut input = baseline();
    let mut duplicate = input.events[0].clone();
    duplicate.at = Some(at(500));
    input.events.push(duplicate);
    error(input, ErrorCode::DuplicateIdentity);
}

#[test]
fn trace_duplication_cannot_repeat_an_underlying_use() {
    let mut input = baseline();
    input.uses.push(input.uses[2].clone());
    error(input, ErrorCode::DuplicateIdentity);
}

#[test]
fn duplicate_object_is_rejected() {
    let mut input = baseline();
    input.objects.push(input.objects[0].clone());
    error(input, ErrorCode::DuplicateIdentity);
}

#[test]
fn missing_time_does_not_acquire_current_or_zero_time() {
    let mut input = baseline();
    input.events[0].at = None;
    error(input, ErrorCode::MissingTimestamp);
}

#[test]
fn dangling_event_anchor_is_rejected() {
    let mut input = baseline();
    input.events.pop();
    error(input, ErrorCode::UnknownReference);
}

#[test]
fn dangling_event_and_use_object_edges_are_rejected() {
    let mut input = baseline();
    input.events[0].objects[0].object_id = "absent".into();
    error(input, ErrorCode::UnknownReference);
    let mut input = baseline();
    input.uses[0].object_ids.push("absent".into());
    error(input, ErrorCode::UnknownReference);
}

#[test]
fn dangling_object_relation_is_rejected() {
    let mut input = baseline();
    input.relations[0].to = "absent".into();
    error(input, ErrorCode::UnknownReference);
}

#[test]
fn qualified_parallel_edges_survive_including_empty_qualifier() {
    let mut input = baseline();
    input.events[0].objects.push(link("specimen-a", ""));
    input.events[0].objects.push(link("specimen-a", "input"));
    let checked = validate_contract(input).unwrap();
    let links = &checked.snapshot().events[0].objects;
    assert_eq!(links.len(), 4);
    assert!(links.contains(&link("specimen-a", "")));
    assert!(links.contains(&link("specimen-a", "input")));
    assert!(links.contains(&link("specimen-a", "output")));
    assert_eq!(checked.require_costing_ready().unwrap().len(), 3);
}

#[test]
fn repeated_qualified_edges_fail_instead_of_disappearing() {
    let mut input = baseline();
    let duplicate = input.events[0].objects[0].clone();
    input.events[0].objects.push(duplicate);
    error(input, ErrorCode::DuplicateRelationship);
    let mut input = baseline();
    input.relations.push(input.relations[0].clone());
    error(input, ErrorCode::DuplicateRelationship);
    let mut input = baseline();
    input.uses[0].object_ids.push("infant-a".into());
    error(input, ErrorCode::DuplicateRelationship);
}

#[test]
fn all_four_censoring_shapes_are_explicit_and_only_complete_is_ready() {
    for (start, end, censoring) in [
        (Some("run-start"), Some("run-complete"), Censoring::None),
        (None, Some("run-complete"), Censoring::Left),
        (Some("run-start"), None, Censoring::Right),
        (None, None, Censoring::Both),
    ] {
        let mut input = baseline();
        input.uses[2].extent = Extent::Interval {
            start_event_id: start.map(String::from),
            end_event_id: end.map(String::from),
            censoring,
        };
        let checked = validate_contract(input).unwrap();
        if censoring == Censoring::None {
            assert_eq!(checked.require_costing_ready().unwrap().len(), 3);
        } else {
            assert_eq!(
                checked.require_costing_ready().unwrap_err().code,
                ErrorCode::CensoredUse
            );
        }
    }
}

#[test]
fn censored_endpoint_is_never_filled_from_observation_cutoff() {
    let mut input = baseline();
    input.uses[2].extent = Extent::Interval {
        start_event_id: Some("run-start".into()),
        end_event_id: None,
        censoring: Censoring::Right,
    };
    let checked = validate_contract(input).unwrap();
    assert!(matches!(
        checked.snapshot().uses[0].extent,
        Extent::Interval {
            end_event_id: None,
            ..
        }
    ));
    assert_eq!(
        checked.require_costing_ready().unwrap_err().code,
        ErrorCode::CensoredUse
    );
}

#[test]
fn incomplete_interval_cannot_be_marked_complete() {
    let mut input = baseline();
    input.uses[2].extent = Extent::Interval {
        start_event_id: Some("run-start".into()),
        end_event_id: None,
        censoring: Censoring::None,
    };
    error(input, ErrorCode::CensoringMismatch);
}

#[test]
fn completed_interval_cannot_claim_censoring() {
    let mut input = baseline();
    input.uses[2].extent = Extent::Interval {
        start_event_id: Some("run-start".into()),
        end_event_id: Some("run-complete".into()),
        censoring: Censoring::Right,
    };
    error(input, ErrorCode::CensoringMismatch);
}

#[test]
fn zero_and_missing_quantity_are_different() {
    let mut input = baseline();
    input.uses[0].quantity.as_mut().unwrap().numerator = "0".into();
    let checked = validate_contract(input).unwrap();
    assert_eq!(checked.require_costing_ready().unwrap().len(), 3);
    let mut input = baseline();
    input.uses[0].quantity = None;
    readiness_error(input, ErrorCode::MissingQuantity);
}

#[test]
fn duration_does_not_supply_or_change_recorded_quantity() {
    let mut input = baseline();
    input.events[3].at = Some(at(3500));
    let checked = validate_contract(input.clone()).unwrap();
    assert_eq!(checked.snapshot().uses[0].quantity, input.uses[2].quantity);
    input.uses[2].quantity = None;
    readiness_error(input, ErrorCode::MissingQuantity);
}

#[test]
fn transfer_is_retained_but_blocks_costing_selection_atomically() {
    let mut input = baseline();
    input.uses[1].kind = UseKind::Transfer;
    let checked = validate_contract(input).unwrap();
    assert_eq!(checked.snapshot().uses.len(), 3);
    assert_eq!(
        checked.require_costing_ready().unwrap_err().code,
        ErrorCode::TransferNotCostable
    );
}

#[test]
fn assumed_and_simulated_quantities_are_never_promoted_to_observed() {
    for basis in [Basis::Assumed, Basis::Simulated] {
        let mut input = baseline();
        input.uses[0].basis = basis;
        let checked = validate_contract(input).unwrap();
        assert_eq!(checked.snapshot().uses[1].basis, basis);
        assert_eq!(
            checked.require_costing_ready().unwrap_err().code,
            ErrorCode::NonObservedUse
        );
    }
}

#[test]
fn replacement_and_retraction_fail_before_any_readiness_result() {
    for correction in [
        Correction::Replace {
            use_id: "prior".into(),
        },
        Correction::Retract {
            use_id: "prior".into(),
        },
    ] {
        let mut input = baseline();
        input.uses[0].correction = correction;
        error(input, ErrorCode::UnsupportedCorrection);
    }
}

#[test]
fn negative_exponent_float_and_nonfinite_quantities_fail() {
    for value in ["-1", "+1", "1e2", "NaN", "Infinity", "0.5", "", " 1", "１"] {
        let mut input = baseline();
        input.uses[0].quantity.as_mut().unwrap().numerator = value.into();
        error(input, ErrorCode::InvalidQuantity);
    }
}

#[test]
fn denominator_must_be_positive_and_quantity_digits_are_bounded() {
    for value in ["0", "000", "-1", "1.0", ""] {
        let mut input = baseline();
        input.uses[0].quantity.as_mut().unwrap().denominator = value.into();
        error(input, ErrorCode::InvalidQuantity);
    }
    let mut input = baseline();
    input.uses[0].quantity.as_mut().unwrap().numerator = "9".repeat(96);
    assert!(validate_contract(input.clone()).is_ok());
    input.uses[0].quantity.as_mut().unwrap().numerator.push('9');
    error(input, ErrorCode::InvalidQuantity);
}

#[test]
fn exact_quantity_spelling_is_preserved_without_reduction() {
    let mut input = baseline();
    input.uses[2].quantity = Some(Quantity {
        numerator: "02".into(),
        denominator: "04".into(),
    });
    let checked = validate_contract(input).unwrap();
    assert_eq!(
        checked.snapshot().uses[0]
            .quantity
            .as_ref()
            .unwrap()
            .numerator,
        "02"
    );
    assert_eq!(
        checked.snapshot().uses[0]
            .quantity
            .as_ref()
            .unwrap()
            .denominator,
        "04"
    );
}

#[test]
fn reversed_or_zero_length_occupancy_is_rejected() {
    for end in [0, 120] {
        let mut input = baseline();
        input.events[3].at = Some(at(end));
        error(input, ErrorCode::InvalidInterval);
    }
}

#[test]
fn simultaneous_distinct_events_are_preserved_without_causal_order() {
    let mut input = baseline();
    input.events[1].at = input.events[0].at;
    let checked = validate_contract(input).unwrap();
    assert_eq!(checked.snapshot().events.len(), 4);
    assert_eq!(checked.require_costing_ready().unwrap().len(), 3);
}

#[test]
fn occupancy_needs_explicit_pairing_instead_of_a_single_event() {
    let mut input = baseline();
    input.uses[0].kind = UseKind::Occupancy;
    error(input, ErrorCode::OccupancyNeedsInterval);
}

#[test]
fn interval_end_at_cutoff_is_an_observed_anchor() {
    let mut input = baseline();
    input.events[3].at = Some(input.window.end);
    assert!(
        validate_contract(input)
            .unwrap()
            .require_costing_ready()
            .is_ok()
    );
}

#[test]
fn out_of_window_anchors_and_empty_windows_fail() {
    for offset in [-1, 3601] {
        let mut input = baseline();
        input.events[0].at = Some(at(offset));
        error(input, ErrorCode::OutsideWindow);
    }
    let mut input = baseline();
    input.window.end = input.window.start;
    error(input, ErrorCode::InvalidInterval);
}

#[test]
fn invalid_fraction_and_out_of_range_instants_fail() {
    for invalid in [
        Instant {
            unix_seconds: 0,
            nanosecond: 1_000_000_000,
        },
        Instant {
            unix_seconds: i64::MAX,
            nanosecond: 0,
        },
        Instant {
            unix_seconds: -62_135_596_801,
            nanosecond: 0,
        },
    ] {
        let mut input = baseline();
        input.events[0].at = Some(invalid);
        error(input, ErrorCode::InvalidInstant);
    }
}

#[test]
fn tokens_are_bounded_and_errors_do_not_echo_values() {
    for bad in ["", "  private-name", "private-name\n", &"x".repeat(129)] {
        let mut input = baseline();
        input.objects[0].id = bad.into();
        let result = validate_contract(input).unwrap_err();
        assert_eq!(result.code, ErrorCode::InvalidToken);
        assert!(!result.to_string().contains("private-name"));
    }
}

#[test]
fn unicode_identity_is_preserved_without_case_folding() {
    let mut input = baseline();
    input.source.namespace = "synthetic-δ".into();
    input.objects.push(ObjectRef {
        id: "Infant-a".into(),
        kind: "infant".into(),
    });
    let checked = validate_contract(input).unwrap();
    assert_eq!(checked.snapshot().objects.len(), 9);
    assert_eq!(checked.snapshot().source.namespace, "synthetic-δ");
}

#[test]
fn invalid_digest_spelling_is_rejected_without_claiming_verification() {
    for value in ["none".to_owned(), format!("sha256:{}", "A".repeat(64))] {
        let mut input = baseline();
        input.source.content_digest = value;
        error(input, ErrorCode::InvalidDigest);
    }
}

#[test]
fn record_and_nested_reference_bounds_fail_before_mapping() {
    let mut input = baseline();
    input.objects = vec![input.objects[0].clone(); MAX_COLLECTION + 1];
    error(input, ErrorCode::LimitExceeded);
    let mut input = baseline();
    input.events[0].objects = vec![input.events[0].objects[0].clone(); MAX_COLLECTION + 1];
    error(input, ErrorCode::LimitExceeded);
    let mut input = baseline();
    for event in &mut input.events {
        event.objects = vec![event.objects[0].clone(); 6000];
    }
    error(input, ErrorCode::LimitExceeded);
}

#[test]
fn a_contract_with_no_uses_cannot_claim_costing_readiness() {
    let mut input = baseline();
    input.uses.clear();
    readiness_error(input, ErrorCode::NoUses);
}

#[test]
fn native_format_tag_never_enables_a_decoder() {
    assert_eq!(RAW_IMPORT_STATUS, "blocked_dependency_qualification");
    let mut input = baseline();
    input.source.format = SourceFormat::Xes;
    assert!(validate_contract(input).is_ok());
}
