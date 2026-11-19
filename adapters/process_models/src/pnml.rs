//! X2.1 bounded PNML 2009 Place/Transition net parser and deterministic executor.

use std::collections::{BTreeMap, BTreeSet};

use crate::json_io::{JsonValue, reject_unknown_keys, req_field};
use crate::model::{
    ActivityRecipe, CONTRACT_VERSION, CostObjectDef, ErrorCode, EvidenceBasis, ExactQty,
    ExecutionStatus, ExecutionTrace, ModelError, ObjectRelationDef, StepRecording,
    parse_objects_and_relations, parse_recipes_map, record_step_and_usages, validate_token,
};
use crate::sha256::prefixed_sha256;
use crate::xml::{XmlNode, parse_xml_bytes};

/// Profile identifier for the bounded X2.1 PNML P/T net adapter.
pub const PNML_PROFILE_ID: &str = "pnml-bounded-v1";
/// ISO/IEC 15909-2 PNML 2009 core namespace URI.
pub const PNML_NS: &str = "http://www.pnml.org/version-2009/grammar/pnml";
/// ISO/IEC 15909-2 Place/Transition net grammar URI.
pub const PTNET_TYPE: &str = "http://www.pnml.org/version-2009/grammar/ptnet";

/// Validated PNML P/T net place.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PnmlPlace {
    /// Place ID.
    pub id: String,
    /// Optional human name.
    pub name: Option<String>,
    /// Initial integer token count.
    pub initial_marking: u64,
}

/// Validated PNML P/T net transition.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PnmlTransition {
    /// Transition ID.
    pub id: String,
    /// Optional human name.
    pub name: Option<String>,
}

/// Validated directed normal P/T net arc.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PnmlArc {
    /// Arc ID.
    pub id: String,
    /// Source node ID (place or transition).
    pub source: String,
    /// Target node ID (transition or place).
    pub target: String,
    /// Positive token inscription weight (`>= 1`).
    pub weight: u64,
}

/// Parsed and validated bounded P/T net model.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PnmlNet {
    /// Net identifier attribute.
    pub id: String,
    /// Optional net name.
    pub name: Option<String>,
    /// Exact `sha256:<64-hex>` of the input PNML XML bytes.
    pub model_sha256: String,
    /// Places keyed by place ID.
    pub places: BTreeMap<String, PnmlPlace>,
    /// Transitions keyed by transition ID.
    pub transitions: BTreeMap<String, PnmlTransition>,
    /// Arcs in declaration order.
    pub arcs: Vec<PnmlArc>,
}

/// Single step in an explicit Petri-net execution schedule.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FiringCommand {
    /// Transition ID to fire.
    pub transition_id: String,
    /// Firing multiplicity (`>= 1`).
    pub multiplicity: u64,
    /// When true, execution terminates cleanly after this step (`CancelledExecution`).
    pub cancel_after: bool,
    /// Caller-supplied cancellation reason when `cancel_after == true`.
    pub cancel_reason: Option<String>,
}

/// Caller configuration for `execute-pnml`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PnmlExecutionConfig {
    /// Process instance identifier.
    pub process_id: String,
    /// Logical model identifier.
    pub model_id: String,
    /// Model revision token.
    pub model_version: String,
    /// Epistemic basis (`assumed` or `simulated`).
    pub evidence_basis: EvidenceBasis,
    /// Maximum firing steps permitted (`1..=2000`).
    pub max_steps: usize,
    /// Optional expected marking verified when run finishes without cancellation.
    pub expected_final_marking: Option<BTreeMap<String, u64>>,
    /// Declared `CostObject` catalog.
    pub objects: Vec<CostObjectDef>,
    /// Declared object relationships.
    pub object_relations: Vec<ObjectRelationDef>,
    /// Per-transition activity timing and resource recipes.
    pub recipes: BTreeMap<String, ActivityRecipe>,
    /// Explicit firing sequence to validate against net semantics.
    pub schedule: Vec<FiringCommand>,
}

