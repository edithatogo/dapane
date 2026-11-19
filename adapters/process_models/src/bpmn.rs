//! X2.2 & X2.3 bounded OMG BPMN 2.0 subset parser and deterministic executor.

use std::cmp::Ordering;
use std::collections::{BTreeMap, BTreeSet, VecDeque};

use crate::json_io::{reject_unknown_keys, req_field};
use crate::model::{
    ActivityRecipe, CONTRACT_VERSION, CostObjectDef, ErrorCode, EvidenceBasis, ExactQty,
    ExecutionStatus, ExecutionTrace, ModelError, ObjectRelationDef, StepRecording,
    parse_objects_and_relations, parse_recipes_map, record_step_and_usages, validate_token,
};
use crate::sha256::prefixed_sha256;
use crate::xml::{XmlNode, parse_xml_bytes};

/// X2.2 acyclic core BPMN 2.0 profile identifier.
pub const BPMN_CORE_PROFILE_ID: &str = "bpmn-core-acyclic-v1";
/// X2.3 extended BPMN 2.0 profile identifier (rework loops, terminate end events, embedded subprocesses).
pub const BPMN_EXTENDED_PROFILE_ID: &str = "bpmn-extended-rework-subprocess-v1";
/// OMG BPMN 2.0 model namespace URI.
pub const BPMN_NS: &str = "http://www.omg.org/spec/BPMN/20100524/MODEL";
/// OMG BPMN 2.0 visual diagram interchange namespace URI (non-semantic layout only).
pub const BPMNDI_NS: &str = "http://www.omg.org/spec/BPMN/20100524/DI";
/// OMG DI / DC namespaces tolerated strictly inside `<bpmndi:BPMNDiagram>`.
const DI_TOLERATED_NS: &[&str] = &[
    BPMNDI_NS,
    "http://www.omg.org/spec/DD/20100524/DI",
    "http://www.omg.org/spec/DD/20100524/DC",
];
/// Maximum embedded `<subProcess>` nesting depth permitted in X2.3.
pub const MAX_SUBPROCESS_DEPTH: usize = 2;

/// Selectable BPMN validation and execution profile.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BpmnProfile {
    /// X2.2 strict acyclic profile: start/end none events, tasks, XOR/AND gateways only.
    CoreAcyclic,
    /// X2.3 extended profile: adds bounded XOR rework loops, terminate end events, and embedded subprocesses.
    ExtendedReworkSubprocess,
}

impl BpmnProfile {
    /// Parse profile token cleanly.
    pub fn parse(raw: &str, path: &str) -> Result<Self, ModelError> {
        match raw {
            BPMN_CORE_PROFILE_ID => Ok(Self::CoreAcyclic),
            BPMN_EXTENDED_PROFILE_ID => Ok(Self::ExtendedReworkSubprocess),
            _ => Err(ModelError::new(
                ErrorCode::UnsupportedConstruct,
                path,
                format!("Unsupported BPMN profile `{raw}`"),
            )),
        }
    }

    /// Canonical profile identifier.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::CoreAcyclic => BPMN_CORE_PROFILE_ID,
            Self::ExtendedReworkSubprocess => BPMN_EXTENDED_PROFILE_ID,
        }
    }
}

/// Supported BPMN node kinds in X2.2 / X2.3.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BpmnNodeKind {
    /// None `<startEvent>`.
    StartEvent,
    /// None `<endEvent>`.
    EndEvent,
    /// `<endEvent><terminateEventDefinition/></endEvent>` (`ExtendedReworkSubprocess` only).
    TerminateEndEvent,
    /// Supported atomic task (`task`, `serviceTask`, `userTask`, `manualTask`).
    Task {
        /// Concrete XML local tag name.
        task_tag: String,
    },
    /// `<exclusiveGateway>` (XOR split / merge).
    ExclusiveGateway,
    /// `<parallelGateway>` (AND fork / join).
    ParallelGateway,
    /// Embedded `<subProcess>` scope (`ExtendedReworkSubprocess` only).
    SubProcess(BpmnScope),
}

/// Parsed node inside a BPMN `<process>` or `<subProcess>`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BpmnNode {
    /// Node ID.
    pub id: String,
    /// Optional human name.
    pub name: Option<String>,
    /// Semantic kind.
    pub kind: BpmnNodeKind,
    /// Incoming sequenceFlow IDs declared by `<sequenceFlow targetRef=...>`.
    pub incoming: Vec<String>,
    /// Outgoing sequenceFlow IDs declared by `<sequenceFlow sourceRef=...>`.
    pub outgoing: Vec<String>,
}

/// Directed BPMN `<sequenceFlow>`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BpmnFlow {
    /// Sequence flow ID.
    pub id: String,
    /// Optional name.
    pub name: Option<String>,
    /// Source node ID in this scope.
    pub source_ref: String,
    /// Target node ID in this scope.
    pub target_ref: String,
}

