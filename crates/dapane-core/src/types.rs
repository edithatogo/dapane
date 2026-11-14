//! Versioned wire DTOs. Exact numbers never pass through a floating-point type.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Rational {
    pub numerator: String,
    pub denominator: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(untagged)]
pub enum ExactNumber {
    Decimal(String),
    Rational(Rational),
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(rename_all = "snake_case")]
pub enum MeasureKind {
    ResourceUse,
    ActivityMeasure,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ValuationBasis {
    EconomicCost,
    FinancialCost,
    Funding,
    Charge,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum RoundingMode {
    HalfEven,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct RoundingPolicy {
    pub scale: u8,
    pub mode: RoundingMode,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ValuationPolicy {
    pub id: String,
    pub version: String,
    pub currency: String,
    pub price_year: u16,
    pub perspective: String,
    pub basis: ValuationBasis,
    pub rounding: RoundingPolicy,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum Evidence {
    Synthetic,
    Observed,
    Derived,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum SourceAccess {
    Public,
    Restricted,
    Private,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum SourceValidation {
    Unvalidated,
    SourceVerified,
    EmpiricallyValidated,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct SourceRef {
    pub id: String,
    pub version: String,
    pub evidence: Evidence,
    pub access: SourceAccess,
    pub validation: SourceValidation,
    #[serde(default)]
    pub content_digest: Option<String>,
    #[serde(default)]
    pub locator: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct UnitQuote {
    pub id: String,
    pub kind: MeasureKind,
    pub target: String,
    pub unit: String,
    pub amount: ExactNumber,
    pub per_quantity: ExactNumber,
    pub currency: String,
    pub price_year: u16,
    pub basis: ValuationBasis,
    pub components: Vec<String>,
    pub valid_from: String,
    pub valid_to: String,
    pub known_from: String,
    pub source: SourceRef,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Usage {
    pub id: String,
    pub use_id: String,
    pub kind: MeasureKind,
    pub target: String,
    pub unit: String,
    pub quantity: ExactNumber,
    pub service_date: String,
    pub quote_id: String,
    pub source: SourceRef,
    #[serde(default)]
    pub event_id: Option<String>,
    #[serde(default)]
    pub process_id: Option<String>,
    #[serde(default)]
    pub activity_id: Option<String>,
    #[serde(default)]
    pub object_ids: Vec<String>,
    #[serde(default)]
    pub attribution_object_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct CostObject {
    pub id: String,
    pub kind: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ProcessInstance {
    pub id: String,
    pub model_id: String,
    pub model_version: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Event {
    pub id: String,
    pub occurred_on: String,
    #[serde(default)]
    pub process_id: Option<String>,
    #[serde(default)]
    pub activity_id: Option<String>,
    #[serde(default)]
    pub object_ids: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ObjectRelation {
    pub from_object_id: String,
    pub to_object_id: String,
    pub relationship: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct AllocationWeight {
    pub object_id: String,
    pub weight: ExactNumber,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Allocation {
    pub id: String,
    pub source_line_ids: Vec<String>,
    pub weights: Vec<AllocationWeight>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Request {
    pub schema_version: String,
    pub run_id: String,
    pub knowledge_cutoff: String,
    pub policy: ValuationPolicy,
    pub quotes: Vec<UnitQuote>,
    pub usage: Vec<Usage>,
    #[serde(default)]
    pub objects: Vec<CostObject>,
    #[serde(default)]
    pub processes: Vec<ProcessInstance>,
    #[serde(default)]
    pub events: Vec<Event>,
    #[serde(default)]
    pub object_relations: Vec<ObjectRelation>,
    #[serde(default)]
    pub allocations: Vec<Allocation>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ValuationLine {
    pub id: String,
    pub use_id: String,
    pub kind: MeasureKind,
    pub target: String,
    pub unit: String,
    pub quote_id: String,
    pub quantity: Rational,
    pub components: Vec<String>,
    pub service_date: String,
    pub exact: Rational,
    pub rounded: String,
    pub rounding_adjustment: Rational,
    pub source: SourceRef,
    pub event_id: Option<String>,
    pub process_id: Option<String>,
    pub activity_id: Option<String>,
    pub object_ids: Vec<String>,
    pub attribution_object_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Totals {
    pub exact: Rational,
    pub rounded: String,
    pub rounding_adjustment: Rational,
    pub directly_attributed: String,
    pub allocated: String,
    pub unattributed: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct AllocationShare {
    pub object_id: String,
    pub weight: Rational,
    pub exact_share: Rational,
    pub rounded: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct AllocationResult {
    pub id: String,
    pub source_line_ids: Vec<String>,
    pub pool_exact: Rational,
    pub pool_rounded: String,
    pub shares: Vec<AllocationShare>,
    pub residual: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ObjectTotal {
    pub object_id: String,
    pub direct: String,
    pub allocated: String,
    pub total: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Context {
    pub objects: Vec<CostObject>,
    pub processes: Vec<ProcessInstance>,
    pub events: Vec<Event>,
    pub object_relations: Vec<ObjectRelation>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ReportStatus {
    Complete,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Report {
    pub schema_version: String,
    pub run_id: String,
    pub status: ReportStatus,
    pub engine_version: String,
    pub method_version: String,
    pub input_digest: String,
    pub output_digest: String,
    pub policy: ValuationPolicy,
    pub lines: Vec<ValuationLine>,
    pub quote_snapshots: Vec<UnitQuote>,
    pub context: Context,
    pub totals: Totals,
    pub allocations: Vec<AllocationResult>,
    pub object_totals: Vec<ObjectTotal>,
}
