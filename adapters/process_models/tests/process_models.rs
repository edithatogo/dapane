//! Integration tests for X2 bounded PNML/Petri-net and BPMN 2.0 adapters.

use std::fs;
use std::path::PathBuf;

use dapane_process_models::bpmn::{BpmnProfile, execute_bpmn, parse_bpmn_bytes, parse_bpmn_config};
use dapane_process_models::json_io::{JsonValue, parse_json_bytes};
use dapane_process_models::model::{
    ErrorCode, ExactQty, ExecutionStatus, ExecutionTrace, ResourceKind, ValuationAttachment,
    project_to_dapane_request, validate_date, validate_token,
};
use dapane_process_models::pnml::{execute_petri_net, parse_pnml_bytes, parse_pnml_config};
use dapane_process_models::sha256::prefixed_sha256;
use dapane_process_models::xml::{MAX_XML_BYTES, parse_xml_bytes};

fn fixture_path(rel: &str) -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("fixtures")
        .join(rel)
}

fn fixture_bytes(rel: &str) -> Vec<u8> {
    fs::read(fixture_path(rel)).expect("read fixture bytes")
}

#[test]
fn xml_blocks_doctype_declarations() {
    let err = parse_xml_bytes(b"<!DOCTYPE x><pnml/>").unwrap_err();
    assert_eq!(err.code, ErrorCode::DisallowedXmlConstruct);
}

#[test]
fn xml_blocks_entity_notation_cdata_pi_and_unknown_entities() {
    let cases = [
        b"<!ENTITY e \"1\"><pnml/>".as_slice(),
        b"<!NOTATION n SYSTEM \"x\"><pnml/>".as_slice(),
        b"<pnml><![CDATA[x]]></pnml>".as_slice(),
        b"<?stylesheet href=\"x\"?><pnml/>".as_slice(),
        b"<pnml>&unknown;</pnml>".as_slice(),
    ];
    for raw in cases {
        assert_eq!(
            parse_xml_bytes(raw).unwrap_err().code,
            ErrorCode::DisallowedXmlConstruct
        );
    }
}

#[test]
fn xml_enforces_byte_and_depth_bounds() {
    let big = vec![b' '; MAX_XML_BYTES + 1];
    assert_eq!(
        parse_xml_bytes(&big).unwrap_err().code,
        ErrorCode::SizeLimitExceeded
    );

    let deep = format!("{}<x/>{}", "<a>".repeat(33), "</a>".repeat(33));
    assert_eq!(
        parse_xml_bytes(deep.as_bytes()).unwrap_err().code,
        ErrorCode::SizeLimitExceeded
    );
}

#[test]
fn xml_rejects_malformed_attributes_mismatched_tags_and_trailing_roots() {
    for raw in [
        b"<a id=\"1\" id=\"2\"/>".as_slice(),
        b"<a></b>".as_slice(),
        b"<p:a/>".as_slice(),
        b"<a/><b/>".as_slice(),
        b"\xff\xfe".as_slice(),
    ] {
        assert_eq!(
            parse_xml_bytes(raw).unwrap_err().code,
            ErrorCode::MalformedXml
        );
    }
}

#[test]
fn json_rejects_duplicate_keys_nonfinite_and_trailing_content() {
    for raw in [
        br#"{"a":1,"a":2}"#.as_slice(),
        br#"{"a":NaN}"#.as_slice(),
        br#"{"a":Infinity}"#.as_slice(),
        br#"{"a":1} trailing"#.as_slice(),
    ] {
        assert_eq!(
            parse_json_bytes(raw).unwrap_err().code,
            ErrorCode::MalformedJson
        );
    }
}

#[test]
fn exact_qty_supports_decimal_and_rational_arithmetic() {
    let third = ExactQty::parse("1/3", "/q").unwrap();
    let two_thirds = ExactQty::parse("2/3", "/q").unwrap();
    let one = third.checked_add(two_thirds, "/q").unwrap();
    assert_eq!(one, ExactQty::from_u64(1));
    assert_eq!(one.to_dapane_json(), JsonValue::String("1".to_owned()));
    assert!(matches!(third.to_dapane_json(), JsonValue::Object(_)));

    let half = ExactQty::parse("0.50", "/q").unwrap();
    let five = ExactQty::parse("5", "/q").unwrap();
    assert_eq!(
        half.checked_mul(five, "/q").unwrap().to_dapane_json(),
        JsonValue::String("2.5".to_owned())
    );
}