/// Validated flow scope (top-level `<process>` or embedded `<subProcess>`).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BpmnScope {
    /// Process or SubProcess ID.
    pub id: String,
    /// Unique startEvent ID in this scope.
    pub start_event_id: String,
    /// Nodes keyed by ID.
    pub nodes: BTreeMap<String, BpmnNode>,
    /// Sequence flows keyed by ID.
    pub flows: BTreeMap<String, BpmnFlow>,
}

/// Validated BPMN 2.0 process model ready for deterministic token execution.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BpmnModel {
    /// Profile under which this model passed validation.
    pub profile: BpmnProfile,
    /// Exact `sha256:<64-hex>` of the input BPMN XML bytes.
    pub model_sha256: String,
    /// Top-level executable `<process>` scope.
    pub process: BpmnScope,
}

/// Caller configuration for `execute-bpmn`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BpmnExecutionConfig {
    /// Requested BPMN execution profile.
    pub profile: BpmnProfile,
    /// Process instance identifier.
    pub process_id: String,
    /// Logical model identifier.
    pub model_id: String,
    /// Model revision token.
    pub model_version: String,
    /// Epistemic basis (`assumed` or `simulated`).
    pub evidence_basis: EvidenceBasis,
    /// Global limit on committed activity/gateway/event steps.
    pub max_steps: usize,
    /// Per-node visit limit inside loops (`ExtendedReworkSubprocess`).
    pub max_node_visits: u64,
    /// Per-XOR-gateway ordered queue of chosen outgoing `sequenceFlow` IDs.
    pub branch_decisions: BTreeMap<String, Vec<String>>,
    /// Declared `CostObject` catalog.
    pub objects: Vec<CostObjectDef>,
    /// Declared object relationships.
    pub object_relations: Vec<ObjectRelationDef>,
    /// Activity timing and resource recipes keyed by BPMN node ID (or `scope/node` qualified ID).
    pub recipes: BTreeMap<String, ActivityRecipe>,
}

fn check_di_subtree(node: &XmlNode, path: &str) -> Result<(), ModelError> {
    match &node.namespace {
        Some(ns) if DI_TOLERATED_NS.contains(&ns.as_str()) => {}
        _ => {
            return Err(ModelError::new(
                ErrorCode::UnsupportedModelNamespace,
                path,
                format!(
                    "Unsupported namespace inside BPMNDiagram: `{}`",
                    node.raw_name
                ),
            ));
        }
    }
    for child in &node.children {
        check_di_subtree(child, &format!("{path}/{}", child.local_name))?;
    }
    Ok(())
}

fn check_no_cycles(scope: &BpmnScope, path: &str) -> Result<(), ModelError> {
    let mut state: BTreeMap<&str, u8> = BTreeMap::new();
    fn dfs<'a>(
        node_id: &'a str,
        scope: &'a BpmnScope,
        state: &mut BTreeMap<&'a str, u8>,
        path: &str,
    ) -> Result<(), ModelError> {
        state.insert(node_id, 1);
        if let Some(node) = scope.nodes.get(node_id) {
            for fid in &node.outgoing {
                let target = scope.flows[fid].target_ref.as_str();
                match state.get(target).copied() {
                    Some(1) => {
                        return Err(ModelError::new(
                            ErrorCode::CycleNotAllowedInCoreProfile,
                            format!("{path}/{node_id}"),
                            format!(
                                "Cycle detected on sequenceFlow `{fid}` to `{target}` (not permitted in `bpmn-core-acyclic-v1`)"
                            ),
                        ));
                    }
                    Some(2) => {}
                    _ => dfs(target, scope, state, path)?,
                }
            }
        }
        state.insert(node_id, 2);
        Ok(())
    }
    for id in scope.nodes.keys() {
        if !state.contains_key(id.as_str()) {
            dfs(id, scope, &mut state, path)?;
        }
    }
    Ok(())
}