fn read_text_element(node: &XmlNode, path: &str) -> Result<String, ModelError> {
    let mut found: Option<String> = None;
    for child in &node.children {
        if child.namespace.as_deref() == Some(PNML_NS) && child.local_name == "text" {
            found = Some(child.trimmed_text().to_owned());
        } else if child.local_name == "graphics" {
            continue;
        } else {
            return Err(ModelError::new(
                ErrorCode::UnsupportedConstruct,
                path,
                format!("Unsupported PNML annotation element `{}`", child.raw_name),
            ));
        }
    }
    found.ok_or_else(|| {
        ModelError::new(
            ErrorCode::MalformedXml,
            path,
            "Expected `<text>` inside PNML annotation",
        )
    })
}

fn parse_u64_annotation(raw: &str, zero_allowed: bool, path: &str) -> Result<u64, ModelError> {
    let v = raw.trim().parse::<u64>().map_err(|_| {
        ModelError::new(
            if zero_allowed {
                ErrorCode::InvalidMarking
            } else {
                ErrorCode::InvalidWeight
            },
            path,
            format!("Expected nonnegative integer in PNML annotation, got `{raw}`"),
        )
    })?;
    if !zero_allowed && v == 0 {
        return Err(ModelError::new(
            ErrorCode::InvalidWeight,
            path,
            "PNML arc inscription weight must be >= 1",
        ));
    }
    Ok(v)
}

