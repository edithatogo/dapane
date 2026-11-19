//! Shared process-model contracts, exact rational arithmetic, execution traces,
//! and strict projection into Dapane `0.1` valuation requests.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt;

use crate::json_io::{JsonValue, reject_unknown_keys, req_field};

/// Contract identity for the X2 PNML and BPMN adapters.
pub const CONTRACT_VERSION: &str = "dapane-process-models-v0.1.0";
/// Maximum total execution steps or generated usages in one bounded run.
pub const MAX_EXECUTION_RECORDS: usize = 2_000;

/// Stable machine-readable rejection code.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ErrorCode {
    /// Input XML or JSON exceeds documented size, depth, or element bounds.
    SizeLimitExceeded,
    /// Disallowed XML construct (DOCTYPE, ENTITY, CDATA, or non-`<?xml` PI).
    DisallowedXmlConstruct,
    /// Syntactically invalid or non-UTF-8 XML.
    MalformedXml,
    /// Syntactically invalid, duplicate-key, or schema-invalid JSON configuration.
    MalformedJson,
    /// Unexpected root element or XML namespace URI.
    UnsupportedModelNamespace,
    /// PNML `<net type=...>` is not P/T net.
    UnsupportedNetType,
    /// Construct outside the selected profile subset (e.g. inhibitor arc, timer, inclusive gateway).
    UnsupportedConstruct,
    /// Cycle detected in the acyclic core BPMN profile (`bpmn-core-acyclic-v1`).
    CycleNotAllowedInCoreProfile,
    /// Duplicate identifier across objects, nodes, arcs, flows, steps, or uses.
    DuplicateIdentity,
    /// Invalid or empty identifier/token.
    InvalidToken,
    /// Arc, sequence flow, gateway branch, or object edge references a missing ID.
    DanglingReference,
    /// Invalid place initial/final marking or marking constraint.
    InvalidMarking,
    /// Invalid arc weight, firing multiplicity, or duration/step bound.
    InvalidWeight,
    /// Petri-net transition is not enabled by the current marking.
    NotEnabled,
    /// Petri-net run completed without reaching the declared expected final marking.
    FinalMarkingMismatch,
    /// Execution exceeded the configured `max_steps` limit.
    StepLimitExceeded,
    /// Extended BPMN rework loop exceeded `max_node_visits`.
    LoopBoundExceeded,
    /// Exclusive gateway split lacked a caller-supplied branch decision.
    MissingBranchDecision,
    /// Caller branch decision referenced an unknown or non-outgoing flow.
    AmbiguousBranchDecision,
    /// Exact rational calculation overflowed `u128` limits.
    ArithmeticOverflow,
    /// Malformed or negative exact quantity.
    InvalidQuantity,
    /// Quotation release or allocation mapping does not match trace targets/units/attribution.
    ValuationMismatch,
}

impl ErrorCode {
    /// Return canonical snake_case code string.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::SizeLimitExceeded => "size_limit_exceeded",
            Self::DisallowedXmlConstruct => "disallowed_xml_construct",
            Self::MalformedXml => "malformed_xml",
            Self::MalformedJson => "malformed_json",
            Self::UnsupportedModelNamespace => "unsupported_model_namespace",
            Self::UnsupportedNetType => "unsupported_net_type",
            Self::UnsupportedConstruct => "unsupported_construct",
            Self::CycleNotAllowedInCoreProfile => "cycle_not_allowed_in_core_profile",
            Self::DuplicateIdentity => "duplicate_identity",
            Self::InvalidToken => "invalid_token",
            Self::DanglingReference => "dangling_reference",
            Self::InvalidMarking => "invalid_marking",
            Self::InvalidWeight => "invalid_weight",
            Self::NotEnabled => "not_enabled",
            Self::FinalMarkingMismatch => "final_marking_mismatch",
            Self::StepLimitExceeded => "step_limit_exceeded",
            Self::LoopBoundExceeded => "loop_bound_exceeded",
            Self::MissingBranchDecision => "missing_branch_decision",
            Self::AmbiguousBranchDecision => "ambiguous_branch_decision",
            Self::ArithmeticOverflow => "arithmetic_overflow",
            Self::InvalidQuantity => "invalid_quantity",
            Self::ValuationMismatch => "valuation_mismatch",
        }
    }
}

/// Structured adapter failure carrying a machine code, path, and diagnostic message.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ModelError {
    /// Machine-readable rejection category.
    pub code: ErrorCode,
    /// Pointer-style location inside input XML/JSON or execution trace.
    pub path: String,
    /// Human-readable explanation.
    pub message: String,
}

impl ModelError {
    /// Construct a new structured error.
    pub fn new(code: ErrorCode, path: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            code,
            path: path.into(),
            message: message.into(),
        }
    }

    /// Encode the error as structured JSON.
    pub fn to_json(&self) -> JsonValue {
        let mut obj = BTreeMap::new();
        obj.insert(
            "code".to_owned(),
            JsonValue::String(self.code.as_str().to_owned()),
        );
        obj.insert(
            "contract_version".to_owned(),
            JsonValue::String(CONTRACT_VERSION.to_owned()),
        );
        obj.insert(
            "message".to_owned(),
            JsonValue::String(self.message.clone()),
        );
        obj.insert("path".to_owned(), JsonValue::String(self.path.clone()));
        JsonValue::Object(obj)
    }
}

impl fmt::Display for ModelError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{} at {}: {}",
            self.code.as_str(),
            self.path,
            self.message
        )
    }
}

impl std::error::Error for ModelError {}

/// Validate a Dapane `0.1`-compatible token (`1..=128` UTF-8 bytes, trimmed, no control chars).
pub fn validate_token(value: &str, path: &str) -> Result<(), ModelError> {
    if value.is_empty() || value.len() > 128 {
        return Err(ModelError::new(
            ErrorCode::InvalidToken,
            path,
            "Token length must be between 1 and 128 UTF-8 bytes",
        ));
    }
    let trimmed = value.trim();
    if trimmed != value {
        return Err(ModelError::new(
            ErrorCode::InvalidToken,
            path,
            "Token must not have surrounding whitespace",
        ));
    }
    if value
        .chars()
        .any(|c| (c as u32) <= 0x1F || matches!(c as u32, 0x7F..=0x9F))
    {
        return Err(ModelError::new(
            ErrorCode::InvalidToken,
            path,
            "Token must not contain control characters",
        ));
    }
    Ok(())
}

/// Validate `YYYY-MM-DD` calendar date spelling (matching Dapane schema `date`).
pub fn validate_date(value: &str, path: &str) -> Result<(), ModelError> {
    let bytes = value.as_bytes();
    if bytes.len() != 10
        || bytes[4] != b'-'
        || bytes[7] != b'-'
        || !bytes[..4].iter().all(u8::is_ascii_digit)
        || !bytes[5..7].iter().all(u8::is_ascii_digit)
        || !bytes[8..10].iter().all(u8::is_ascii_digit)
    {
        return Err(ModelError::new(
            ErrorCode::MalformedJson,
            path,
            "Expected YYYY-MM-DD date string",
        ));
    }
    let year: u16 = value[..4].parse().unwrap_or(0);
    let month: u8 = value[5..7].parse().unwrap_or(0);
    let day: u8 = value[8..10].parse().unwrap_or(0);
    if year == 0 || !(1..=12).contains(&month) || !(1..=31).contains(&day) {
        return Err(ModelError::new(
            ErrorCode::MalformedJson,
            path,
            "Calendar date components out of range",
        ));
    }
    let max_day = match month {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 => {
            let leap =
                (year.is_multiple_of(4) && !year.is_multiple_of(100)) || year.is_multiple_of(400);
            if leap { 29 } else { 28 }
        }
        _ => 0,
    };
    if day > max_day {
        return Err(ModelError::new(
            ErrorCode::MalformedJson,
            path,
            "Calendar day invalid for month/year",
        ));
    }
    Ok(())
}

/// Nonnegative reduced exact rational quantity (`numerator / denominator`, `denominator >= 1`).
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct ExactQty {
    /// Nonnegative reduced numerator.
    pub numerator: u128,
    /// Strictly positive reduced denominator.
    pub denominator: u128,
}

fn gcd(mut a: u128, mut b: u128) -> u128 {
    while b != 0 {
        let r = a % b;
        a = b;
        b = r;
    }
    if a == 0 { 1 } else { a }
}

impl ExactQty {
    /// Zero quantity (`0/1`).
    pub fn zero() -> Self {
        Self {
            numerator: 0,
            denominator: 1,
        }
    }

    /// Whole integer quantity (`n/1`).
    pub fn from_u64(n: u64) -> Self {
        Self {
            numerator: u128::from(n),
            denominator: 1,
        }
    }

    /// Construct and reduce `numerator / denominator`, rejecting zero denominators.
    pub fn new(numerator: u128, denominator: u128, path: &str) -> Result<Self, ModelError> {
        if denominator == 0 {
            return Err(ModelError::new(
                ErrorCode::InvalidQuantity,
                path,
                "Denominator cannot be zero",
            ));
        }
        if numerator == 0 {
            return Ok(Self::zero());
        }
        let d = gcd(numerator, denominator);
        Ok(Self {
            numerator: numerator / d,
            denominator: denominator / d,
        })
    }