fn parse_scope(
    elem: &XmlNode,
    profile: BpmnProfile,
    depth: usize,
    global_ids: &mut BTreeSet<String>,
    path: &str,
) -> Result<BpmnScope, ModelError> {
    if depth > MAX_SUBPROCESS_DEPTH {
        return Err(ModelError::new(
            ErrorCode::SizeLimitExceeded,
            path,
            "BPMN subprocess nesting exceeds maximum supported depth",
        ));
    }
    let scope_id = elem
        .attributes
        .get("id")
        .ok_or_else(|| {
            ModelError::new(
                ErrorCode::MalformedXml,
                path,
                format!("BPMN `<{}>` missing `id` attribute", elem.local_name),
            )
        })?
        .clone();
    validate_token(&scope_id, &format!("{path}/@id"))?;
    if !global_ids.insert(scope_id.clone()) {
        return Err(ModelError::new(
            ErrorCode::DuplicateIdentity,
            format!("{path}/@id"),
            format!("Duplicate BPMN element ID `{scope_id}`"),
        ));
    }

    let mut nodes: BTreeMap<String, BpmnNode> = BTreeMap::new();
    let mut flows: BTreeMap<String, BpmnFlow> = BTreeMap::new();
    let mut start_events = Vec::new();
    let mut has_end_event = false;

    for child in &elem.children {
        if child.namespace.as_deref() != Some(BPMN_NS) {
            return Err(ModelError::new(
                ErrorCode::UnsupportedModelNamespace,
                format!("{path}/{}", child.raw_name),
                format!("Unsupported non-BPMN element `{}`", child.raw_name),
            ));
        }
        let cp = format!("{path}/{}", child.local_name);
        match child.local_name.as_str() {
            "documentation" | "incoming" | "outgoing" | "laneSet" => {}
            "sequenceFlow" => {
                let fid = child
                    .attributes
                    .get("id")
                    .ok_or_else(|| {
                        ModelError::new(ErrorCode::MalformedXml, &cp, "sequenceFlow missing `id`")
                    })?
                    .clone();
                let source_ref = child
                    .attributes
                    .get("sourceRef")
                    .ok_or_else(|| {
                        ModelError::new(
                            ErrorCode::MalformedXml,
                            &cp,
                            format!("sequenceFlow `{fid}` missing `sourceRef`"),
                        )
                    })?
                    .clone();
                let target_ref = child
                    .attributes
                    .get("targetRef")
                    .ok_or_else(|| {
                        ModelError::new(
                            ErrorCode::MalformedXml,
                            &cp,
                            format!("sequenceFlow `{fid}` missing `targetRef`"),
                        )
                    })?
                    .clone();
                validate_token(&fid, &format!("{cp}/@id"))?;
                if !global_ids.insert(fid.clone()) {
                    return Err(ModelError::new(
                        ErrorCode::DuplicateIdentity,
                        format!("{cp}/@id"),
                        format!("Duplicate BPMN ID `{fid}`"),
                    ));
                }
                for sub in &child.children {
                    if sub.local_name != "documentation" {
                        return Err(ModelError::new(
                            ErrorCode::UnsupportedConstruct,
                            format!("{cp}/{}", sub.local_name),
                            format!("Unsupported sequenceFlow child `<{}>`", sub.local_name),
                        ));
                    }
                }
                flows.insert(
                    fid.clone(),
                    BpmnFlow {
                        id: fid,
                        name: child.attributes.get("name").cloned(),
                        source_ref,
                        target_ref,
                    },
                );
            }
            "startEvent" => {
                let id = child
                    .attributes
                    .get("id")
                    .ok_or_else(|| {
                        ModelError::new(ErrorCode::MalformedXml, &cp, "startEvent missing `id`")
                    })?
                    .clone();
                validate_token(&id, &format!("{cp}/@id"))?;
                if !global_ids.insert(id.clone()) {
                    return Err(ModelError::new(
                        ErrorCode::DuplicateIdentity,
                        format!("{cp}/@id"),
                        format!("Duplicate BPMN ID `{id}`"),
                    ));
                }
                for sub in &child.children {
                    if !matches!(sub.local_name.as_str(), "outgoing" | "documentation") {
                        return Err(ModelError::new(
                            ErrorCode::UnsupportedConstruct,
                            format!("{cp}/{}", sub.local_name),
                            format!(
                                "Only none startEvent is supported; found `<{}>`",
                                sub.local_name
                            ),
                        ));
                    }
                }
                start_events.push(id.clone());
                nodes.insert(
                    id.clone(),
                    BpmnNode {
                        id,
                        name: child.attributes.get("name").cloned(),
                        kind: BpmnNodeKind::StartEvent,
                        incoming: Vec::new(),
                        outgoing: Vec::new(),
                    },
                );
            }
            "endEvent" => {
                let id = child
                    .attributes
                    .get("id")
                    .ok_or_else(|| {
                        ModelError::new(ErrorCode::MalformedXml, &cp, "endEvent missing `id`")
                    })?
                    .clone();
                validate_token(&id, &format!("{cp}/@id"))?;
                if !global_ids.insert(id.clone()) {
                    return Err(ModelError::new(
                        ErrorCode::DuplicateIdentity,
                        format!("{cp}/@id"),
                        format!("Duplicate BPMN ID `{id}`"),
                    ));
                }
                let mut is_terminate = false;
                for sub in &child.children {
                    if sub.namespace.as_deref() != Some(BPMN_NS) {
                        return Err(ModelError::new(
                            ErrorCode::UnsupportedModelNamespace,
                            &cp,
                            format!("Unexpected element `{}` in endEvent", sub.raw_name),
                        ));
                    }
                    match sub.local_name.as_str() {
                        "incoming" | "documentation" => {}
                        "terminateEventDefinition" => {
                            if profile != BpmnProfile::ExtendedReworkSubprocess {
                                return Err(ModelError::new(
                                    ErrorCode::UnsupportedConstruct,
                                    format!("{cp}/terminateEventDefinition"),
                                    "Terminate endEvent is not allowed in `bpmn-core-acyclic-v1`",
                                ));
                            }
                            is_terminate = true;
                        }
                        other => {
                            return Err(ModelError::new(
                                ErrorCode::UnsupportedConstruct,
                                format!("{cp}/{other}"),
                                format!("Unsupported endEvent definition `<{other}>`"),
                            ));
                        }
                    }
                }
                has_end_event = true;
                nodes.insert(
                    id.clone(),
                    BpmnNode {
                        id,
                        name: child.attributes.get("name").cloned(),
                        kind: if is_terminate {
                            BpmnNodeKind::TerminateEndEvent
                        } else {
                            BpmnNodeKind::EndEvent
                        },
                        incoming: Vec::new(),
                        outgoing: Vec::new(),
                    },
                );
            }
            "task" | "serviceTask" | "userTask" | "manualTask" => {
                let id = child
                    .attributes
                    .get("id")
                    .ok_or_else(|| {
                        ModelError::new(ErrorCode::MalformedXml, &cp, "Task missing `id`")
                    })?
                    .clone();
                validate_token(&id, &format!("{cp}/@id"))?;
                if !global_ids.insert(id.clone()) {
                    return Err(ModelError::new(
                        ErrorCode::DuplicateIdentity,
                        format!("{cp}/@id"),
                        format!("Duplicate BPMN ID `{id}`"),
                    ));
                }
                for sub in &child.children {
                    if !matches!(
                        sub.local_name.as_str(),
                        "incoming" | "outgoing" | "documentation"
                    ) {
                        return Err(ModelError::new(
                            ErrorCode::UnsupportedConstruct,
                            format!("{cp}/{}", sub.local_name),
                            format!(
                                "Unsupported task modifier `<{}>` inside `<{}>`",
                                sub.local_name, child.local_name
                            ),
                        ));
                    }
                }
                nodes.insert(
                    id.clone(),
                    BpmnNode {
                        id,
                        name: child.attributes.get("name").cloned(),
                        kind: BpmnNodeKind::Task {
                            task_tag: child.local_name.clone(),
                        },
                        incoming: Vec::new(),
                        outgoing: Vec::new(),
                    },
                );
            }
            "exclusiveGateway" | "parallelGateway" => {
                let id = child
                    .attributes
                    .get("id")
                    .ok_or_else(|| {
                        ModelError::new(ErrorCode::MalformedXml, &cp, "Gateway missing `id`")
                    })?
                    .clone();
                validate_token(&id, &format!("{cp}/@id"))?;
                if !global_ids.insert(id.clone()) {
                    return Err(ModelError::new(
                        ErrorCode::DuplicateIdentity,
                        format!("{cp}/@id"),
                        format!("Duplicate BPMN ID `{id}`"),
                    ));
                }
                for sub in &child.children {
                    if !matches!(
                        sub.local_name.as_str(),
                        "incoming" | "outgoing" | "documentation"
                    ) {
                        return Err(ModelError::new(
                            ErrorCode::UnsupportedConstruct,
                            format!("{cp}/{}", sub.local_name),
                            format!("Unsupported gateway child `<{}>`", sub.local_name),
                        ));
                    }
                }
                let kind = if child.local_name == "exclusiveGateway" {
                    BpmnNodeKind::ExclusiveGateway
                } else {
                    BpmnNodeKind::ParallelGateway
                };
                nodes.insert(
                    id.clone(),
                    BpmnNode {
                        id,
                        name: child.attributes.get("name").cloned(),
                        kind,
                        incoming: Vec::new(),
                        outgoing: Vec::new(),
                    },
                );
            }
            "subProcess" => {
                if profile != BpmnProfile::ExtendedReworkSubprocess {
                    return Err(ModelError::new(
                        ErrorCode::UnsupportedConstruct,
                        cp,
                        "`<subProcess>` is not permitted in `bpmn-core-acyclic-v1`",
                    ));
                }
                if child
                    .attributes
                    .get("triggeredByEvent")
                    .is_some_and(|v| v == "true")
                {
                    return Err(ModelError::new(
                        ErrorCode::UnsupportedConstruct,
                        format!("{cp}/@triggeredByEvent"),
                        "Event subprocesses are outside the bounded X2.3 profile",
                    ));
                }
                let sub_scope = parse_scope(child, profile, depth + 1, global_ids, &cp)?;
                let id = sub_scope.id.clone();
                nodes.insert(
                    id.clone(),
                    BpmnNode {
                        id,
                        name: child.attributes.get("name").cloned(),
                        kind: BpmnNodeKind::SubProcess(sub_scope),
                        incoming: Vec::new(),
                        outgoing: Vec::new(),
                    },
                );
            }
            other => {
                return Err(ModelError::new(
                    ErrorCode::UnsupportedConstruct,
                    &cp,
                    format!("Unsupported BPMN construct `<{other}>`"),
                ));
            }
        }
    }

    if start_events.len() != 1 || !has_end_event {
        return Err(ModelError::new(
            ErrorCode::UnsupportedConstruct,
            path,
            "BPMN process/subprocess requires exactly one startEvent and at least one endEvent",
        ));
    }

    let flow_list: Vec<BpmnFlow> = flows.values().cloned().collect();
    for flow in flow_list {
        if !nodes.contains_key(&flow.source_ref) || !nodes.contains_key(&flow.target_ref) {
            return Err(ModelError::new(
                ErrorCode::DanglingReference,
                format!("{path}/sequenceFlow/{}", flow.id),
                format!(
                    "sequenceFlow `{}` must connect nodes within the same scope",
                    flow.id
                ),
            ));
        }
        nodes
            .get_mut(&flow.source_ref)
            .expect("checked source")
            .outgoing
            .push(flow.id.clone());
        nodes
            .get_mut(&flow.target_ref)
            .expect("checked target")
            .incoming
            .push(flow.id.clone());
    }

    for (id, node) in &mut nodes {
        node.incoming.sort();
        node.outgoing.sort();
        match &node.kind {
            BpmnNodeKind::StartEvent => {
                if !node.incoming.is_empty() || node.outgoing.len() != 1 {
                    return Err(ModelError::new(
                        ErrorCode::UnsupportedConstruct,
                        format!("{path}/{id}"),
                        "startEvent must have 0 incoming and 1 outgoing sequenceFlow",
                    ));
                }
            }
            BpmnNodeKind::EndEvent | BpmnNodeKind::TerminateEndEvent => {
                if node.incoming.is_empty() || !node.outgoing.is_empty() {
                    return Err(ModelError::new(
                        ErrorCode::UnsupportedConstruct,
                        format!("{path}/{id}"),
                        "endEvent must have >= 1 incoming and 0 outgoing sequenceFlows",
                    ));
                }
            }
            BpmnNodeKind::Task { .. } | BpmnNodeKind::SubProcess(_) => {
                if node.incoming.len() != 1 || node.outgoing.len() != 1 {
                    return Err(ModelError::new(
                        ErrorCode::UnsupportedConstruct,
                        format!("{path}/{id}"),
                        "Task/SubProcess in bounded profile requires 1 incoming and 1 outgoing sequenceFlow (use explicit gateways for splits/joins)",
                    ));
                }
            }
            BpmnNodeKind::ExclusiveGateway | BpmnNodeKind::ParallelGateway => {
                if node.incoming.is_empty() || node.outgoing.is_empty() {
                    return Err(ModelError::new(
                        ErrorCode::UnsupportedConstruct,
                        format!("{path}/{id}"),
                        "Gateway requires >= 1 incoming and >= 1 outgoing sequenceFlow",
                    ));
                }
            }
        }
    }

    let scope = BpmnScope {
        id: scope_id,
        start_event_id: start_events[0].clone(),
        nodes,
        flows,
    };
    if profile == BpmnProfile::CoreAcyclic {
        check_no_cycles(&scope, path)?;
    }
    Ok(scope)
}