#[test]
fn exact_qty_rejects_zero_denominator_and_u128_overflow() {
    assert_eq!(
        ExactQty::new(1, 0, "/q").unwrap_err().code,
        ErrorCode::InvalidQuantity
    );
    let huge = ExactQty {
        numerator: u128::MAX,
        denominator: 1,
    };
    assert_eq!(
        huge.checked_add(ExactQty::from_u64(1), "/q")
            .unwrap_err()
            .code,
        ErrorCode::ArithmeticOverflow
    );
}

#[test]
fn tokens_and_calendar_dates_enforce_dapane_bounds() {
    assert!(validate_token("valid_token-1", "/t").is_ok());
    assert_eq!(
        validate_token(" leading", "/t").unwrap_err().code,
        ErrorCode::InvalidToken
    );
    assert_eq!(
        validate_token(&"x".repeat(129), "/t").unwrap_err().code,
        ErrorCode::InvalidToken
    );
    assert!(validate_date("2024-02-29", "/d").is_ok());
    assert_eq!(
        validate_date("2025-02-29", "/d").unwrap_err().code,
        ErrorCode::MalformedJson
    );
}

#[test]
fn pnml_sequential_assay_scales_multiplicity_and_preserves_batch() {
    let xml = fixture_bytes("pnml/sequential-assay.pnml");
    let net = parse_pnml_bytes(&xml).unwrap();
    let cfg = parse_pnml_config(&fixture_bytes("pnml/sequential-assay.config.json")).unwrap();
    let trace = execute_petri_net(&net, &cfg).unwrap();

    assert_eq!(trace.status, ExecutionStatus::Completed);
    assert_eq!(trace.model_sha256, prefixed_sha256(&xml));
    assert_eq!(trace.total_elapsed_minutes, ExactQty::from_u64(8));
    assert_eq!(trace.steps.len(), 2);
    assert_eq!(trace.steps[0].multiplicity, 2);
    assert_eq!(trace.usages[0].quantity, ExactQty::from_u64(9));
    assert_eq!(trace.usages[1].quantity, ExactQty::from_u64(1));
    assert_eq!(trace.usages[1].attribution_object_id, None);
    let final_m = trace.final_marking.as_ref().unwrap();
    assert_eq!(final_m["p_ready"], 0);
    assert_eq!(final_m["p_collected"], 0);
    assert_eq!(final_m["p_assayed"], 1);
}

#[test]
fn pnml_shared_batch_omits_transfer_from_dapane_request() {
    let net = parse_pnml_bytes(&fixture_bytes("pnml/shared-batch-parallel.pnml")).unwrap();
    let cfg = parse_pnml_config(&fixture_bytes("pnml/shared-batch-parallel.config.json")).unwrap();
    let trace = execute_petri_net(&net, &cfg).unwrap();

    assert_eq!(
        trace.total_elapsed_minutes,
        ExactQty::new(29, 2, "/t").unwrap()
    );
    assert_eq!(trace.usages.len(), 3);
    assert_eq!(trace.usages[0].resource_kind, ResourceKind::Transfer);
    assert!(!trace.usages[0].costable);
    assert_eq!(trace.usages[1].resource_kind, ResourceKind::Occupancy);
    assert!(trace.usages[1].costable);

    let val = ValuationAttachment::from_json(
        &parse_json_bytes(&fixture_bytes("quotes-release-2026-v1.json")).unwrap(),
    )
    .unwrap();
    let req = project_to_dapane_request(&trace, &val).unwrap();
    let projected = req.as_object("/").unwrap()["usage"]
        .as_array("/usage")
        .unwrap();
    assert_eq!(projected.len(), 2);
}

#[test]
fn pnml_cancelled_rework_skips_unexecuted_downstream_steps() {
    let net = parse_pnml_bytes(&fixture_bytes("pnml/cancelled-rework.pnml")).unwrap();
    let cfg = parse_pnml_config(&fixture_bytes("pnml/cancelled-rework.config.json")).unwrap();
    let trace = execute_petri_net(&net, &cfg).unwrap();

    assert!(matches!(
        trace.status,
        ExecutionStatus::Cancelled {
            ref cancelled_at_node,
            ..
        } if cancelled_at_node == "t_repeat"
    ));
    assert_eq!(trace.steps.len(), 2);
    assert_eq!(trace.usages.len(), 2);
    assert_eq!(
        trace.total_elapsed_minutes,
        ExactQty::new(11, 2, "/t").unwrap()
    );
}