    /// Parse unsigned exact decimal (`"5"`, `"2.5"`) or rational (`"1/3"`) text.
    pub fn parse(raw: &str, path: &str) -> Result<Self, ModelError> {
        if raw.is_empty() || raw.len() > 97 {
            return Err(ModelError::new(
                ErrorCode::InvalidQuantity,
                path,
                "Quantity string must be non-empty and bounded",
            ));
        }
        if let Some((num_s, den_s)) = raw.split_once('/') {
            if num_s.is_empty()
                || den_s.is_empty()
                || !num_s.bytes().all(|b| b.is_ascii_digit())
                || !den_s.bytes().all(|b| b.is_ascii_digit())
            {
                return Err(ModelError::new(
                    ErrorCode::InvalidQuantity,
                    path,
                    "Rational quantity must use unsigned digits `num/den`",
                ));
            }
            let num = num_s.parse::<u128>().map_err(|_| {
                ModelError::new(ErrorCode::ArithmeticOverflow, path, "Numerator overflow")
            })?;
            let den = den_s.parse::<u128>().map_err(|_| {
                ModelError::new(ErrorCode::ArithmeticOverflow, path, "Denominator overflow")
            })?;
            return Self::new(num, den, path);
        }
        if let Some((int_s, frac_s)) = raw.split_once('.') {
            if int_s.is_empty()
                || frac_s.is_empty()
                || frac_s.len() > 18
                || !int_s.bytes().all(|b| b.is_ascii_digit())
                || !frac_s.bytes().all(|b| b.is_ascii_digit())
            {
                return Err(ModelError::new(
                    ErrorCode::InvalidQuantity,
                    path,
                    "Decimal quantity must be unsigned with 1..=18 fractional digits",
                ));
            }
            let scale = 10u128.pow(frac_s.len() as u32);
            let whole = int_s.parse::<u128>().map_err(|_| {
                ModelError::new(ErrorCode::ArithmeticOverflow, path, "Integer overflow")
            })?;
            let frac = frac_s.parse::<u128>().map_err(|_| {
                ModelError::new(ErrorCode::ArithmeticOverflow, path, "Fraction overflow")
            })?;
            let num = whole
                .checked_mul(scale)
                .and_then(|v| v.checked_add(frac))
                .ok_or_else(|| {
                    ModelError::new(ErrorCode::ArithmeticOverflow, path, "Decimal overflow")
                })?;
            return Self::new(num, scale, path);
        }
        if !raw.bytes().all(|b| b.is_ascii_digit()) {
            return Err(ModelError::new(
                ErrorCode::InvalidQuantity,
                path,
                "Quantity must be unsigned decimal or fraction",
            ));
        }
        let num = raw.parse::<u128>().map_err(|_| {
            ModelError::new(ErrorCode::ArithmeticOverflow, path, "Quantity overflow")
        })?;
        Ok(Self {
            numerator: num,
            denominator: 1,
        })
    }

    /// Checked rational addition.
    pub fn checked_add(self, rhs: Self, path: &str) -> Result<Self, ModelError> {
        let g = gcd(self.denominator, rhs.denominator);
        let lhs_factor = rhs.denominator / g;
        let rhs_factor = self.denominator / g;
        let left = self.numerator.checked_mul(lhs_factor).ok_or_else(|| {
            ModelError::new(ErrorCode::ArithmeticOverflow, path, "Addition overflow")
        })?;
        let right = rhs.numerator.checked_mul(rhs_factor).ok_or_else(|| {
            ModelError::new(ErrorCode::ArithmeticOverflow, path, "Addition overflow")
        })?;
        let num = left.checked_add(right).ok_or_else(|| {
            ModelError::new(ErrorCode::ArithmeticOverflow, path, "Addition overflow")
        })?;
        let den = self.denominator.checked_mul(lhs_factor).ok_or_else(|| {
            ModelError::new(ErrorCode::ArithmeticOverflow, path, "Denominator overflow")
        })?;
        Self::new(num, den, path)
    }

    /// Checked rational multiplication.
    pub fn checked_mul(self, rhs: Self, path: &str) -> Result<Self, ModelError> {
        let g1 = gcd(self.numerator, rhs.denominator);
        let g2 = gcd(rhs.numerator, self.denominator);
        let num = (self.numerator / g1)
            .checked_mul(rhs.numerator / g2)
            .ok_or_else(|| {
                ModelError::new(ErrorCode::ArithmeticOverflow, path, "Multiply overflow")
            })?;
        let den = (self.denominator / g2)
            .checked_mul(rhs.denominator / g1)
            .ok_or_else(|| {
                ModelError::new(ErrorCode::ArithmeticOverflow, path, "Multiply overflow")
            })?;
        Self::new(num, den, path)
    }

    /// Format as an exact terminating decimal string if denominator only has factors `2` and `5`.
    pub fn as_decimal_string(&self) -> Option<String> {
        if self.numerator == 0 {
            return Some("0".to_owned());
        }
        if self.denominator == 1 {
            return Some(self.numerator.to_string());
        }
        let mut d = self.denominator;
        let mut twos = 0u32;
        let mut fives = 0u32;
        while d.is_multiple_of(2) {
            d /= 2;
            twos += 1;
        }
        while d.is_multiple_of(5) {
            d /= 5;
            fives += 1;
        }
        if d != 1 {
            return None;
        }
        let frac_digits = twos.max(fives);
        if frac_digits > 18 {
            return None;
        }
        let mut num = self.numerator;
        for _ in 0..(frac_digits - twos) {
            num = num.checked_mul(2)?;
        }
        for _ in 0..(frac_digits - fives) {
            num = num.checked_mul(5)?;
        }
        let scale = 10u128.pow(frac_digits);
        let whole = num / scale;
        let frac = num % scale;
        if frac == 0 {
            Some(whole.to_string())
        } else {
            let padded = format!("{frac:0width$}", width = frac_digits as usize);
            let trimmed = padded.trim_end_matches('0');
            Some(format!("{whole}.{trimmed}"))
        }
    }

    /// Encode in strict Dapane `0.1` `exactNumber` JSON format (decimal string or `{numerator, denominator}`).
    pub fn to_dapane_json(&self) -> JsonValue {
        if let Some(dec) = self.as_decimal_string() {
            JsonValue::String(dec)
        } else {
            let mut obj = BTreeMap::new();
            obj.insert(
                "denominator".to_owned(),
                JsonValue::String(self.denominator.to_string()),
            );
            obj.insert(
                "numerator".to_owned(),
                JsonValue::String(self.numerator.to_string()),
            );
            JsonValue::Object(obj)
        }
    }

    /// Encode trace exact rational as `{numerator, denominator, display}`.
    pub fn to_trace_json(&self) -> JsonValue {
        let mut obj = BTreeMap::new();
        obj.insert(
            "denominator".to_owned(),
            JsonValue::String(self.denominator.to_string()),
        );
        obj.insert("display".to_owned(), JsonValue::String(self.to_string()));
        obj.insert(
            "numerator".to_owned(),
            JsonValue::String(self.numerator.to_string()),
        );
        JsonValue::Object(obj)
    }

    /// Parse exact rational from a trace JSON object or string.
    pub fn from_json(value: &JsonValue, path: &str) -> Result<Self, ModelError> {
        match value {
            JsonValue::String(s) => Self::parse(s, path),
            JsonValue::Object(obj) => {
                let num_s =
                    req_field(obj, "numerator", path)?.as_str(&format!("{path}/numerator"))?;
                let den_s =
                    req_field(obj, "denominator", path)?.as_str(&format!("{path}/denominator"))?;
                let num = num_s.parse::<u128>().map_err(|_| {
                    ModelError::new(ErrorCode::InvalidQuantity, path, "Invalid numerator")
                })?;
                let den = den_s.parse::<u128>().map_err(|_| {
                    ModelError::new(ErrorCode::InvalidQuantity, path, "Invalid denominator")
                })?;
                Self::new(num, den, path)
            }
            _ => Err(ModelError::new(
                ErrorCode::InvalidQuantity,
                path,
                "Expected exact number string or {numerator, denominator}",
            )),
        }
    }
}

impl fmt::Display for ExactQty {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if let Some(dec) = self.as_decimal_string() {
            f.write_str(&dec)
        } else {
            write!(f, "{}/{}", self.numerator, self.denominator)
        }
    }
}

/// Economic nature of a step's resource line (AC 3).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ResourceKind {
    /// Physical consumable used up during activity execution (`costable = true`).
    Consumption,
    /// Shared or dedicated resource occupied across interval duration (`costable = true`).
    Occupancy,
    /// Physical movement or custody handover; never directly chargeable (`costable = false`).
    Transfer,
}