/// Parse and validate OMG BPMN 2.0 XML against `bpmn-core-acyclic-v1` or `bpmn-extended-rework-subprocess-v1`.
pub fn parse_bpmn_bytes(bytes: &[u8], profile: BpmnProfile) -> Result<BpmnModel, ModelError> {
    let model_sha256 = prefixed_sha256(bytes);
    let root = parse_xml_bytes(bytes)?;
    if root.namespace.as_deref() != Some(BPMN_NS) || root.local_name != "definitions" {
        return Err(ModelError::new(
            ErrorCode::UnsupportedModelNamespace,
            "/definitions",
            "Root element must be `<definitions>` in the OMG BPMN 2.0 namespace",
        ));
    }

    let mut processes = Vec::new();
    for child in &root.children {
        if child.namespace.as_deref() == Some(BPMNDI_NS) && child.local_name == "BPMNDiagram" {
            check_di_subtree(child, "/definitions/BPMNDiagram")?;
            continue;
        }
        if child.namespace.as_deref() != Some(BPMN_NS) {
            return Err(ModelError::new(
                ErrorCode::UnsupportedModelNamespace,
                format!("/definitions/{}", child.raw_name),
                format!("Unsupported `<definitions>` element `{}`", child.raw_name),
            ));
        }
        match child.local_name.as_str() {
            "process" => processes.push(child),
            other => {
                return Err(ModelError::new(
                    ErrorCode::UnsupportedConstruct,
                    format!("/definitions/{other}"),
                    format!("Unsupported BPMN definitions element `<{other}>`"),
                ));
            }
        }
    }
    if processes.len() != 1 {
        return Err(ModelError::new(
            ErrorCode::UnsupportedConstruct,
            "/definitions",
            "BPMN definitions must contain exactly one `<process>`",
        ));
    }
    if processes[0]
        .attributes
        .get("isExecutable")
        .is_some_and(|v| v == "false")
    {
        return Err(ModelError::new(
            ErrorCode::UnsupportedConstruct,
            "/definitions/process/@isExecutable",
            "Non-executable BPMN process cannot be executed",
        ));
    }

    let mut global_ids = BTreeSet::new();
    let process = parse_scope(
        processes[0],
        profile,
        0,
        &mut global_ids,
        "/definitions/process",
    )?;
    Ok(BpmnModel {
        profile,
        model_sha256,
        process,
    })
}