#[test]
fn pnml_rejects_inhibitor_arc_highlevel_net_and_doctype() {
    assert_eq!(
        parse_pnml_bytes(&fixture_bytes("pnml/invalid-inhibitor-arc.pnml"))
            .unwrap_err()
            .code,
        ErrorCode::UnsupportedConstruct
    );
    assert_eq!(
        parse_pnml_bytes(&fixture_bytes("pnml/invalid-net-type.pnml"))
            .unwrap_err()
            .code,
        ErrorCode::UnsupportedNetType
    );
    assert_eq!(
        parse_pnml_bytes(&fixture_bytes("pnml/invalid-doctype.pnml"))
            .unwrap_err()
            .code,
        ErrorCode::DisallowedXmlConstruct
    );
}

#[test]
fn pnml_rejects_unenabled_transition_and_mismatched_final_marking() {
    let net = parse_pnml_bytes(&fixture_bytes("pnml/sequential-assay.pnml")).unwrap();
    let mut cfg = parse_pnml_config(&fixture_bytes("pnml/sequential-assay.config.json")).unwrap();
    cfg.schedule[0].transition_id = "t_report".to_owned();
    assert_eq!(
        execute_petri_net(&net, &cfg).unwrap_err().code,
        ErrorCode::NotEnabled
    );

    let mut cfg_final =
        parse_pnml_config(&fixture_bytes("pnml/sequential-assay.config.json")).unwrap();
    cfg_final
        .expected_final_marking
        .as_mut()
        .unwrap()
        .insert("p_ready".to_owned(), 1);
    assert_eq!(
        execute_petri_net(&net, &cfg_final).unwrap_err().code,
        ErrorCode::FinalMarkingMismatch
    );
}

#[test]
fn pnml_rejects_zero_multiplicity_and_step_limit() {
    let zero_json = String::from_utf8(fixture_bytes("pnml/sequential-assay.config.json"))
        .unwrap()
        .replace("\"multiplicity\": 2", "\"multiplicity\": 0");
    assert_eq!(
        parse_pnml_config(zero_json.as_bytes()).unwrap_err().code,
        ErrorCode::InvalidWeight
    );

    let net = parse_pnml_bytes(&fixture_bytes("pnml/sequential-assay.pnml")).unwrap();
    let mut cfg = parse_pnml_config(&fixture_bytes("pnml/sequential-assay.config.json")).unwrap();
    cfg.max_steps = 1;
    assert_eq!(
        execute_petri_net(&net, &cfg).unwrap_err().code,
        ErrorCode::StepLimitExceeded
    );
}

#[test]
fn pnml_rejects_toolspecific_place_to_place_zero_weight_and_duplicate_id() {
    let tool_xml = br#"<pnml xmlns="http://www.pnml.org/version-2009/grammar/pnml">
      <net id="n" type="http://www.pnml.org/version-2009/grammar/ptnet">
        <page id="p"><place id="p0"/><transition id="t0"><toolspecific tool="x" version="1"/></transition></page>
      </net></pnml>"#;
    assert_eq!(
        parse_pnml_bytes(tool_xml).unwrap_err().code,
        ErrorCode::UnsupportedConstruct
    );

    let p2p_xml = br#"<pnml xmlns="http://www.pnml.org/version-2009/grammar/pnml">
      <net id="n" type="http://www.pnml.org/version-2009/grammar/ptnet">
        <page id="p"><place id="p0"/><place id="p1"/><transition id="t0"/>
        <arc id="a" source="p0" target="p1"/></page>
      </net></pnml>"#;
    assert_eq!(
        parse_pnml_bytes(p2p_xml).unwrap_err().code,
        ErrorCode::UnsupportedConstruct
    );

    let zero_arc = br#"<pnml xmlns="http://www.pnml.org/version-2009/grammar/pnml">
      <net id="n" type="http://www.pnml.org/version-2009/grammar/ptnet">
        <page id="p"><place id="p0"/><transition id="t0"/>
        <arc id="a" source="p0" target="t0"><inscription><text>0</text></inscription></arc></page>
      </net></pnml>"#;
    assert_eq!(
        parse_pnml_bytes(zero_arc).unwrap_err().code,
        ErrorCode::InvalidWeight
    );

    let dup_id = br#"<pnml xmlns="http://www.pnml.org/version-2009/grammar/pnml">
      <net id="n" type="http://www.pnml.org/version-2009/grammar/ptnet">
        <page id="p"><place id="dup"/><transition id="dup"/></page>
      </net></pnml>"#;
    assert_eq!(
        parse_pnml_bytes(dup_id).unwrap_err().code,
        ErrorCode::DuplicateIdentity
    );
}