impl ResourceKind {
    /// Return canonical string representation.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Consumption => "consumption",
            Self::Occupancy => "occupancy",
            Self::Transfer => "transfer",
        }
    }

    /// Parse resource kind strictly.
    pub fn parse(raw: &str, path: &str) -> Result<Self, ModelError> {
        match raw {
            "consumption" => Ok(Self::Consumption),
            "occupancy" => Ok(Self::Occupancy),
            "transfer" => Ok(Self::Transfer),
            _ => Err(ModelError::new(
                ErrorCode::MalformedJson,
                path,
                "Expected resource_kind `consumption`, `occupancy`, or `transfer`",
            )),
        }
    }

    /// Only consumption and occupancy produce chargeable Dapane `0.1` usage lines.
    pub fn is_costable(self) -> bool {
        !matches!(self, Self::Transfer)
    }
}

/// Epistemic basis of a process-model resource record (distinct from observed logs).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EvidenceBasis {
    /// Parameterized recipe assumption attached to a model activity.
    Assumed,
    /// Output emitted by a deterministic process-model simulation run.
    Simulated,
}

impl EvidenceBasis {
    /// Return canonical string representation.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Assumed => "assumed",
            Self::Simulated => "simulated",
        }
    }

    /// Parse `assumed` or `simulated` strictly (rejecting `observed` on executed models).
    pub fn parse(raw: &str, path: &str) -> Result<Self, ModelError> {
        match raw {
            "assumed" => Ok(Self::Assumed),
            "simulated" => Ok(Self::Simulated),
            _ => Err(ModelError::new(
                ErrorCode::MalformedJson,
                path,
                "Process execution basis must be `assumed` or `simulated`",
            )),
        }
    }
}

/// How an activity's resource quantity scales across firing multiplicity and shared batches.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BatchMode {
    /// Emits `quantity * multiplicity` when executed, permitting direct attribution.
    PerFiring,
    /// Emits ONE shared batch line per step (quantity unmultiplied by participant count; no direct attribution).
    SingleSharedBatch {
        /// Shared batch `CostObject` identifier included in `object_ids`.
        batch_object_id: String,
    },
}

/// Declared `CostObject` carried from process config into Dapane requests.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CostObjectDef {
    /// Unique object ID.
    pub id: String,
    /// Object kind (e.g. `infant`, `specimen`, `assay_batch`).
    pub kind: String,
}

/// Declared `ObjectRelation` carried from process config into Dapane requests.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ObjectRelationDef {
    /// Source object ID.
    pub from_object_id: String,
    /// Target object ID.
    pub to_object_id: String,
    /// Relationship label.
    pub relationship: String,
}

/// Resource consumption/occupancy/transfer rule attached to an executed model activity.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ResourceSpec {
    /// Resource target (matches Dapane `Quote.target`).
    pub target: String,
    /// Measurement unit (matches Dapane `Quote.unit`).
    pub unit: String,
    /// Base exact physical quantity for one step (or per firing in `PerFiring` mode).
    pub quantity: ExactQty,
    /// Whether this record is consumption, occupancy, or a non-costable transfer.
    pub resource_kind: ResourceKind,
    /// Scaling and batch-sharing rule.
    pub batch_mode: BatchMode,
    /// Optional single direct `attribution_object_id` (disallowed for `SingleSharedBatch`).
    pub attribution_object_id: Option<String>,
    /// Context `object_ids` bound to this resource line.
    pub object_ids: Vec<String>,
}

/// Activity recipe mapped from a PNML transition ID or BPMN node ID.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ActivityRecipe {
    /// Stable logical activity ID preserved on emitted Dapane events and usages.
    pub activity_id: String,
    /// Exact elapsed duration in minutes added by executing this node/transition once.
    pub duration_minutes: ExactQty,
    /// Context `object_ids` associated with this activity's event.
    pub object_ids: Vec<String>,
    /// Ordered resource lines generated when this activity completes.
    pub resources: Vec<ResourceSpec>,
}

/// Completion state of a process execution trace.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ExecutionStatus {
    /// Process reached completion cleanly (and matched any expected PNML final marking).
    Completed,
    /// Process stopped due to an explicit cancellation point or BPMN terminate end event.
    Cancelled {
        /// Node or transition ID where cancellation occurred.
        cancelled_at_node: String,
        /// Caller-supplied or model reason for cancellation.
        reason: String,
    },
}

/// One committed step in an `ExecutionTrace`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ExecutionStep {
    /// Unique deterministic step identifier.
    pub step_id: String,
    /// Unique event identifier emitted into Dapane `events`.
    pub event_id: String,
    /// Executed model element ID (PNML transition ID or BPMN node ID).
    pub node_id: String,
    /// Logical activity ID.
    pub activity_id: String,
    /// Enclosing subprocess path (empty for top-level PNML transitions or top-level BPMN nodes).
    pub subprocess_path: Vec<String>,
    /// 1-based execution visit counter for this `(subprocess_path, node_id)`.
    pub visit: u64,
    /// Integer firing multiplicity (always `1` for BPMN token steps; `>= 1` for PNML transitions).
    pub multiplicity: u64,
    /// Exact start instant relative to process t=0 in minutes.
    pub start_minute: ExactQty,
    /// Exact completion instant relative to process t=0 in minutes.
    pub end_minute: ExactQty,
    /// Context object IDs associated with this step's event.
    pub object_ids: Vec<String>,
}

/// One physical resource-use or transfer record emitted by an executed step.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EmittedUsage {
    /// Deterministic physical use identifier preserved across quotation changes.
    pub use_id: String,
    /// Step ID that emitted this record.
    pub step_id: String,
    /// Event ID associated with this record.
    pub event_id: String,
    /// Logical activity ID.
    pub activity_id: String,
    /// Consumption, occupancy, or transfer classification.
    pub resource_kind: ResourceKind,
    /// Whether this record enters Dapane `0.1` valuation (`false` for `Transfer`).
    pub costable: bool,
    /// Epistemic basis (`assumed` or `simulated`).
    pub evidence_basis: EvidenceBasis,
    /// Resource target.
    pub target: String,
    /// Resource unit.
    pub unit: String,
    /// Exact physical quantity.
    pub quantity: ExactQty,
    /// Optional direct object attribution (`None` for shared batch pools or transfers).
    pub attribution_object_id: Option<String>,
    /// Context object IDs attached to this record.
    pub object_ids: Vec<String>,
}

/// Self-contained physical execution trace emitted by `execute-pnml` or `execute-bpmn`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ExecutionTrace {
    /// Adapter contract version.
    pub contract_version: String,
    /// Bounded execution profile identifier (`pnml-bounded-v1`, `bpmn-core-acyclic-v1`, etc.).
    pub profile_id: String,
    /// Exact `sha256:<64-hex>` of the executed XML model bytes.
    pub model_sha256: String,
    /// Process instance identifier.
    pub process_id: String,
    /// Model identifier.
    pub model_id: String,
    /// Model revision string.
    pub model_version: String,
    /// Default evidence basis for emitted usage records.
    pub evidence_basis: EvidenceBasis,
    /// Completion or cancellation status.
    pub status: ExecutionStatus,
    /// Optional PNML initial marking snapshot (`place_id -> count`).
    pub initial_marking: Option<BTreeMap<String, u64>>,
    /// Optional PNML final marking snapshot (`place_id -> count`).
    pub final_marking: Option<BTreeMap<String, u64>>,
    /// Total process makespan / elapsed time until completion or cancellation, in minutes.
    pub total_elapsed_minutes: ExactQty,
    /// Declared `CostObject`s carried forward from model config.
    pub objects: Vec<CostObjectDef>,
    /// Declared object relationships carried forward from model config.
    pub object_relations: Vec<ObjectRelationDef>,
    /// Ordered committed steps.
    pub steps: Vec<ExecutionStep>,
    /// Ordered emitted usage and transfer records (no prices or currency fields).
    pub usages: Vec<EmittedUsage>,
}

/// Optional shared-cost allocation rule attached during `project-dapane`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AllocationRule {
    /// Dapane `0.1` allocation identifier.
    pub id: String,
    /// Target name selector matching emitted costable usage lines.
    pub match_target: String,
    /// Optional activity ID filter (`None` matches any activity with `match_target`).
    pub match_activity_id: Option<String>,
    /// Pairs of `(object_id, weight)` passed directly to Dapane `0.1` allocations.
    pub weights: Vec<(String, ExactQty)>,
}

/// Downstream quotation release & valuation policy attached separately from process execution.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValuationAttachment {
    /// Dapane `0.1` run identifier.
    pub run_id: String,
    /// `YYYY-MM-DD` knowledge cutoff date.
    pub knowledge_cutoff: String,
    /// `YYYY-MM-DD` service date attached to events and usage lines.
    pub service_date: String,
    /// Dapane `0.1` source evidence tag (`synthetic` or `derived`; never `observed`).
    pub source_evidence: String,
    /// Dapane `0.1` source access tag (`public`, `restricted`, or `private`).
    pub source_access: String,
    /// Dapane `0.1` source validation tag (`unvalidated`, `source_verified`, `empirically_validated`).
    pub source_validation: String,
    /// Optional source locator string.
    pub source_locator: Option<String>,
    /// Raw Dapane `0.1` `policy` JSON object (passed straight to Rust kernel after validation).
    pub policy: JsonValue,
    /// Mapping from resource `target` -> `quote_id`.
    pub quote_bindings: BTreeMap<String, String>,
    /// Full Dapane `0.1` `quotes` array (validated to be non-empty JSON objects).
    pub quotes: Vec<JsonValue>,
    /// Optional pooled allocations to attach to emitted non-attributed costable lines.
    pub allocations: Vec<AllocationRule>,
}