fn collect_page(
    page: &XmlNode,
    path: &str,
    places: &mut BTreeMap<String, PnmlPlace>,
    transitions: &mut BTreeMap<String, PnmlTransition>,
    arcs: &mut Vec<PnmlArc>,
    all_node_ids: &mut BTreeSet<String>,
) -> Result<(), ModelError> {
    for child in &page.children {
        if child.namespace.as_deref() != Some(PNML_NS) {
            return Err(ModelError::new(
                ErrorCode::UnsupportedModelNamespace,
                path,
                format!("Non-PNML element `{}` inside page", child.raw_name),
            ));
        }
        let cp = format!("{path}/{}", child.local_name);
        match child.local_name.as_str() {
            "graphics" | "name" => {}
            "page" => collect_page(child, &cp, places, transitions, arcs, all_node_ids)?,
            "place" => {
                let id = child
                    .attributes
                    .get("id")
                    .ok_or_else(|| {
                        ModelError::new(ErrorCode::MalformedXml, &cp, "PNML place missing `id`")
                    })?
                    .clone();
                validate_token(&id, &format!("{cp}/@id"))?;
                if !all_node_ids.insert(id.clone()) {
                    return Err(ModelError::new(
                        ErrorCode::DuplicateIdentity,
                        format!("{cp}/@id"),
                        format!("Duplicate PNML ID `{id}`"),
                    ));
                }
                let mut name = None;
                let mut initial_marking = 0u64;
                for sub in &child.children {
                    if sub.namespace.as_deref() != Some(PNML_NS) {
                        return Err(ModelError::new(
                            ErrorCode::UnsupportedModelNamespace,
                            &cp,
                            format!("Unexpected namespace element `{}`", sub.raw_name),
                        ));
                    }
                    match sub.local_name.as_str() {
                        "graphics" => {}
                        "name" => name = Some(read_text_element(sub, &format!("{cp}/name"))?),
                        "initialMarking" => {
                            let txt = read_text_element(sub, &format!("{cp}/initialMarking"))?;
                            initial_marking =
                                parse_u64_annotation(&txt, true, &format!("{cp}/initialMarking"))?;
                        }
                        other => {
                            return Err(ModelError::new(
                                ErrorCode::UnsupportedConstruct,
                                format!("{cp}/{other}"),
                                format!("Unsupported PNML place element `<{other}>`"),
                            ));
                        }
                    }
                }
                places.insert(
                    id.clone(),
                    PnmlPlace {
                        id,
                        name,
                        initial_marking,
                    },
                );
            }
            "transition" => {
                let id = child
                    .attributes
                    .get("id")
                    .ok_or_else(|| {
                        ModelError::new(
                            ErrorCode::MalformedXml,
                            &cp,
                            "PNML transition missing `id`",
                        )
                    })?
                    .clone();
                validate_token(&id, &format!("{cp}/@id"))?;
                if !all_node_ids.insert(id.clone()) {
                    return Err(ModelError::new(
                        ErrorCode::DuplicateIdentity,
                        format!("{cp}/@id"),
                        format!("Duplicate PNML ID `{id}`"),
                    ));
                }
                let mut name = None;
                for sub in &child.children {
                    if sub.namespace.as_deref() != Some(PNML_NS) {
                        return Err(ModelError::new(
                            ErrorCode::UnsupportedModelNamespace,
                            &cp,
                            format!("Unexpected namespace element `{}`", sub.raw_name),
                        ));
                    }
                    match sub.local_name.as_str() {
                        "graphics" => {}
                        "name" => name = Some(read_text_element(sub, &format!("{cp}/name"))?),
                        other => {
                            return Err(ModelError::new(
                                ErrorCode::UnsupportedConstruct,
                                format!("{cp}/{other}"),
                                format!("Unsupported PNML transition element `<{other}>`"),
                            ));
                        }
                    }
                }
                transitions.insert(id.clone(), PnmlTransition { id, name });
            }
            "arc" => {
                let id = child
                    .attributes
                    .get("id")
                    .ok_or_else(|| {
                        ModelError::new(ErrorCode::MalformedXml, &cp, "PNML arc missing `id`")
                    })?
                    .clone();
                let source = child
                    .attributes
                    .get("source")
                    .ok_or_else(|| {
                        ModelError::new(ErrorCode::MalformedXml, &cp, "PNML arc missing `source`")
                    })?
                    .clone();
                let target = child
                    .attributes
                    .get("target")
                    .ok_or_else(|| {
                        ModelError::new(ErrorCode::MalformedXml, &cp, "PNML arc missing `target`")
                    })?
                    .clone();
                validate_token(&id, &format!("{cp}/@id"))?;
                if !all_node_ids.insert(id.clone()) {
                    return Err(ModelError::new(
                        ErrorCode::DuplicateIdentity,
                        format!("{cp}/@id"),
                        format!("Duplicate PNML ID `{id}`"),
                    ));
                }
                let mut weight = 1u64;
                for sub in &child.children {
                    if sub.namespace.as_deref() != Some(PNML_NS) {
                        return Err(ModelError::new(
                            ErrorCode::UnsupportedModelNamespace,
                            &cp,
                            format!("Unexpected namespace element `{}`", sub.raw_name),
                        ));
                    }
                    match sub.local_name.as_str() {
                        "graphics" | "name" => {}
                        "inscription" => {
                            let txt = read_text_element(sub, &format!("{cp}/inscription"))?;
                            weight =
                                parse_u64_annotation(&txt, false, &format!("{cp}/inscription"))?;
                        }
                        "type" => {
                            let arc_type = sub.attributes.get("value").map(String::as_str);
                            let arc_text = read_text_element(sub, &format!("{cp}/type")).ok();
                            let kind = arc_type.or(arc_text.as_deref()).unwrap_or("");
                            if kind != "normal" {
                                return Err(ModelError::new(
                                    ErrorCode::UnsupportedConstruct,
                                    format!("{cp}/type"),
                                    format!(
                                        "Unsupported PNML arc type `{kind}` (only normal P/T arcs allowed)"
                                    ),
                                ));
                            }
                        }
                        other => {
                            return Err(ModelError::new(
                                ErrorCode::UnsupportedConstruct,
                                format!("{cp}/{other}"),
                                format!("Unsupported PNML arc element `<{other}>`"),
                            ));
                        }
                    }
                }
                arcs.push(PnmlArc {
                    id,
                    source,
                    target,
                    weight,
                });
            }
            other => {
                return Err(ModelError::new(
                    ErrorCode::UnsupportedConstruct,
                    &cp,
                    format!("Unsupported PNML page element `<{other}>`"),
                ));
            }
        }
    }
    Ok(())
}