#[test]
fn pnml_rejects_dangling_arc_and_unknown_transition_in_schedule() {
    let dangling = br#"<pnml xmlns="http://www.pnml.org/version-2009/grammar/pnml">
      <net id="n" type="http://www.pnml.org/version-2009/grammar/ptnet">
        <page id="p"><place id="p0"/><transition id="t0"/>
        <arc id="a" source="p_missing" target="t0"/></page>
      </net></pnml>"#;
    assert_eq!(
        parse_pnml_bytes(dangling).unwrap_err().code,
        ErrorCode::DanglingReference
    );

    let net = parse_pnml_bytes(&fixture_bytes("pnml/sequential-assay.pnml")).unwrap();
    let mut cfg = parse_pnml_config(&fixture_bytes("pnml/sequential-assay.config.json")).unwrap();
    cfg.schedule[0].transition_id = "t_nonexistent".to_owned();
    assert_eq!(
        execute_petri_net(&net, &cfg).unwrap_err().code,
        ErrorCode::DanglingReference
    );
}

#[test]
fn bpmn_sequential_executes_in_core_profile() {
    let model = parse_bpmn_bytes(
        &fixture_bytes("bpmn/sequential.bpmn"),
        BpmnProfile::CoreAcyclic,
    )
    .unwrap();
    let cfg = parse_bpmn_config(&fixture_bytes("bpmn/sequential.config.json")).unwrap();
    let trace = execute_bpmn(&model, &cfg).unwrap();
    assert_eq!(trace.total_elapsed_minutes, ExactQty::from_u64(10));
    assert_eq!(trace.steps.len(), 2);
    assert_eq!(trace.usages.len(), 3);
}

#[test]
fn bpmn_xor_routing_selects_only_chosen_branch() {
    let model = parse_bpmn_bytes(
        &fixture_bytes("bpmn/alternative-xor.bpmn"),
        BpmnProfile::CoreAcyclic,
    )
    .unwrap();
    let routine = execute_bpmn(
        &model,
        &parse_bpmn_config(&fixture_bytes("bpmn/alternative-xor-routine.config.json")).unwrap(),
    )
    .unwrap();
    let confirm = execute_bpmn(
        &model,
        &parse_bpmn_config(&fixture_bytes("bpmn/alternative-xor-confirm.config.json")).unwrap(),
    )
    .unwrap();

    assert_eq!(routine.total_elapsed_minutes, ExactQty::from_u64(8));
    assert_eq!(routine.steps[1].activity_id, "routine_report");
    assert_eq!(confirm.total_elapsed_minutes, ExactQty::from_u64(23));
    assert_eq!(confirm.steps[1].activity_id, "confirmatory_workup");
}

#[test]
fn bpmn_parallel_join_computes_makespan_and_avoids_batch_duplication() {
    let model = parse_bpmn_bytes(
        &fixture_bytes("bpmn/concurrent-and-shared.bpmn"),
        BpmnProfile::CoreAcyclic,
    )
    .unwrap();
    let cfg = parse_bpmn_config(&fixture_bytes("bpmn/concurrent-and-shared.config.json")).unwrap();
    let trace = execute_bpmn(&model, &cfg).unwrap();

    assert_eq!(trace.total_elapsed_minutes, ExactQty::from_u64(30));
    assert_eq!(trace.steps.len(), 3);
    assert_eq!(trace.usages.len(), 4);
    assert_eq!(trace.usages[1].resource_kind, ResourceKind::Transfer);
    assert!(!trace.usages[1].costable);
    assert_eq!(trace.usages[2].target, "analyzer_time");
    assert_eq!(trace.usages[2].quantity, ExactQty::from_u64(25));
    assert_eq!(trace.usages[2].attribution_object_id, None);
}