/// Parsed `(objects, object_ids, object_relations)` triple returned by object config parsing.
pub type ParsedObjects = (Vec<CostObjectDef>, BTreeSet<String>, Vec<ObjectRelationDef>);

/// Parse declared `objects` and `object_relations`, returning `(objects, object_id_set, relations)`.
pub fn parse_objects_and_relations(
    cfg: &BTreeMap<String, JsonValue>,
    path: &str,
) -> Result<ParsedObjects, ModelError> {
    let mut objects = Vec::new();
    let mut object_ids = BTreeSet::new();
    if let Some(raw_objs) = cfg.get("objects") {
        let items = raw_objs.as_array(&format!("{path}/objects"))?;
        for (idx, item) in items.iter().enumerate() {
            let p = format!("{path}/objects/{idx}");
            let obj = item.as_object(&p)?;
            reject_unknown_keys(obj, &["id", "kind"], &p)?;
            let id = req_field(obj, "id", &p)?
                .as_str(&format!("{p}/id"))?
                .to_owned();
            let kind = req_field(obj, "kind", &p)?
                .as_str(&format!("{p}/kind"))?
                .to_owned();
            validate_token(&id, &format!("{p}/id"))?;
            validate_token(&kind, &format!("{p}/kind"))?;
            if !object_ids.insert(id.clone()) {
                return Err(ModelError::new(
                    ErrorCode::DuplicateIdentity,
                    format!("{p}/id"),
                    format!("Duplicate CostObject `{id}`"),
                ));
            }
            objects.push(CostObjectDef { id, kind });
        }
    }

    let mut relations = Vec::new();
    let mut seen_rel = BTreeSet::new();
    if let Some(raw_rels) = cfg.get("object_relations") {
        let items = raw_rels.as_array(&format!("{path}/object_relations"))?;
        for (idx, item) in items.iter().enumerate() {
            let p = format!("{path}/object_relations/{idx}");
            let obj = item.as_object(&p)?;
            reject_unknown_keys(obj, &["from_object_id", "relationship", "to_object_id"], &p)?;
            let from = req_field(obj, "from_object_id", &p)?
                .as_str(&format!("{p}/from_object_id"))?
                .to_owned();
            let to = req_field(obj, "to_object_id", &p)?
                .as_str(&format!("{p}/to_object_id"))?
                .to_owned();
            let rel = req_field(obj, "relationship", &p)?
                .as_str(&format!("{p}/relationship"))?
                .to_owned();
            validate_token(&rel, &format!("{p}/relationship"))?;
            if !object_ids.contains(&from) {
                return Err(ModelError::new(
                    ErrorCode::DanglingReference,
                    format!("{p}/from_object_id"),
                    format!("Unknown object `{from}`"),
                ));
            }
            if !object_ids.contains(&to) {
                return Err(ModelError::new(
                    ErrorCode::DanglingReference,
                    format!("{p}/to_object_id"),
                    format!("Unknown object `{to}`"),
                ));
            }
            if !seen_rel.insert((from.clone(), to.clone(), rel.clone())) {
                return Err(ModelError::new(
                    ErrorCode::DuplicateIdentity,
                    &p,
                    "Duplicate object relation",
                ));
            }
            relations.push(ObjectRelationDef {
                from_object_id: from,
                to_object_id: to,
                relationship: rel,
            });
        }
    }
    Ok((objects, object_ids, relations))
}

fn parse_string_list_refs(
    raw: Option<&JsonValue>,
    known_objects: &BTreeSet<String>,
    path: &str,
) -> Result<Vec<String>, ModelError> {
    let Some(val) = raw else {
        return Ok(Vec::new());
    };
    let arr = val.as_array(path)?;
    let mut out = Vec::with_capacity(arr.len());
    let mut seen = BTreeSet::new();
    for (idx, item) in arr.iter().enumerate() {
        let p = format!("{path}/{idx}");
        let id = item.as_str(&p)?.to_owned();
        if !known_objects.contains(&id) {
            return Err(ModelError::new(
                ErrorCode::DanglingReference,
                &p,
                format!("Unknown object `{id}`"),
            ));
        }
        if !seen.insert(id.clone()) {
            return Err(ModelError::new(
                ErrorCode::DuplicateIdentity,
                &p,
                format!("Repeated object ID `{id}`"),
            ));
        }
        out.push(id);
    }
    Ok(out)
}

/// Parse `recipes` map `{ node_or_transition_id -> ActivityRecipe }`.
pub fn parse_recipes_map(
    raw: &JsonValue,
    known_objects: &BTreeSet<String>,
    path: &str,
) -> Result<BTreeMap<String, ActivityRecipe>, ModelError> {
    let map = raw.as_object(path)?;
    let mut recipes = BTreeMap::new();
    for (node_id, val) in map {
        let p = format!("{path}/{node_id}");
        let obj = val.as_object(&p)?;
        reject_unknown_keys(
            obj,
            &["activity_id", "duration_minutes", "object_ids", "resources"],
            &p,
        )?;
        let activity_id = req_field(obj, "activity_id", &p)?
            .as_str(&format!("{p}/activity_id"))?
            .to_owned();
        validate_token(&activity_id, &format!("{p}/activity_id"))?;
        let duration_minutes = match obj.get("duration_minutes") {
            Some(JsonValue::String(s)) => ExactQty::parse(s, &format!("{p}/duration_minutes"))?,
            Some(_) => {
                return Err(ModelError::new(
                    ErrorCode::InvalidQuantity,
                    format!("{p}/duration_minutes"),
                    "duration_minutes must be an exact decimal/fraction string",
                ));
            }
            None => ExactQty::zero(),
        };
        let step_objects = parse_string_list_refs(
            obj.get("object_ids"),
            known_objects,
            &format!("{p}/object_ids"),
        )?;

        let mut resources = Vec::new();
        if let Some(raw_res) = obj.get("resources") {
            let items = raw_res.as_array(&format!("{p}/resources"))?;
            for (idx, item) in items.iter().enumerate() {
                let rp = format!("{p}/resources/{idx}");
                let robj = item.as_object(&rp)?;
                reject_unknown_keys(
                    robj,
                    &[
                        "attribution_object_id",
                        "batch_mode",
                        "batch_object_id",
                        "object_ids",
                        "quantity",
                        "resource_kind",
                        "target",
                        "unit",
                    ],
                    &rp,
                )?;
                let target = req_field(robj, "target", &rp)?
                    .as_str(&format!("{rp}/target"))?
                    .to_owned();
                let unit = req_field(robj, "unit", &rp)?
                    .as_str(&format!("{rp}/unit"))?
                    .to_owned();
                validate_token(&target, &format!("{rp}/target"))?;
                validate_token(&unit, &format!("{rp}/unit"))?;
                let qty_raw =
                    req_field(robj, "quantity", &rp)?.as_str(&format!("{rp}/quantity"))?;
                let quantity = ExactQty::parse(qty_raw, &format!("{rp}/quantity"))?;
                let kind_raw = req_field(robj, "resource_kind", &rp)?
                    .as_str(&format!("{rp}/resource_kind"))?;
                let resource_kind = ResourceKind::parse(kind_raw, &format!("{rp}/resource_kind"))?;

                let batch_mode = match robj
                    .get("batch_mode")
                    .map(|v| v.as_str(&format!("{rp}/batch_mode")))
                    .transpose()?
                {
                    None | Some("per_firing") => {
                        if robj.contains_key("batch_object_id") {
                            return Err(ModelError::new(
                                ErrorCode::MalformedJson,
                                format!("{rp}/batch_object_id"),
                                "batch_object_id is only valid with batch_mode `single_shared_batch`",
                            ));
                        }
                        BatchMode::PerFiring
                    }
                    Some("single_shared_batch") => {
                        let batch_obj = req_field(robj, "batch_object_id", &rp)?
                            .as_str(&format!("{rp}/batch_object_id"))?
                            .to_owned();
                        if !known_objects.contains(&batch_obj) {
                            return Err(ModelError::new(
                                ErrorCode::DanglingReference,
                                format!("{rp}/batch_object_id"),
                                format!("Unknown batch object `{batch_obj}`"),
                            ));
                        }
                        BatchMode::SingleSharedBatch {
                            batch_object_id: batch_obj,
                        }
                    }
                    Some(other) => {
                        return Err(ModelError::new(
                            ErrorCode::MalformedJson,
                            format!("{rp}/batch_mode"),
                            format!("Unsupported batch_mode `{other}`"),
                        ));
                    }
                };

                let attribution_object_id = match robj.get("attribution_object_id") {
                    None | Some(JsonValue::Null) => None,
                    Some(v) => {
                        let id = v.as_str(&format!("{rp}/attribution_object_id"))?.to_owned();
                        if !known_objects.contains(&id) {
                            return Err(ModelError::new(
                                ErrorCode::DanglingReference,
                                format!("{rp}/attribution_object_id"),
                                format!("Unknown object `{id}`"),
                            ));
                        }
                        Some(id)
                    }
                };
                if matches!(batch_mode, BatchMode::SingleSharedBatch { .. })
                    && attribution_object_id.is_some()
                {
                    return Err(ModelError::new(
                        ErrorCode::ValuationMismatch,
                        format!("{rp}/attribution_object_id"),
                        "Shared batch resource cannot also specify direct attribution_object_id",
                    ));
                }
                if !resource_kind.is_costable() && attribution_object_id.is_some() {
                    return Err(ModelError::new(
                        ErrorCode::ValuationMismatch,
                        format!("{rp}/attribution_object_id"),
                        "Non-costable transfer line cannot specify attribution_object_id",
                    ));
                }

                let res_objects = parse_string_list_refs(
                    robj.get("object_ids"),
                    known_objects,
                    &format!("{rp}/object_ids"),
                )?;
                resources.push(ResourceSpec {
                    target,
                    unit,
                    quantity,
                    resource_kind,
                    batch_mode,
                    attribution_object_id,
                    object_ids: res_objects,
                });
            }
        }
        recipes.insert(
            node_id.clone(),
            ActivityRecipe {
                activity_id,
                duration_minutes,
                object_ids: step_objects,
                resources,
            },
        );
    }
    Ok(recipes)
}