/// Parse strict JSON execution configuration for `execute-bpmn`.
pub fn parse_bpmn_config(bytes: &[u8]) -> Result<BpmnExecutionConfig, ModelError> {
    let val = crate::json_io::parse_json_bytes(bytes)?;
    let root = val.as_object("/")?;
    reject_unknown_keys(
        root,
        &[
            "branch_decisions",
            "evidence_basis",
            "max_node_visits",
            "max_steps",
            "model_id",
            "model_version",
            "object_relations",
            "objects",
            "process_id",
            "profile",
            "recipes",
        ],
        "",
    )?;
    let profile = BpmnProfile::parse(
        req_field(root, "profile", "/")?.as_str("/profile")?,
        "/profile",
    )?;
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
    let max_node_visits = match root.get("max_node_visits") {
        None => 16,
        Some(v) => v.as_u64("/max_node_visits")?,
    };
    if max_node_visits == 0 || max_node_visits > 64 {
        return Err(ModelError::new(
            ErrorCode::InvalidWeight,
            "/max_node_visits",
            "max_node_visits must be between 1 and 64",
        ));
    }

    let mut branch_decisions = BTreeMap::new();
    if let Some(raw_dec) = root.get("branch_decisions") {
        let map = raw_dec.as_object("/branch_decisions")?;
        for (gw, choices) in map {
            let gp = format!("/branch_decisions/{gw}");
            let mut list = Vec::new();
            for (idx, c) in choices.as_array(&gp)?.iter().enumerate() {
                list.push(c.as_str(&format!("{gp}/{idx}"))?.to_owned());
            }
            branch_decisions.insert(gw.clone(), list);
        }
    }

    let (objects, known_objects, object_relations) = parse_objects_and_relations(root, "")?;
    let recipes = parse_recipes_map(req_field(root, "recipes", "/")?, &known_objects, "/recipes")?;

    Ok(BpmnExecutionConfig {
        profile,
        process_id,
        model_id,
        model_version,
        evidence_basis,
        max_steps,
        max_node_visits,
        branch_decisions,
        objects,
        object_relations,
        recipes,
    })
}