#[test]
fn bpmn_core_profile_rejects_cycles_subprocesses_and_terminate_events() {
    assert_eq!(
        parse_bpmn_bytes(
            &fixture_bytes("bpmn/rework-loop.bpmn"),
            BpmnProfile::CoreAcyclic
        )
        .unwrap_err()
        .code,
        ErrorCode::CycleNotAllowedInCoreProfile
    );
    assert_eq!(
        parse_bpmn_bytes(
            &fixture_bytes("bpmn/embedded-subprocess.bpmn"),
            BpmnProfile::CoreAcyclic,
        )
        .unwrap_err()
        .code,
        ErrorCode::UnsupportedConstruct
    );
    assert_eq!(
        parse_bpmn_bytes(
            &fixture_bytes("bpmn/cancelled-terminate.bpmn"),
            BpmnProfile::CoreAcyclic,
        )
        .unwrap_err()
        .code,
        ErrorCode::UnsupportedConstruct
    );
}

#[test]
fn bpmn_extended_executes_rework_loop_with_distinct_visit_identities() {
    let model = parse_bpmn_bytes(
        &fixture_bytes("bpmn/rework-loop.bpmn"),
        BpmnProfile::ExtendedReworkSubprocess,
    )
    .unwrap();
    let cfg = parse_bpmn_config(&fixture_bytes("bpmn/rework-loop.config.json")).unwrap();
    let trace = execute_bpmn(&model, &cfg).unwrap();

    assert_eq!(trace.total_elapsed_minutes, ExactQty::from_u64(16));
    assert_eq!(trace.steps.len(), 3);
    assert_eq!(trace.steps[0].visit, 1);
    assert_eq!(trace.steps[2].visit, 2);
    assert_ne!(trace.usages[0].use_id, trace.usages[2].use_id);
}

#[test]
fn bpmn_extended_executes_embedded_subprocess_with_scoped_paths() {
    let model = parse_bpmn_bytes(
        &fixture_bytes("bpmn/embedded-subprocess.bpmn"),
        BpmnProfile::ExtendedReworkSubprocess,
    )
    .unwrap();
    let cfg = parse_bpmn_config(&fixture_bytes("bpmn/embedded-subprocess.config.json")).unwrap();
    let trace = execute_bpmn(&model, &cfg).unwrap();

    assert_eq!(trace.total_elapsed_minutes, ExactQty::from_u64(15));
    assert_eq!(trace.steps[0].subprocess_path, vec!["sub_dna".to_owned()]);
    assert_eq!(trace.steps[1].subprocess_path, vec!["sub_dna".to_owned()]);
    assert!(trace.steps[2].subprocess_path.is_empty());
}

#[test]
fn bpmn_extended_terminate_aborts_inflight_branch_without_charging_it() {
    let model = parse_bpmn_bytes(
        &fixture_bytes("bpmn/cancelled-terminate.bpmn"),
        BpmnProfile::ExtendedReworkSubprocess,
    )
    .unwrap();
    let cfg = parse_bpmn_config(&fixture_bytes("bpmn/cancelled-terminate.config.json")).unwrap();
    let trace = execute_bpmn(&model, &cfg).unwrap();

    assert_eq!(
        trace.status,
        ExecutionStatus::Cancelled {
            cancelled_at_node: "end_terminate".to_owned(),
            reason: "bpmn_terminate_end_event".to_owned(),
        }
    );
    assert_eq!(trace.total_elapsed_minutes, ExactQty::from_u64(5));
    assert_eq!(trace.steps.len(), 2);
    assert!(
        trace
            .usages
            .iter()
            .all(|u| u.activity_id != "deferred_assay")
    );
}

#[test]
fn bpmn_enforces_loop_bound_and_global_step_limit() {
    let model = parse_bpmn_bytes(
        &fixture_bytes("bpmn/rework-loop.bpmn"),
        BpmnProfile::ExtendedReworkSubprocess,
    )
    .unwrap();
    let mut cfg = parse_bpmn_config(&fixture_bytes("bpmn/rework-loop.config.json")).unwrap();
    cfg.branch_decisions
        .insert("gw_qc".to_owned(), vec!["flow_rework".to_owned(); 10]);
    cfg.max_node_visits = 2;
    assert_eq!(
        execute_bpmn(&model, &cfg).unwrap_err().code,
        ErrorCode::LoopBoundExceeded
    );

    let mut cfg_steps = parse_bpmn_config(&fixture_bytes("bpmn/rework-loop.config.json")).unwrap();
    cfg_steps.max_steps = 3;
    assert_eq!(
        execute_bpmn(&model, &cfg_steps).unwrap_err().code,
        ErrorCode::StepLimitExceeded
    );
}