/// Parameters for recording one committed execution step and its physical resource lines.
pub struct StepRecording<'a> {
    /// Deterministic unique step ID.
    pub step_id: String,
    /// Executed PNML transition ID or BPMN node ID.
    pub node_id: String,
    /// Enclosing subprocess path (empty at top level).
    pub subprocess_path: Vec<String>,
    /// 1-based execution visit count for this node in its scope.
    pub visit: u64,
    /// Integer firing multiplicity (`>= 1`).
    pub multiplicity: u64,
    /// Exact start instant relative to process start, in minutes.
    pub start_minute: ExactQty,
    /// Exact completion instant relative to process start, in minutes.
    pub end_minute: ExactQty,
    /// Attached activity timing and resource recipe.
    pub recipe: &'a ActivityRecipe,
    /// Epistemic basis (`assumed` or `simulated`).
    pub evidence_basis: EvidenceBasis,
}

/// Emit step + resource records for one committed execution step, enforcing batch non-duplication.
pub fn record_step_and_usages(
    steps: &mut Vec<ExecutionStep>,
    usages: &mut Vec<EmittedUsage>,
    rec: StepRecording<'_>,
) -> Result<(), ModelError> {
    if steps.len() >= MAX_EXECUTION_RECORDS {
        return Err(ModelError::new(
            ErrorCode::SizeLimitExceeded,
            "/steps",
            "Execution steps exceed bounded record limit",
        ));
    }
    let StepRecording {
        step_id,
        node_id,
        subprocess_path,
        visit,
        multiplicity,
        start_minute,
        end_minute,
        recipe,
        evidence_basis,
    } = rec;
    let event_id = format!("evt:{step_id}");
    validate_token(&step_id, "/steps/step_id")?;
    validate_token(&event_id, "/steps/event_id")?;
    let step_objs = recipe.object_ids.clone();

    for (idx, res) in recipe.resources.iter().enumerate() {
        if usages.len() >= MAX_EXECUTION_RECORDS {
            return Err(ModelError::new(
                ErrorCode::SizeLimitExceeded,
                "/usages",
                "Emitted usages exceed bounded record limit",
            ));
        }
        let use_id = format!("use:{step_id}:r{idx}:{}", res.target);
        validate_token(&use_id, "/usages/use_id")?;
        let quantity = match &res.batch_mode {
            BatchMode::PerFiring => res
                .quantity
                .checked_mul(ExactQty::from_u64(multiplicity), "/usages/quantity")?,
            BatchMode::SingleSharedBatch { .. } => res.quantity,
        };
        let mut obj_set: BTreeSet<String> = step_objs.iter().cloned().collect();
        for id in &res.object_ids {
            obj_set.insert(id.clone());
        }
        if let BatchMode::SingleSharedBatch { batch_object_id } = &res.batch_mode {
            obj_set.insert(batch_object_id.clone());
        }
        if let Some(attr) = &res.attribution_object_id {
            obj_set.insert(attr.clone());
        }
        usages.push(EmittedUsage {
            use_id,
            step_id: step_id.clone(),
            event_id: event_id.clone(),
            activity_id: recipe.activity_id.clone(),
            resource_kind: res.resource_kind,
            costable: res.resource_kind.is_costable(),
            evidence_basis,
            target: res.target.clone(),
            unit: res.unit.clone(),
            quantity,
            attribution_object_id: res.attribution_object_id.clone(),
            object_ids: obj_set.into_iter().collect(),
        });
    }

    steps.push(ExecutionStep {
        step_id,
        event_id,
        node_id,
        activity_id: recipe.activity_id.clone(),
        subprocess_path,
        visit,
        multiplicity,
        start_minute,
        end_minute,
        object_ids: step_objs,
    });
    Ok(())
}

fn marking_to_json(marking: &BTreeMap<String, u64>) -> JsonValue {
    let mut obj = BTreeMap::new();
    for (place, tokens) in marking {
        obj.insert(place.clone(), JsonValue::Number(tokens.to_string()));
    }
    JsonValue::Object(obj)
}

fn marking_from_json(val: &JsonValue, path: &str) -> Result<BTreeMap<String, u64>, ModelError> {
    let obj = val.as_object(path)?;
    let mut out = BTreeMap::new();
    for (k, v) in obj {
        out.insert(k.clone(), v.as_u64(&format!("{path}/{k}"))?);
    }
    Ok(out)
}