/// Parse and validate a PNML 2009 P/T net document against `pnml-bounded-v1`.
pub fn parse_pnml_bytes(bytes: &[u8]) -> Result<PnmlNet, ModelError> {
    let model_sha256 = prefixed_sha256(bytes);
    let root = parse_xml_bytes(bytes)?;
    if root.namespace.as_deref() != Some(PNML_NS) || root.local_name != "pnml" {
        return Err(ModelError::new(
            ErrorCode::UnsupportedModelNamespace,
            "/pnml",
            "Root element must be `<pnml>` in the PNML 2009 namespace",
        ));
    }
    let nets: Vec<&XmlNode> = root
        .children
        .iter()
        .filter(|c| c.namespace.as_deref() == Some(PNML_NS) && c.local_name == "net")
        .collect();
    if nets.len() != 1 || root.children.len() != 1 {
        return Err(ModelError::new(
            ErrorCode::UnsupportedConstruct,
            "/pnml",
            "PNML document must contain exactly one `<net>` element",
        ));
    }
    let net = nets[0];
    let net_id = net
        .attributes
        .get("id")
        .ok_or_else(|| ModelError::new(ErrorCode::MalformedXml, "/pnml/net", "Net missing `id`"))?
        .clone();
    validate_token(&net_id, "/pnml/net/@id")?;
    let net_type = net.attributes.get("type").map(String::as_str).unwrap_or("");
    if net_type != PTNET_TYPE {
        return Err(ModelError::new(
            ErrorCode::UnsupportedNetType,
            "/pnml/net/@type",
            format!("Unsupported PNML net type `{net_type}` (expected P/T net)"),
        ));
    }

    let mut net_name = None;
    let mut places = BTreeMap::new();
    let mut transitions = BTreeMap::new();
    let mut arcs = Vec::new();
    let mut all_ids = BTreeSet::new();
    all_ids.insert(net_id.clone());
    let mut saw_page = false;

    for child in &net.children {
        if child.namespace.as_deref() != Some(PNML_NS) {
            return Err(ModelError::new(
                ErrorCode::UnsupportedModelNamespace,
                "/pnml/net",
                format!("Non-PNML element `{}` inside `<net>`", child.raw_name),
            ));
        }
        match child.local_name.as_str() {
            "name" => net_name = Some(read_text_element(child, "/pnml/net/name")?),
            "page" => {
                saw_page = true;
                if let Some(pid) = child.attributes.get("id") {
                    validate_token(pid, "/pnml/net/page/@id")?;
                    if !all_ids.insert(pid.clone()) {
                        return Err(ModelError::new(
                            ErrorCode::DuplicateIdentity,
                            "/pnml/net/page/@id",
                            format!("Duplicate PNML ID `{pid}`"),
                        ));
                    }
                }
                collect_page(
                    child,
                    "/pnml/net/page",
                    &mut places,
                    &mut transitions,
                    &mut arcs,
                    &mut all_ids,
                )?;
            }
            "graphics" => {}
            other => {
                return Err(ModelError::new(
                    ErrorCode::UnsupportedConstruct,
                    format!("/pnml/net/{other}"),
                    format!("Unsupported PNML `<net>` child `<{other}>`"),
                ));
            }
        }
    }

    if !saw_page {
        return Err(ModelError::new(
            ErrorCode::MalformedXml,
            "/pnml/net",
            "PNML `<net>` must contain at least one `<page>`",
        ));
    }
    if places.is_empty() || transitions.is_empty() {
        return Err(ModelError::new(
            ErrorCode::InvalidMarking,
            "/pnml/net",
            "PNML P/T net requires at least one place and one transition",
        ));
    }

    for (idx, arc) in arcs.iter().enumerate() {
        let ap = format!("/pnml/net/arcs/{idx}");
        let src_is_place = places.contains_key(&arc.source);
        let src_is_trans = transitions.contains_key(&arc.source);
        let dst_is_place = places.contains_key(&arc.target);
        let dst_is_trans = transitions.contains_key(&arc.target);
        if (!src_is_place && !src_is_trans) || (!dst_is_place && !dst_is_trans) {
            return Err(ModelError::new(
                ErrorCode::DanglingReference,
                ap,
                format!("Arc `{}` references unknown node", arc.id),
            ));
        }
        if (src_is_place && dst_is_place) || (src_is_trans && dst_is_trans) {
            return Err(ModelError::new(
                ErrorCode::UnsupportedConstruct,
                ap,
                format!("P/T arc `{}` must connect a place and a transition", arc.id),
            ));
        }
    }

    Ok(PnmlNet {
        id: net_id,
        name: net_name,
        model_sha256,
        places,
        transitions,
        arcs,
    })
}