#[test]
fn bpmn_requires_explicit_and_valid_xor_branch_decisions() {
    let model = parse_bpmn_bytes(
        &fixture_bytes("bpmn/alternative-xor.bpmn"),
        BpmnProfile::CoreAcyclic,
    )
    .unwrap();

    let mut missing =
        parse_bpmn_config(&fixture_bytes("bpmn/alternative-xor-routine.config.json")).unwrap();
    missing.branch_decisions.clear();
    assert_eq!(
        execute_bpmn(&model, &missing).unwrap_err().code,
        ErrorCode::MissingBranchDecision
    );

    let mut invalid =
        parse_bpmn_config(&fixture_bytes("bpmn/alternative-xor-routine.config.json")).unwrap();
    invalid.branch_decisions.insert(
        "gw_xor_split".to_owned(),
        vec!["nonexistent_flow".to_owned()],
    );
    assert_eq!(
        execute_bpmn(&model, &invalid).unwrap_err().code,
        ErrorCode::AmbiguousBranchDecision
    );
}

#[test]
fn bpmn_rejects_unsupported_gateways_timers_multi_instance_and_doctype() {
    for (rel, expected) in [
        (
            "bpmn/invalid-inclusive-gateway.bpmn",
            ErrorCode::UnsupportedConstruct,
        ),
        (
            "bpmn/invalid-timer-event.bpmn",
            ErrorCode::UnsupportedConstruct,
        ),
        (
            "bpmn/invalid-multi-instance.bpmn",
            ErrorCode::UnsupportedConstruct,
        ),
        (
            "bpmn/invalid-doctype.bpmn",
            ErrorCode::DisallowedXmlConstruct,
        ),
    ] {
        assert_eq!(
            parse_bpmn_bytes(&fixture_bytes(rel), BpmnProfile::ExtendedReworkSubprocess)
                .unwrap_err()
                .code,
            expected
        );
    }
}

#[test]
fn bpmn_rejects_deep_subprocess_nesting_and_non_executable_process() {
    let deep_sub = br#"<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL" id="d">
      <process id="p" isExecutable="true">
        <startEvent id="s0"/><endEvent id="e0"/>
        <subProcess id="sub1">
          <startEvent id="s1"/><endEvent id="e1"/>
          <subProcess id="sub2">
            <startEvent id="s2"/><endEvent id="e2"/>
            <subProcess id="sub3">
              <startEvent id="s3"/><endEvent id="e3"/>
              <sequenceFlow id="f3" sourceRef="s3" targetRef="e3"/>
            </subProcess>
            <sequenceFlow id="f2a" sourceRef="s2" targetRef="sub3"/>
            <sequenceFlow id="f2b" sourceRef="sub3" targetRef="e2"/>
          </subProcess>
          <sequenceFlow id="f1a" sourceRef="s1" targetRef="sub2"/>
          <sequenceFlow id="f1b" sourceRef="sub2" targetRef="e1"/>
        </subProcess>
        <sequenceFlow id="f0a" sourceRef="s0" targetRef="sub1"/>
        <sequenceFlow id="f0b" sourceRef="sub1" targetRef="e0"/>
      </process></definitions>"#;
    assert_eq!(
        parse_bpmn_bytes(deep_sub, BpmnProfile::ExtendedReworkSubprocess)
            .unwrap_err()
            .code,
        ErrorCode::SizeLimitExceeded
    );

    let non_exec = br#"<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL" id="d">
      <process id="p" isExecutable="false"><startEvent id="s"/><endEvent id="e"/>
      <sequenceFlow id="f" sourceRef="s" targetRef="e"/></process></definitions>"#;
    assert_eq!(
        parse_bpmn_bytes(non_exec, BpmnProfile::CoreAcyclic)
            .unwrap_err()
            .code,
        ErrorCode::UnsupportedConstruct
    );
}

#[test]
fn trace_round_trips_losslessly_and_is_deterministic_across_runs() {
    let model = parse_bpmn_bytes(
        &fixture_bytes("bpmn/concurrent-and-shared.bpmn"),
        BpmnProfile::CoreAcyclic,
    )
    .unwrap();
    let cfg = parse_bpmn_config(&fixture_bytes("bpmn/concurrent-and-shared.config.json")).unwrap();
    let trace_a = execute_bpmn(&model, &cfg).unwrap();
    let trace_b = execute_bpmn(&model, &cfg).unwrap();
    assert_eq!(
        trace_a.to_json().to_pretty_string(),
        trace_b.to_json().to_pretty_string()
    );
    let roundtrip = ExecutionTrace::from_json(&trace_a.to_json()).unwrap();
    assert_eq!(trace_a, roundtrip);
}