impl ExecutionTrace {
    /// Serialize the execution trace to deterministic JSON without any monetary or quotation data.
    pub fn to_json(&self) -> JsonValue {
        let mut root = BTreeMap::new();
        root.insert(
            "contract_version".to_owned(),
            JsonValue::String(self.contract_version.clone()),
        );
        root.insert(
            "evidence_basis".to_owned(),
            JsonValue::String(self.evidence_basis.as_str().to_owned()),
        );
        if let Some(final_m) = &self.final_marking {
            root.insert("final_marking".to_owned(), marking_to_json(final_m));
        } else {
            root.insert("final_marking".to_owned(), JsonValue::Null);
        }
        if let Some(init_m) = &self.initial_marking {
            root.insert("initial_marking".to_owned(), marking_to_json(init_m));
        } else {
            root.insert("initial_marking".to_owned(), JsonValue::Null);
        }
        root.insert(
            "model_id".to_owned(),
            JsonValue::String(self.model_id.clone()),
        );
        root.insert(
            "model_sha256".to_owned(),
            JsonValue::String(self.model_sha256.clone()),
        );
        root.insert(
            "model_version".to_owned(),
            JsonValue::String(self.model_version.clone()),
        );
        root.insert(
            "object_relations".to_owned(),
            JsonValue::Array(
                self.object_relations
                    .iter()
                    .map(|r| {
                        let mut o = BTreeMap::new();
                        o.insert(
                            "from_object_id".to_owned(),
                            JsonValue::String(r.from_object_id.clone()),
                        );
                        o.insert(
                            "relationship".to_owned(),
                            JsonValue::String(r.relationship.clone()),
                        );
                        o.insert(
                            "to_object_id".to_owned(),
                            JsonValue::String(r.to_object_id.clone()),
                        );
                        JsonValue::Object(o)
                    })
                    .collect(),
            ),
        );
        root.insert(
            "objects".to_owned(),
            JsonValue::Array(
                self.objects
                    .iter()
                    .map(|obj| {
                        let mut o = BTreeMap::new();
                        o.insert("id".to_owned(), JsonValue::String(obj.id.clone()));
                        o.insert("kind".to_owned(), JsonValue::String(obj.kind.clone()));
                        JsonValue::Object(o)
                    })
                    .collect(),
            ),
        );
        root.insert(
            "process_id".to_owned(),
            JsonValue::String(self.process_id.clone()),
        );
        root.insert(
            "profile_id".to_owned(),
            JsonValue::String(self.profile_id.clone()),
        );
        match &self.status {
            ExecutionStatus::Completed => {
                let mut st = BTreeMap::new();
                st.insert(
                    "state".to_owned(),
                    JsonValue::String("completed".to_owned()),
                );
                root.insert("status".to_owned(), JsonValue::Object(st));
            }
            ExecutionStatus::Cancelled {
                cancelled_at_node,
                reason,
            } => {
                let mut st = BTreeMap::new();
                st.insert(
                    "cancelled_at_node".to_owned(),
                    JsonValue::String(cancelled_at_node.clone()),
                );
                st.insert("reason".to_owned(), JsonValue::String(reason.clone()));
                st.insert(
                    "state".to_owned(),
                    JsonValue::String("cancelled".to_owned()),
                );
                root.insert("status".to_owned(), JsonValue::Object(st));
            }
        }
        root.insert(
            "steps".to_owned(),
            JsonValue::Array(
                self.steps
                    .iter()
                    .map(|s| {
                        let mut o = BTreeMap::new();
                        o.insert(
                            "activity_id".to_owned(),
                            JsonValue::String(s.activity_id.clone()),
                        );
                        o.insert("end_minute".to_owned(), s.end_minute.to_trace_json());
                        o.insert("event_id".to_owned(), JsonValue::String(s.event_id.clone()));
                        o.insert(
                            "multiplicity".to_owned(),
                            JsonValue::Number(s.multiplicity.to_string()),
                        );
                        o.insert("node_id".to_owned(), JsonValue::String(s.node_id.clone()));
                        o.insert(
                            "object_ids".to_owned(),
                            JsonValue::Array(
                                s.object_ids
                                    .iter()
                                    .cloned()
                                    .map(JsonValue::String)
                                    .collect(),
                            ),
                        );
                        o.insert("start_minute".to_owned(), s.start_minute.to_trace_json());
                        o.insert("step_id".to_owned(), JsonValue::String(s.step_id.clone()));
                        o.insert(
                            "subprocess_path".to_owned(),
                            JsonValue::Array(
                                s.subprocess_path
                                    .iter()
                                    .cloned()
                                    .map(JsonValue::String)
                                    .collect(),
                            ),
                        );
                        o.insert("visit".to_owned(), JsonValue::Number(s.visit.to_string()));
                        JsonValue::Object(o)
                    })
                    .collect(),
            ),
        );
        root.insert(
            "total_elapsed_minutes".to_owned(),
            self.total_elapsed_minutes.to_trace_json(),
        );
        root.insert(
            "usages".to_owned(),
            JsonValue::Array(
                self.usages
                    .iter()
                    .map(|u| {
                        let mut o = BTreeMap::new();
                        o.insert(
                            "activity_id".to_owned(),
                            JsonValue::String(u.activity_id.clone()),
                        );
                        o.insert(
                            "attribution_object_id".to_owned(),
                            u.attribution_object_id
                                .as_ref()
                                .map_or(JsonValue::Null, |id| JsonValue::String(id.clone())),
                        );
                        o.insert("costable".to_owned(), JsonValue::Bool(u.costable));
                        o.insert(
                            "evidence_basis".to_owned(),
                            JsonValue::String(u.evidence_basis.as_str().to_owned()),
                        );
                        o.insert("event_id".to_owned(), JsonValue::String(u.event_id.clone()));
                        o.insert(
                            "object_ids".to_owned(),
                            JsonValue::Array(
                                u.object_ids
                                    .iter()
                                    .cloned()
                                    .map(JsonValue::String)
                                    .collect(),
                            ),
                        );
                        o.insert("quantity".to_owned(), u.quantity.to_trace_json());
                        o.insert(
                            "resource_kind".to_owned(),
                            JsonValue::String(u.resource_kind.as_str().to_owned()),
                        );
                        o.insert("step_id".to_owned(), JsonValue::String(u.step_id.clone()));
                        o.insert("target".to_owned(), JsonValue::String(u.target.clone()));
                        o.insert("unit".to_owned(), JsonValue::String(u.unit.clone()));
                        o.insert("use_id".to_owned(), JsonValue::String(u.use_id.clone()));
                        JsonValue::Object(o)
                    })
                    .collect(),
            ),
        );
        JsonValue::Object(root)
    }