#[derive(Debug, Clone, PartialEq, Eq)]
enum EventPayload {
    /// Token arriving at `node_id` via optional `incoming_flow_id` inside `scope_path`.
    Arrive {
        scope_path: Vec<String>,
        node_id: String,
        incoming_flow_id: Option<String>,
    },
    /// Task completing at `end_time`, triggering its outgoing flow and emitting step/usages.
    CompleteTask {
        scope_path: Vec<String>,
        node_id: String,
        visit: u64,
        start_time: ExactQty,
    },
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct TimedEvent {
    time: ExactQty,
    /// `0` = task completions, `1` = node arrivals (so completions commit cleanly at boundary ticks).
    kind_rank: u8,
    scope_key: String,
    node_id: String,
    seq: u64,
    payload: EventPayload,
}

impl Ord for TimedEvent {
    fn cmp(&self, other: &Self) -> Ordering {
        self.time
            .cmp(&other.time)
            .then_with(|| self.kind_rank.cmp(&other.kind_rank))
            .then_with(|| self.scope_key.cmp(&other.scope_key))
            .then_with(|| self.node_id.cmp(&other.node_id))
            .then_with(|| self.seq.cmp(&other.seq))
    }
}

impl PartialOrd for TimedEvent {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

fn scope_for_path<'a>(root: &'a BpmnScope, path: &[String]) -> Option<&'a BpmnScope> {
    let mut cur = root;
    for seg in path {
        match &cur.nodes.get(seg)?.kind {
            BpmnNodeKind::SubProcess(child) => cur = child,
            _ => return None,
        }
    }
    Some(cur)
}

fn qualified_key(scope_path: &[String], node_id: &str) -> String {
    if scope_path.is_empty() {
        node_id.to_owned()
    } else {
        format!("{}/{node_id}", scope_path.join("/"))
    }
}

fn pop_earliest_event(queue: &mut Vec<TimedEvent>) -> Option<TimedEvent> {
    if queue.is_empty() {
        return None;
    }
    let mut best = 0usize;
    for i in 1..queue.len() {
        if queue[i] < queue[best] {
            best = i;
        }
    }
    Some(queue.swap_remove(best))
}

fn push_arrive(
    queue: &mut Vec<TimedEvent>,
    next_seq: &mut u64,
    time: ExactQty,
    scope_path: Vec<String>,
    node_id: String,
    incoming_flow_id: Option<String>,
) {
    let seq = *next_seq;
    *next_seq += 1;
    let scope_key = scope_path.join("/");
    queue.push(TimedEvent {
        time,
        kind_rank: 1,
        scope_key,
        node_id: node_id.clone(),
        seq,
        payload: EventPayload::Arrive {
            scope_path,
            node_id,
            incoming_flow_id,
        },
    });
}