/// Parse strict JSON execution configuration for `execute-pnml`.
pub fn parse_pnml_config(bytes: &[u8]) -> Result<PnmlExecutionConfig, ModelError> {
    let val = crate::json_io::parse_json_bytes(bytes)?;
    let root = val.as_object("/")?;
    reject_unknown_keys(
        root,
        &[
            "evidence_basis",
            "expected_final_marking",
            "max_steps",
            "model_id",
            "model_version",
            "object_relations",
            "objects",
            "process_id",
            "profile",
            "recipes",
            "schedule",
        ],
        "",
    )?;
    if let Some(profile) = root.get("profile") {
        let p = profile.as_str("/profile")?;
        if p != PNML_PROFILE_ID {
            return Err(ModelError::new(
                ErrorCode::UnsupportedConstruct,
                "/profile",
                format!("Expected `{PNML_PROFILE_ID}`, got `{p}`"),
            ));
        }
    }
    let process_id = req_field(root, "process_id", "/")?
        .as_str("/process_id")?
        .to_owned();
    let model_id = req_field(root, "model_id", "/")?
        .as_str("/model_id")?
        .to_owned();
    let model_version = req_field(root, "model_version", "/")?
        .as_str("/model_version")?
        .to_owned();
    validate_token(&process_id, "/process_id")?;
    validate_token(&model_id, "/model_id")?;
    validate_token(&model_version, "/model_version")?;
    let evidence_basis = EvidenceBasis::parse(
        req_field(root, "evidence_basis", "/")?.as_str("/evidence_basis")?,
        "/evidence_basis",
    )?;
    let max_steps = match root.get("max_steps") {
        None => 256,
        Some(v) => v.as_u64("/max_steps")? as usize,
    };
    if max_steps == 0 || max_steps > 2_000 {
        return Err(ModelError::new(
            ErrorCode::InvalidWeight,
            "/max_steps",
            "max_steps must be between 1 and 2000",
        ));
    }

    let expected_final_marking = match root.get("expected_final_marking") {
        None | Some(JsonValue::Null) => None,
        Some(v) => {
            let mo = v.as_object("/expected_final_marking")?;
            let mut m = BTreeMap::new();
            for (k, c) in mo {
                m.insert(
                    k.clone(),
                    c.as_u64(&format!("/expected_final_marking/{k}"))?,
                );
            }
            Some(m)
        }
    };

    let (objects, known_objects, object_relations) = parse_objects_and_relations(root, "")?;
    let recipes = parse_recipes_map(req_field(root, "recipes", "/")?, &known_objects, "/recipes")?;

    let sched_arr = req_field(root, "schedule", "/")?.as_array("/schedule")?;
    let mut schedule = Vec::with_capacity(sched_arr.len());
    for (idx, item) in sched_arr.iter().enumerate() {
        let sp = format!("/schedule/{idx}");
        let so = item.as_object(&sp)?;
        reject_unknown_keys(
            so,
            &[
                "cancel_after",
                "cancel_reason",
                "multiplicity",
                "transition_id",
            ],
            &sp,
        )?;
        let transition_id = req_field(so, "transition_id", &sp)?
            .as_str(&format!("{sp}/transition_id"))?
            .to_owned();
        let multiplicity = match so.get("multiplicity") {
            None => 1,
            Some(v) => v.as_u64(&format!("{sp}/multiplicity"))?,
        };
        if multiplicity == 0 {
            return Err(ModelError::new(
                ErrorCode::InvalidWeight,
                format!("{sp}/multiplicity"),
                "Transition firing multiplicity must be >= 1",
            ));
        }
        let cancel_after = match so.get("cancel_after") {
            None => false,
            Some(v) => v.as_bool(&format!("{sp}/cancel_after"))?,
        };
        let cancel_reason = match so.get("cancel_reason") {
            None | Some(JsonValue::Null) => None,
            Some(v) => Some(v.as_str(&format!("{sp}/cancel_reason"))?.to_owned()),
        };
        schedule.push(FiringCommand {
            transition_id,
            multiplicity,
            cancel_after,
            cancel_reason,
        });
    }

    Ok(PnmlExecutionConfig {
        process_id,
        model_id,
        model_version,
        evidence_basis,
        max_steps,
        expected_final_marking,
        objects,
        object_relations,
        recipes,
        schedule,
    })
}