    /// Decode an `ExecutionTrace` previously produced by `execute-pnml` or `execute-bpmn`.
    pub fn from_json(value: &JsonValue) -> Result<Self, ModelError> {
        let root = value.as_object("/")?;
        let contract_version = req_field(root, "contract_version", "/")?
            .as_str("/contract_version")?
            .to_owned();
        if contract_version != CONTRACT_VERSION {
            return Err(ModelError::new(
                ErrorCode::MalformedJson,
                "/contract_version",
                format!("Unsupported trace contract_version `{contract_version}`"),
            ));
        }
        let profile_id = req_field(root, "profile_id", "/")?
            .as_str("/profile_id")?
            .to_owned();
        let model_sha256 = req_field(root, "model_sha256", "/")?
            .as_str("/model_sha256")?
            .to_owned();
        if !model_sha256.starts_with("sha256:") || model_sha256.len() != 71 {
            return Err(ModelError::new(
                ErrorCode::MalformedJson,
                "/model_sha256",
                "Expected `sha256:<64-hex>` model digest",
            ));
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
        let initial_marking = match root.get("initial_marking") {
            None | Some(JsonValue::Null) => None,
            Some(v) => Some(marking_from_json(v, "/initial_marking")?),
        };
        let final_marking = match root.get("final_marking") {
            None | Some(JsonValue::Null) => None,
            Some(v) => Some(marking_from_json(v, "/final_marking")?),
        };
        let total_elapsed_minutes = ExactQty::from_json(
            req_field(root, "total_elapsed_minutes", "/")?,
            "/total_elapsed_minutes",
        )?;

        let status_obj = req_field(root, "status", "/")?.as_object("/status")?;
        let status = match req_field(status_obj, "state", "/status")?.as_str("/status/state")? {
            "completed" => ExecutionStatus::Completed,
            "cancelled" => ExecutionStatus::Cancelled {
                cancelled_at_node: req_field(status_obj, "cancelled_at_node", "/status")?
                    .as_str("/status/cancelled_at_node")?
                    .to_owned(),
                reason: req_field(status_obj, "reason", "/status")?
                    .as_str("/status/reason")?
                    .to_owned(),
            },
            other => {
                return Err(ModelError::new(
                    ErrorCode::MalformedJson,
                    "/status/state",
                    format!("Unknown trace status `{other}`"),
                ));
            }
        };

        let (objects, _object_set, object_relations) = parse_objects_and_relations(root, "")?;

        let raw_steps = req_field(root, "steps", "/")?.as_array("/steps")?;
        let mut steps = Vec::with_capacity(raw_steps.len());
        for (idx, item) in raw_steps.iter().enumerate() {
            let sp = format!("/steps/{idx}");
            let so = item.as_object(&sp)?;
            let step_id = req_field(so, "step_id", &sp)?
                .as_str(&format!("{sp}/step_id"))?
                .to_owned();
            let event_id = req_field(so, "event_id", &sp)?
                .as_str(&format!("{sp}/event_id"))?
                .to_owned();
            let node_id = req_field(so, "node_id", &sp)?
                .as_str(&format!("{sp}/node_id"))?
                .to_owned();
            let activity_id = req_field(so, "activity_id", &sp)?
                .as_str(&format!("{sp}/activity_id"))?
                .to_owned();
            let visit = req_field(so, "visit", &sp)?.as_u64(&format!("{sp}/visit"))?;
            let multiplicity =
                req_field(so, "multiplicity", &sp)?.as_u64(&format!("{sp}/multiplicity"))?;
            let start_minute = ExactQty::from_json(
                req_field(so, "start_minute", &sp)?,
                &format!("{sp}/start_minute"),
            )?;
            let end_minute = ExactQty::from_json(
                req_field(so, "end_minute", &sp)?,
                &format!("{sp}/end_minute"),
            )?;
            let subprocess_path = req_field(so, "subprocess_path", &sp)?
                .as_array(&format!("{sp}/subprocess_path"))?
                .iter()
                .enumerate()
                .map(|(j, v)| {
                    v.as_str(&format!("{sp}/subprocess_path/{j}"))
                        .map(str::to_owned)
                })
                .collect::<Result<Vec<_>, _>>()?;
            let object_ids = req_field(so, "object_ids", &sp)?
                .as_array(&format!("{sp}/object_ids"))?
                .iter()
                .enumerate()
                .map(|(j, v)| v.as_str(&format!("{sp}/object_ids/{j}")).map(str::to_owned))
                .collect::<Result<Vec<_>, _>>()?;
            steps.push(ExecutionStep {
                step_id,
                event_id,
                node_id,
                activity_id,
                subprocess_path,
                visit,
                multiplicity,
                start_minute,
                end_minute,
                object_ids,
            });
        }

        let raw_usages = req_field(root, "usages", "/")?.as_array("/usages")?;
        let mut usages = Vec::with_capacity(raw_usages.len());
        for (idx, item) in raw_usages.iter().enumerate() {
            let up = format!("/usages/{idx}");
            let uo = item.as_object(&up)?;
            let resource_kind = ResourceKind::parse(
                req_field(uo, "resource_kind", &up)?.as_str(&format!("{up}/resource_kind"))?,
                &format!("{up}/resource_kind"),
            )?;
            let costable = req_field(uo, "costable", &up)?.as_bool(&format!("{up}/costable"))?;
            if costable != resource_kind.is_costable() {
                return Err(ModelError::new(
                    ErrorCode::MalformedJson,
                    format!("{up}/costable"),
                    "Transfer lines cannot be marked costable",
                ));
            }
            let attribution_object_id = match uo.get("attribution_object_id") {
                None | Some(JsonValue::Null) => None,
                Some(v) => Some(v.as_str(&format!("{up}/attribution_object_id"))?.to_owned()),
            };
            let object_ids = req_field(uo, "object_ids", &up)?
                .as_array(&format!("{up}/object_ids"))?
                .iter()
                .enumerate()
                .map(|(j, v)| v.as_str(&format!("{up}/object_ids/{j}")).map(str::to_owned))
                .collect::<Result<Vec<_>, _>>()?;
            usages.push(EmittedUsage {
                use_id: req_field(uo, "use_id", &up)?
                    .as_str(&format!("{up}/use_id"))?
                    .to_owned(),
                step_id: req_field(uo, "step_id", &up)?
                    .as_str(&format!("{up}/step_id"))?
                    .to_owned(),
                event_id: req_field(uo, "event_id", &up)?
                    .as_str(&format!("{up}/event_id"))?
                    .to_owned(),
                activity_id: req_field(uo, "activity_id", &up)?
                    .as_str(&format!("{up}/activity_id"))?
                    .to_owned(),
                resource_kind,
                costable,
                evidence_basis: EvidenceBasis::parse(
                    req_field(uo, "evidence_basis", &up)?
                        .as_str(&format!("{up}/evidence_basis"))?,
                    &format!("{up}/evidence_basis"),
                )?,
                target: req_field(uo, "target", &up)?
                    .as_str(&format!("{up}/target"))?
                    .to_owned(),
                unit: req_field(uo, "unit", &up)?
                    .as_str(&format!("{up}/unit"))?
                    .to_owned(),
                quantity: ExactQty::from_json(
                    req_field(uo, "quantity", &up)?,
                    &format!("{up}/quantity"),
                )?,
                attribution_object_id,
                object_ids,
            });
        }

        Ok(Self {
            contract_version,
            profile_id,
            model_sha256,
            process_id,
            model_id,
            model_version,
            evidence_basis,
            status,
            initial_marking,
            final_marking,
            total_elapsed_minutes,
            objects,
            object_relations,
            steps,
            usages,
        })
    }
}

impl ValuationAttachment {
    /// Parse valuation attachment / quotation release JSON strictly.
    pub fn from_json(value: &JsonValue) -> Result<Self, ModelError> {
        let root = value.as_object("/")?;
        reject_unknown_keys(
            root,
            &[
                "allocations",
                "knowledge_cutoff",
                "policy",
                "quote_bindings",
                "quotes",
                "run_id",
                "service_date",
                "source_access",
                "source_evidence",
                "source_locator",
                "source_validation",
            ],
            "",
        )?;
        let run_id = req_field(root, "run_id", "/")?
            .as_str("/run_id")?
            .to_owned();
        validate_token(&run_id, "/run_id")?;
        let knowledge_cutoff = req_field(root, "knowledge_cutoff", "/")?
            .as_str("/knowledge_cutoff")?
            .to_owned();
        let service_date = req_field(root, "service_date", "/")?
            .as_str("/service_date")?
            .to_owned();
        validate_date(&knowledge_cutoff, "/knowledge_cutoff")?;
        validate_date(&service_date, "/service_date")?;

        let source_evidence = req_field(root, "source_evidence", "/")?
            .as_str("/source_evidence")?
            .to_owned();
        if !matches!(source_evidence.as_str(), "synthetic" | "derived") {
            return Err(ModelError::new(
                ErrorCode::ValuationMismatch,
                "/source_evidence",
                "Model execution must project to `synthetic` or `derived`, never `observed`",
            ));
        }
        let source_access = req_field(root, "source_access", "/")?
            .as_str("/source_access")?
            .to_owned();
        if !matches!(source_access.as_str(), "public" | "restricted" | "private") {
            return Err(ModelError::new(
                ErrorCode::MalformedJson,
                "/source_access",
                "Unsupported source_access",
            ));
        }
        let source_validation = req_field(root, "source_validation", "/")?
            .as_str("/source_validation")?
            .to_owned();
        if !matches!(
            source_validation.as_str(),
            "unvalidated" | "source_verified" | "empirically_validated"
        ) {
            return Err(ModelError::new(
                ErrorCode::MalformedJson,
                "/source_validation",
                "Unsupported source_validation",
            ));
        }
        let source_locator = match root.get("source_locator") {
            None | Some(JsonValue::Null) => None,
            Some(v) => Some(v.as_str("/source_locator")?.to_owned()),
        };

        let policy = req_field(root, "policy", "/")?.clone();
        policy.as_object("/policy")?;

        let bindings_obj = req_field(root, "quote_bindings", "/")?.as_object("/quote_bindings")?;
        let mut quote_bindings = BTreeMap::new();
        for (target, qid) in bindings_obj {
            let p = format!("/quote_bindings/{target}");
            validate_token(target, &p)?;
            let id = qid.as_str(&p)?.to_owned();
            validate_token(&id, &p)?;
            quote_bindings.insert(target.clone(), id);
        }

        let quotes_arr = req_field(root, "quotes", "/")?.as_array("/quotes")?;
        let mut quotes = Vec::with_capacity(quotes_arr.len());
        let mut quote_targets: BTreeMap<String, String> = BTreeMap::new();
        for (idx, q) in quotes_arr.iter().enumerate() {
            let qp = format!("/quotes/{idx}");
            let qobj = q.as_object(&qp)?;
            let qid = req_field(qobj, "id", &qp)?.as_str(&format!("{qp}/id"))?;
            let qtarget = req_field(qobj, "target", &qp)?.as_str(&format!("{qp}/target"))?;
            let qunit = req_field(qobj, "unit", &qp)?.as_str(&format!("{qp}/unit"))?;
            if quote_targets
                .insert(qid.to_owned(), format!("{qtarget}::{qunit}"))
                .is_some()
            {
                return Err(ModelError::new(
                    ErrorCode::DuplicateIdentity,
                    format!("{qp}/id"),
                    format!("Duplicate quote_id `{qid}`"),
                ));
            }
            quotes.push(q.clone());
        }

        let mut allocations = Vec::new();
        if let Some(raw_allocs) = root.get("allocations") {
            for (idx, item) in raw_allocs.as_array("/allocations")?.iter().enumerate() {
                let ap = format!("/allocations/{idx}");
                let ao = item.as_object(&ap)?;
                reject_unknown_keys(
                    ao,
                    &["id", "match_activity_id", "match_target", "weights"],
                    &ap,
                )?;
                let id = req_field(ao, "id", &ap)?
                    .as_str(&format!("{ap}/id"))?
                    .to_owned();
                validate_token(&id, &format!("{ap}/id"))?;
                let match_target = req_field(ao, "match_target", &ap)?
                    .as_str(&format!("{ap}/match_target"))?
                    .to_owned();
                let match_activity_id = match ao.get("match_activity_id") {
                    None | Some(JsonValue::Null) => None,
                    Some(v) => Some(v.as_str(&format!("{ap}/match_activity_id"))?.to_owned()),
                };
                let weights_arr =
                    req_field(ao, "weights", &ap)?.as_array(&format!("{ap}/weights"))?;
                let mut weights = Vec::with_capacity(weights_arr.len());
                for (j, wv) in weights_arr.iter().enumerate() {
                    let wp = format!("{ap}/weights/{j}");
                    let wo = wv.as_object(&wp)?;
                    reject_unknown_keys(wo, &["object_id", "weight"], &wp)?;
                    let oid = req_field(wo, "object_id", &wp)?
                        .as_str(&format!("{wp}/object_id"))?
                        .to_owned();
                    let wraw = req_field(wo, "weight", &wp)?.as_str(&format!("{wp}/weight"))?;
                    weights.push((oid, ExactQty::parse(wraw, &format!("{wp}/weight"))?));
                }
                allocations.push(AllocationRule {
                    id,
                    match_target,
                    match_activity_id,
                    weights,
                });
            }
        }

        Ok(Self {
            run_id,
            knowledge_cutoff,
            service_date,
            source_evidence,
            source_access,
            source_validation,
            source_locator,
            policy,
            quote_bindings,
            quotes,
            allocations,
        })
    }
}

/// Project an executed physical trace and an independent quotation release into a Dapane `0.1` request.
pub fn project_to_dapane_request(
    trace: &ExecutionTrace,
    valuation: &ValuationAttachment,
) -> Result<JsonValue, ModelError> {
    let quote_index: BTreeMap<String, (&str, &str)> = valuation
        .quotes
        .iter()
        .enumerate()
        .map(|(i, q)| {
            let qp = format!("/quotes/{i}");
            let qo = q.as_object(&qp)?;
            let id = req_field(qo, "id", &qp)?
                .as_str(&format!("{qp}/id"))?
                .to_owned();
            let target = req_field(qo, "target", &qp)?.as_str(&format!("{qp}/target"))?;
            let unit = req_field(qo, "unit", &qp)?.as_str(&format!("{qp}/unit"))?;
            Ok((id, (target, unit)))
        })
        .collect::<Result<BTreeMap<_, _>, ModelError>>()?;

    let mut usage_lines = Vec::new();
    struct CostableMeta<'a> {
        line_id: String,
        target: &'a str,
        activity_id: &'a str,
        has_direct_attribution: bool,
    }
    let mut costable_metas = Vec::new();
    let source_id = format!("model-{}", trace.model_id);
    validate_token(&source_id, "/usage/source/id")?;