#[test]
fn quotation_release_update_leaves_physical_identities_and_quantities_unchanged() {
    let model = parse_bpmn_bytes(
        &fixture_bytes("bpmn/concurrent-and-shared.bpmn"),
        BpmnProfile::CoreAcyclic,
    )
    .unwrap();
    let cfg = parse_bpmn_config(&fixture_bytes("bpmn/concurrent-and-shared.config.json")).unwrap();
    let trace = execute_bpmn(&model, &cfg).unwrap();

    let v1 = ValuationAttachment::from_json(
        &parse_json_bytes(&fixture_bytes("quotes-release-2026-v1.json")).unwrap(),
    )
    .unwrap();
    let v2 = ValuationAttachment::from_json(
        &parse_json_bytes(&fixture_bytes("quotes-release-2026-v2.json")).unwrap(),
    )
    .unwrap();
    let req1 = project_to_dapane_request(&trace, &v1).unwrap();
    let req2 = project_to_dapane_request(&trace, &v2).unwrap();

    let o1 = req1.as_object("/").unwrap();
    let o2 = req2.as_object("/").unwrap();
    assert_eq!(o1["processes"], o2["processes"]);
    assert_eq!(o1["events"], o2["events"]);
    assert_eq!(o1["objects"], o2["objects"]);
    assert_eq!(o1["object_relations"], o2["object_relations"]);
    assert_eq!(o1["allocations"], o2["allocations"]);

    let u1 = o1["usage"].as_array("/usage").unwrap();
    let u2 = o2["usage"].as_array("/usage").unwrap();
    assert_eq!(u1.len(), u2.len());
    for (r1, r2) in u1.iter().zip(u2.iter()) {
        let m1 = r1.as_object("/u").unwrap();
        let m2 = r2.as_object("/u").unwrap();
        for key in [
            "id",
            "use_id",
            "event_id",
            "process_id",
            "activity_id",
            "target",
            "unit",
            "quantity",
            "object_ids",
            "attribution_object_id",
        ] {
            assert_eq!(m1[key], m2[key]);
        }
        assert_ne!(m1["quote_id"], m2["quote_id"]);
    }
}

#[test]
fn projection_rejects_observed_evidence_and_mismatched_quote_unit_or_overlap() {
    let model = parse_bpmn_bytes(
        &fixture_bytes("bpmn/sequential.bpmn"),
        BpmnProfile::CoreAcyclic,
    )
    .unwrap();
    let cfg = parse_bpmn_config(&fixture_bytes("bpmn/sequential.config.json")).unwrap();
    let trace = execute_bpmn(&model, &cfg).unwrap();

    let raw_v1 = String::from_utf8(fixture_bytes("quotes-release-2026-v1.json")).unwrap();
    let observed = raw_v1.replace(
        "\"source_evidence\": \"synthetic\"",
        "\"source_evidence\": \"observed\"",
    );
    assert_eq!(
        ValuationAttachment::from_json(&parse_json_bytes(observed.as_bytes()).unwrap())
            .unwrap_err()
            .code,
        ErrorCode::ValuationMismatch
    );

    let wrong_unit = raw_v1.replace("\"unit\": \"minute\"", "\"unit\": \"hour\"");
    let bad_val =
        ValuationAttachment::from_json(&parse_json_bytes(wrong_unit.as_bytes()).unwrap()).unwrap();
    assert_eq!(
        project_to_dapane_request(&trace, &bad_val)
            .unwrap_err()
            .code,
        ErrorCode::ValuationMismatch
    );

    // Pooled allocation rule targeting directly-attributed line fails visibly.
    let mut val =
        ValuationAttachment::from_json(&parse_json_bytes(raw_v1.as_bytes()).unwrap()).unwrap();
    val.allocations
        .push(dapane_process_models::model::AllocationRule {
            id: "bad-direct-overlap".to_owned(),
            match_target: "card_kit".to_owned(),
            match_activity_id: None,
            weights: vec![("infant-a".to_owned(), ExactQty::from_u64(1))],
        });
    assert_eq!(
        project_to_dapane_request(&trace, &val).unwrap_err().code,
        ErrorCode::ValuationMismatch
    );
}