/// Deterministically execute a validated PNML P/T net schedule and emit an `ExecutionTrace`.
pub fn execute_petri_net(
    net: &PnmlNet,
    config: &PnmlExecutionConfig,
) -> Result<ExecutionTrace, ModelError> {
    if config.schedule.len() > config.max_steps {
        return Err(ModelError::new(
            ErrorCode::StepLimitExceeded,
            "/schedule",
            "PNML firing schedule exceeds configured max_steps",
        ));
    }

    let initial_marking: BTreeMap<String, u64> = net
        .places
        .iter()
        .map(|(id, p)| (id.clone(), p.initial_marking))
        .collect();
    let mut marking = initial_marking.clone();

    let mut pre_arcs: BTreeMap<&str, Vec<(&str, u64)>> = BTreeMap::new();
    let mut post_arcs: BTreeMap<&str, Vec<(&str, u64)>> = BTreeMap::new();
    for arc in &net.arcs {
        if net.places.contains_key(&arc.source) && net.transitions.contains_key(&arc.target) {
            pre_arcs
                .entry(arc.target.as_str())
                .or_default()
                .push((arc.source.as_str(), arc.weight));
        } else if net.transitions.contains_key(&arc.source) && net.places.contains_key(&arc.target)
        {
            post_arcs
                .entry(arc.source.as_str())
                .or_default()
                .push((arc.target.as_str(), arc.weight));
        }
    }

    if let Some(expected) = &config.expected_final_marking {
        for place_id in expected.keys() {
            if !marking.contains_key(place_id) {
                return Err(ModelError::new(
                    ErrorCode::DanglingReference,
                    format!("/expected_final_marking/{place_id}"),
                    format!("Unknown PNML place `{place_id}`"),
                ));
            }
        }
    }

    let mut steps = Vec::new();
    let mut usages = Vec::new();
    let mut elapsed = ExactQty::zero();
    let mut visits: BTreeMap<String, u64> = BTreeMap::new();
    let mut status = ExecutionStatus::Completed;

    for (idx, cmd) in config.schedule.iter().enumerate() {
        let sp = format!("/schedule/{idx}");
        if !net.transitions.contains_key(&cmd.transition_id) {
            return Err(ModelError::new(
                ErrorCode::DanglingReference,
                format!("{sp}/transition_id"),
                format!("Unknown PNML transition `{}`", cmd.transition_id),
            ));
        }
        let recipe = config.recipes.get(&cmd.transition_id).ok_or_else(|| {
            ModelError::new(
                ErrorCode::DanglingReference,
                "/recipes",
                format!("Missing recipe for PNML transition `{}`", cmd.transition_id),
            )
        })?;

        if let Some(inputs) = pre_arcs.get(cmd.transition_id.as_str()) {
            for (place_id, weight) in inputs {
                let required = weight.checked_mul(cmd.multiplicity).ok_or_else(|| {
                    ModelError::new(
                        ErrorCode::ArithmeticOverflow,
                        &sp,
                        "Required token weight overflow",
                    )
                })?;
                let avail = marking[*place_id];
                if avail < required {
                    return Err(ModelError::new(
                        ErrorCode::NotEnabled,
                        &sp,
                        format!(
                            "Transition `{}` requires {required} token(s) in `{place_id}`, found {avail}",
                            cmd.transition_id
                        ),
                    ));
                }
            }
            for (place_id, weight) in inputs {
                let required = weight * cmd.multiplicity;
                if let Some(slot) = marking.get_mut(*place_id) {
                    *slot -= required;
                }
            }
        }

        if let Some(outputs) = post_arcs.get(cmd.transition_id.as_str()) {
            for (place_id, weight) in outputs {
                let produced = weight.checked_mul(cmd.multiplicity).ok_or_else(|| {
                    ModelError::new(
                        ErrorCode::ArithmeticOverflow,
                        &sp,
                        "Produced token weight overflow",
                    )
                })?;
                let slot = marking.get_mut(*place_id).expect("validated place");
                *slot = slot.checked_add(produced).ok_or_else(|| {
                    ModelError::new(ErrorCode::ArithmeticOverflow, &sp, "Place marking overflow")
                })?;
            }
        }

        let visit = visits
            .entry(cmd.transition_id.clone())
            .and_modify(|v| *v += 1)
            .or_insert(1);
        let visit_num = *visit;
        let step_id = format!("pnml:s{}:{}:{visit_num}", idx + 1, cmd.transition_id);
        let start = elapsed;
        let end = start.checked_add(recipe.duration_minutes, &sp)?;
        elapsed = end;

        record_step_and_usages(
            &mut steps,
            &mut usages,
            StepRecording {
                step_id,
                node_id: cmd.transition_id.clone(),
                subprocess_path: Vec::new(),
                visit: visit_num,
                multiplicity: cmd.multiplicity,
                start_minute: start,
                end_minute: end,
                recipe,
                evidence_basis: config.evidence_basis,
            },
        )?;

        if cmd.cancel_after {
            status = ExecutionStatus::Cancelled {
                cancelled_at_node: cmd.transition_id.clone(),
                reason: cmd
                    .cancel_reason
                    .clone()
                    .unwrap_or_else(|| "caller_cancelled_after_step".to_owned()),
            };
            break;
        }
    }

    if matches!(status, ExecutionStatus::Completed)
        && let Some(expected) = &config.expected_final_marking
    {
        for (place_id, actual_count) in &marking {
            let want = expected.get(place_id).copied().unwrap_or(0);
            if *actual_count != want {
                return Err(ModelError::new(
                    ErrorCode::FinalMarkingMismatch,
                    format!("/expected_final_marking/{place_id}"),
                    format!(
                        "Place `{place_id}` ended with {actual_count} token(s), expected {want}"
                    ),
                ));
            }
        }
    }

    Ok(ExecutionTrace {
        contract_version: CONTRACT_VERSION.to_owned(),
        profile_id: PNML_PROFILE_ID.to_owned(),
        model_sha256: net.model_sha256.clone(),
        process_id: config.process_id.clone(),
        model_id: config.model_id.clone(),
        model_version: config.model_version.clone(),
        evidence_basis: config.evidence_basis,
        status,
        initial_marking: Some(initial_marking),
        final_marking: Some(marking),
        total_elapsed_minutes: elapsed,
        objects: config.objects.clone(),
        object_relations: config.object_relations.clone(),
        steps,
        usages,
    })
}