    for (idx, u) in trace.usages.iter().enumerate() {
        if !u.costable {
            continue;
        }
        let quote_id = valuation.quote_bindings.get(&u.target).ok_or_else(|| {
            ModelError::new(
                ErrorCode::ValuationMismatch,
                format!("/usages/{idx}/target"),
                format!("No quote binding for costable target `{}`", u.target),
            )
        })?;
        let (q_target, q_unit) = quote_index.get(quote_id).ok_or_else(|| {
            ModelError::new(
                ErrorCode::ValuationMismatch,
                "/quote_bindings",
                format!("Bound quote_id `{quote_id}` not found in quotes release"),
            )
        })?;
        if *q_target != u.target || *q_unit != u.unit {
            return Err(ModelError::new(
                ErrorCode::ValuationMismatch,
                format!("/usages/{idx}"),
                format!(
                    "Quote `{quote_id}` ({q_target}/{q_unit}) mismatches usage target/unit ({}/{})",
                    u.target, u.unit
                ),
            ));
        }

        let line_id = format!("line-{}", u.use_id);
        validate_token(&line_id, "/usage/id")?;
        let mut src = BTreeMap::new();
        src.insert(
            "access".to_owned(),
            JsonValue::String(valuation.source_access.clone()),
        );
        src.insert(
            "content_digest".to_owned(),
            JsonValue::String(trace.model_sha256.clone()),
        );
        src.insert(
            "evidence".to_owned(),
            JsonValue::String(valuation.source_evidence.clone()),
        );
        src.insert("id".to_owned(), JsonValue::String(source_id.clone()));
        src.insert(
            "locator".to_owned(),
            valuation
                .source_locator
                .as_ref()
                .map_or(JsonValue::Null, |l| JsonValue::String(l.clone())),
        );
        src.insert(
            "validation".to_owned(),
            JsonValue::String(valuation.source_validation.clone()),
        );
        src.insert(
            "version".to_owned(),
            JsonValue::String(trace.model_version.clone()),
        );

        let mut row = BTreeMap::new();
        row.insert(
            "activity_id".to_owned(),
            JsonValue::String(u.activity_id.clone()),
        );
        row.insert(
            "attribution_object_id".to_owned(),
            u.attribution_object_id
                .as_ref()
                .map_or(JsonValue::Null, |id| JsonValue::String(id.clone())),
        );
        row.insert("event_id".to_owned(), JsonValue::String(u.event_id.clone()));
        row.insert("id".to_owned(), JsonValue::String(line_id.clone()));
        row.insert(
            "kind".to_owned(),
            JsonValue::String("resource_use".to_owned()),
        );
        row.insert(
            "object_ids".to_owned(),
            JsonValue::Array(
                u.object_ids
                    .iter()
                    .cloned()
                    .map(JsonValue::String)
                    .collect(),
            ),
        );
        row.insert(
            "process_id".to_owned(),
            JsonValue::String(trace.process_id.clone()),
        );
        row.insert("quantity".to_owned(), u.quantity.to_dapane_json());
        row.insert("quote_id".to_owned(), JsonValue::String(quote_id.clone()));
        row.insert(
            "service_date".to_owned(),
            JsonValue::String(valuation.service_date.clone()),
        );
        row.insert("source".to_owned(), JsonValue::Object(src));
        row.insert("target".to_owned(), JsonValue::String(u.target.clone()));
        row.insert("unit".to_owned(), JsonValue::String(u.unit.clone()));
        row.insert("use_id".to_owned(), JsonValue::String(u.use_id.clone()));
        usage_lines.push(JsonValue::Object(row));

        costable_metas.push(CostableMeta {
            line_id,
            target: &u.target,
            activity_id: &u.activity_id,
            has_direct_attribution: u.attribution_object_id.is_some(),
        });
    }

    let mut allocs_json = Vec::new();
    for rule in &valuation.allocations {
        let mut matched_lines = Vec::new();
        for meta in &costable_metas {
            let act_ok = rule
                .match_activity_id
                .as_deref()
                .is_none_or(|a| a == meta.activity_id);
            if meta.target == rule.match_target && act_ok {
                if meta.has_direct_attribution {
                    return Err(ModelError::new(
                        ErrorCode::ValuationMismatch,
                        format!("/allocations/{}", rule.id),
                        "Pooled allocation rule cannot match a directly attributed usage line",
                    ));
                }
                matched_lines.push(JsonValue::String(meta.line_id.clone()));
            }
        }
        if matched_lines.is_empty() {
            // Cancelled or unreached branch never emitted this pooled line.
            continue;
        }
        let weights_json = rule
            .weights
            .iter()
            .map(|(oid, w)| {
                let mut wo = BTreeMap::new();
                wo.insert("object_id".to_owned(), JsonValue::String(oid.clone()));
                wo.insert("weight".to_owned(), w.to_dapane_json());
                JsonValue::Object(wo)
            })
            .collect();
        let mut ao = BTreeMap::new();
        ao.insert("id".to_owned(), JsonValue::String(rule.id.clone()));
        ao.insert(
            "source_line_ids".to_owned(),
            JsonValue::Array(matched_lines),
        );
        ao.insert("weights".to_owned(), JsonValue::Array(weights_json));
        allocs_json.push(JsonValue::Object(ao));
    }

    let mut process_obj = BTreeMap::new();
    process_obj.insert("id".to_owned(), JsonValue::String(trace.process_id.clone()));
    process_obj.insert(
        "model_id".to_owned(),
        JsonValue::String(trace.model_id.clone()),
    );
    process_obj.insert(
        "model_version".to_owned(),
        JsonValue::String(trace.model_version.clone()),
    );

    let events_json = trace
        .steps
        .iter()
        .map(|s| {
            let mut eo = BTreeMap::new();
            eo.insert(
                "activity_id".to_owned(),
                JsonValue::String(s.activity_id.clone()),
            );
            eo.insert("id".to_owned(), JsonValue::String(s.event_id.clone()));
            eo.insert(
                "object_ids".to_owned(),
                JsonValue::Array(
                    s.object_ids
                        .iter()
                        .cloned()
                        .map(JsonValue::String)
                        .collect(),
                ),
            );
            eo.insert(
                "occurred_on".to_owned(),
                JsonValue::String(valuation.service_date.clone()),
            );
            eo.insert(
                "process_id".to_owned(),
                JsonValue::String(trace.process_id.clone()),
            );
            JsonValue::Object(eo)
        })
        .collect();

    let objects_json = trace
        .objects
        .iter()
        .map(|o| {
            let mut map = BTreeMap::new();
            map.insert("id".to_owned(), JsonValue::String(o.id.clone()));
            map.insert("kind".to_owned(), JsonValue::String(o.kind.clone()));
            JsonValue::Object(map)
        })
        .collect();

    let relations_json = trace
        .object_relations
        .iter()
        .map(|r| {
            let mut map = BTreeMap::new();
            map.insert(
                "from_object_id".to_owned(),
                JsonValue::String(r.from_object_id.clone()),
            );
            map.insert(
                "relationship".to_owned(),
                JsonValue::String(r.relationship.clone()),
            );
            map.insert(
                "to_object_id".to_owned(),
                JsonValue::String(r.to_object_id.clone()),
            );
            JsonValue::Object(map)
        })
        .collect();

    let mut req = BTreeMap::new();
    req.insert("allocations".to_owned(), JsonValue::Array(allocs_json));
    req.insert("events".to_owned(), JsonValue::Array(events_json));
    req.insert(
        "knowledge_cutoff".to_owned(),
        JsonValue::String(valuation.knowledge_cutoff.clone()),
    );
    req.insert(
        "object_relations".to_owned(),
        JsonValue::Array(relations_json),
    );
    req.insert("objects".to_owned(), JsonValue::Array(objects_json));
    req.insert("policy".to_owned(), valuation.policy.clone());
    req.insert(
        "processes".to_owned(),
        JsonValue::Array(vec![JsonValue::Object(process_obj)]),
    );
    req.insert(
        "quotes".to_owned(),
        JsonValue::Array(valuation.quotes.clone()),
    );
    req.insert(
        "run_id".to_owned(),
        JsonValue::String(valuation.run_id.clone()),
    );
    req.insert(
        "schema_version".to_owned(),
        JsonValue::String("0.1".to_owned()),
    );
    req.insert("usage".to_owned(), JsonValue::Array(usage_lines));

    Ok(JsonValue::Object(req))
}