/// Deterministically execute a validated BPMN model and emit an `ExecutionTrace`.
pub fn execute_bpmn(
    model: &BpmnModel,
    config: &BpmnExecutionConfig,
) -> Result<ExecutionTrace, ModelError> {
    if model.profile != config.profile {
        return Err(ModelError::new(
            ErrorCode::UnsupportedConstruct,
            "/profile",
            format!(
                "Model was validated under `{}`, config requested `{}`",
                model.profile.as_str(),
                config.profile.as_str()
            ),
        ));
    }

    let mut queue: Vec<TimedEvent> = Vec::new();
    let mut next_seq = 0u64;

    push_arrive(
        &mut queue,
        &mut next_seq,
        ExactQty::zero(),
        Vec::new(),
        model.process.start_event_id.clone(),
        None,
    );

    let mut decisions: BTreeMap<String, VecDeque<String>> = config
        .branch_decisions
        .iter()
        .map(|(k, v)| (k.clone(), VecDeque::from(v.clone())))
        .collect();
    let mut and_join_arrivals: BTreeMap<String, BTreeMap<String, ExactQty>> = BTreeMap::new();
    let mut visit_counts: BTreeMap<String, u64> = BTreeMap::new();
    let mut active_scope_tokens: BTreeMap<Vec<String>, usize> = BTreeMap::new();
    active_scope_tokens.insert(Vec::new(), 1);

    let mut steps = Vec::new();
    let mut usages = Vec::new();
    let mut last_time = ExactQty::zero();
    let mut handled_events = 0usize;
    let mut status = ExecutionStatus::Completed;

    while let Some(ev) = pop_earliest_event(&mut queue) {
        handled_events += 1;
        if handled_events > config.max_steps {
            return Err(ModelError::new(
                ErrorCode::StepLimitExceeded,
                "/max_steps",
                "BPMN execution exceeded configured max_steps",
            ));
        }
        if ev.time > last_time {
            last_time = ev.time;
        }

        match ev.payload {
            EventPayload::CompleteTask {
                scope_path,
                node_id,
                visit,
                start_time,
            } => {
                let scope = scope_for_path(&model.process, &scope_path).expect("valid scope");
                let node = &scope.nodes[&node_id];
                let qkey = qualified_key(&scope_path, &node_id);
                if let Some(recipe) = config
                    .recipes
                    .get(&qkey)
                    .or_else(|| config.recipes.get(&node_id))
                {
                    let step_id = if scope_path.is_empty() {
                        format!("bpmn:s{}:{}:{visit}", steps.len() + 1, node_id)
                    } else {
                        format!(
                            "bpmn:s{}:{}:{}:{visit}",
                            steps.len() + 1,
                            scope_path.join("."),
                            node_id
                        )
                    };
                    record_step_and_usages(
                        &mut steps,
                        &mut usages,
                        StepRecording {
                            step_id,
                            node_id: node_id.clone(),
                            subprocess_path: scope_path.clone(),
                            visit,
                            multiplicity: 1,
                            start_minute: start_time,
                            end_minute: ev.time,
                            recipe,
                            evidence_basis: config.evidence_basis,
                        },
                    )?;
                }
                let fid = &node.outgoing[0];
                let target = scope.flows[fid].target_ref.clone();
                push_arrive(
                    &mut queue,
                    &mut next_seq,
                    ev.time,
                    scope_path,
                    target,
                    Some(fid.clone()),
                );
            }
            EventPayload::Arrive {
                scope_path,
                node_id,
                incoming_flow_id,
            } => {
                let scope = scope_for_path(&model.process, &scope_path).expect("valid scope");
                let node = &scope.nodes[&node_id];
                let qkey = qualified_key(&scope_path, &node_id);
                let visit = visit_counts
                    .entry(qkey.clone())
                    .and_modify(|c| *c += 1)
                    .or_insert(1);
                let visit_num = *visit;
                if visit_num > config.max_node_visits {
                    return Err(ModelError::new(
                        ErrorCode::LoopBoundExceeded,
                        format!("/{qkey}"),
                        format!(
                            "Node `{qkey}` exceeded loop guard max_node_visits ({})",
                            config.max_node_visits
                        ),
                    ));
                }

                match &node.kind {
                    BpmnNodeKind::StartEvent => {
                        let fid = &node.outgoing[0];
                        let target = scope.flows[fid].target_ref.clone();
                        push_arrive(
                            &mut queue,
                            &mut next_seq,
                            ev.time,
                            scope_path,
                            target,
                            Some(fid.clone()),
                        );
                    }
                    BpmnNodeKind::Task { .. } => {
                        let duration = config
                            .recipes
                            .get(&qkey)
                            .or_else(|| config.recipes.get(&node_id))
                            .map_or_else(ExactQty::zero, |r| r.duration_minutes);
                        let end_time = ev
                            .time
                            .checked_add(duration, &format!("/{qkey}/duration_minutes"))?;
                        let seq = next_seq;
                        next_seq += 1;
                        queue.push(TimedEvent {
                            time: end_time,
                            kind_rank: 0,
                            scope_key: scope_path.join("/"),
                            node_id: node_id.clone(),
                            seq,
                            payload: EventPayload::CompleteTask {
                                scope_path,
                                node_id,
                                visit: visit_num,
                                start_time: ev.time,
                            },
                        });
                    }
                    BpmnNodeKind::ExclusiveGateway => {
                        let chosen_fid = if node.outgoing.len() == 1 {
                            node.outgoing[0].clone()
                        } else {
                            let decision_key = if decisions.contains_key(&qkey) {
                                &qkey
                            } else {
                                &node_id
                            };
                            let queue_for_gw = decisions.get_mut(decision_key).ok_or_else(|| {
                                ModelError::new(
                                    ErrorCode::MissingBranchDecision,
                                    format!("/branch_decisions/{qkey}"),
                                    format!(
                                        "Exclusive gateway `{qkey}` split requires explicit branch decision"
                                    ),
                                )
                            })?;
                            let fid = queue_for_gw.pop_front().ok_or_else(|| {
                                ModelError::new(
                                    ErrorCode::MissingBranchDecision,
                                    format!("/branch_decisions/{qkey}"),
                                    format!(
                                        "Exhausted branch decisions for exclusive gateway `{qkey}` at visit {visit_num}"
                                    ),
                                )
                            })?;
                            if !node.outgoing.contains(&fid) {
                                return Err(ModelError::new(
                                    ErrorCode::AmbiguousBranchDecision,
                                    format!("/branch_decisions/{qkey}"),
                                    format!(
                                        "Flow `{fid}` is not an outgoing sequenceFlow of `{qkey}`"
                                    ),
                                ));
                            }
                            fid
                        };
                        let target = scope.flows[&chosen_fid].target_ref.clone();
                        push_arrive(
                            &mut queue,
                            &mut next_seq,
                            ev.time,
                            scope_path,
                            target,
                            Some(chosen_fid),
                        );
                    }
                    BpmnNodeKind::ParallelGateway => {
                        let ready = if node.incoming.len() > 1 {
                            let flow_id = incoming_flow_id.ok_or_else(|| {
                                ModelError::new(
                                    ErrorCode::MalformedXml,
                                    &qkey,
                                    "Missing incoming edge at parallel join",
                                )
                            })?;
                            let slot = and_join_arrivals.entry(qkey.clone()).or_default();
                            if slot.contains_key(&flow_id) {
                                return Err(ModelError::new(
                                    ErrorCode::UnsupportedConstruct,
                                    &qkey,
                                    format!(
                                        "Parallel join `{qkey}` received overlapping arrival on flow `{flow_id}`"
                                    ),
                                ));
                            }
                            slot.insert(flow_id, ev.time);
                            if slot.len() < node.incoming.len() {
                                false
                            } else {
                                slot.clear();
                                true
                            }
                        } else {
                            true
                        };
                        if ready {
                            // Consume N incoming tokens -> emit M outgoing tokens in this scope.
                            let tok_count =
                                active_scope_tokens.get_mut(&scope_path).expect("scope");
                            *tok_count = (*tok_count + node.outgoing.len())
                                .saturating_sub(node.incoming.len().max(1));
                            for fid in &node.outgoing {
                                let target = scope.flows[fid].target_ref.clone();
                                push_arrive(
                                    &mut queue,
                                    &mut next_seq,
                                    ev.time,
                                    scope_path.clone(),
                                    target,
                                    Some(fid.clone()),
                                );
                            }
                        }
                    }
                    BpmnNodeKind::SubProcess(child_scope) => {
                        let mut child_path = scope_path.clone();
                        child_path.push(node_id);
                        active_scope_tokens.insert(child_path.clone(), 1);
                        push_arrive(
                            &mut queue,
                            &mut next_seq,
                            ev.time,
                            child_path,
                            child_scope.start_event_id.clone(),
                            None,
                        );
                    }
                    BpmnNodeKind::EndEvent => {
                        let remaining = active_scope_tokens.get_mut(&scope_path).expect("scope");
                        *remaining = remaining.saturating_sub(1);
                        if *remaining == 0 && !scope_path.is_empty() {
                            let mut parent_path = scope_path;
                            let sub_id = parent_path.pop().expect("non-empty sub path");
                            let parent_scope =
                                scope_for_path(&model.process, &parent_path).expect("parent");
                            let fid = &parent_scope.nodes[&sub_id].outgoing[0];
                            let target = parent_scope.flows[fid].target_ref.clone();
                            push_arrive(
                                &mut queue,
                                &mut next_seq,
                                ev.time,
                                parent_path,
                                target,
                                Some(fid.clone()),
                            );
                        }
                    }
                    BpmnNodeKind::TerminateEndEvent => {
                        status = ExecutionStatus::Cancelled {
                            cancelled_at_node: node_id,
                            reason: "bpmn_terminate_end_event".to_owned(),
                        };
                        queue.clear();
                        break;
                    }
                }
            }
        }
    }

    Ok(ExecutionTrace {
        contract_version: CONTRACT_VERSION.to_owned(),
        profile_id: model.profile.as_str().to_owned(),
        model_sha256: model.model_sha256.clone(),
        process_id: config.process_id.clone(),
        model_id: config.model_id.clone(),
        model_version: config.model_version.clone(),
        evidence_basis: config.evidence_basis,
        status,
        initial_marking: None,
        final_marking: None,
        total_elapsed_minutes: last_time,
        objects: config.objects.clone(),
        object_relations: config.object_relations.clone(),
        steps,
        usages,
    })
}
