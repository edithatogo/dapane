//! Independent, typed X1 observation contracts. This crate does **not** decode
//! XES or OCEL, execute a process, measure elapsed use, or calculate money.
//!
//! A future qualified Rust4PM adapter must preserve its native source model and
//! submit explicitly mapped assertions to this boundary. Contract validation is
//! not native-format qualification, source verification, or a valuation report.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt;

/// Contract identity; separate from all Dapane monetary method identities.
pub const CONTRACT_VERSION: &str = "dapane-observed-contracts-v0.1.0";
/// No raw decoder is enabled by this contract-only package.
pub const RAW_IMPORT_STATUS: &str = "blocked_dependency_qualification";
/// Maximum records in any one top-level collection.
pub const MAX_COLLECTION: usize = 10_000;
/// Maximum top-level records and, separately, nested references.
pub const MAX_AGGREGATE: usize = 20_000;

/// Raw format for which the retained source is declared; not a parser selector.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SourceFormat {
    /// IEEE XES XML, restricted further by the future qualified mapping profile.
    Xes,
    /// OCEL 2.0 JSON; OCEL XML/SQLite/2.1 are outside X1's proposed subset.
    Ocel2Json,
}

/// Identity of retained source bytes, supplied by the caller.
///
/// The digest is syntax-checked only: no raw bytes enter this validator. Full
/// typed attributes, history and native relationships stay in that source.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SourceIdentity {
    /// Stable source namespace, never a trace number or array position.
    pub namespace: String,
    /// Explicit immutable snapshot revision; no implicit latest revision.
    pub revision: String,
    /// Declared native format.
    pub format: SourceFormat,
    /// Lowercase hexadecimal SHA-256 prefixed with `sha256:`.
    pub content_digest: String,
}

/// A UTC instant already decoded by a caller, with nanosecond precision.
///
/// Seconds are relative to 1970-01-01T00:00:00Z. The proposed profile accepts
/// years 0001..9999, nanoseconds below 1e9, and no leap-second encoding. The raw
/// source retains offset spelling; this type does not parse a timestamp string.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct Instant {
    /// Whole UTC Unix seconds.
    pub unix_seconds: i64,
    /// Nonnegative fractional nanoseconds.
    pub nanosecond: u32,
}

/// Declared observation coverage, not an imputation rule.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ObservationWindow {
    /// Inclusive start for observation anchors.
    pub start: Instant,
    /// Inclusive endpoint for completion anchors; occupancy is still half-open.
    pub end: Instant,
}

/// Object identity and source-declared type, without copying the native model.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ObjectRef {
    /// Source-stable object ID.
    pub id: String,
    /// Source-declared object kind, e.g. infant, specimen, assay or batch.
    pub kind: String,
}

/// A qualified event-to-object edge retained by the costing projection.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub struct ObjectLink {
    /// Referenced object identity.
    pub object_id: String,
    /// Source qualifier; an empty qualifier is valid and is preserved.
    pub qualifier: String,
}

/// Only the event identity, instant and context needed by this contract.
///
/// This is not an OCEL event replacement. Native attributes and history must
/// remain in the digest-identified source, with a separately qualified decoder.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EventRef {
    /// Source-stable ID; never synthesized from name, time or array order.
    pub id: String,
    /// Missing time is represented explicitly and rejected by validation.
    pub at: Option<Instant>,
    /// Context edges; these never multiply or allocate use.
    pub objects: Vec<ObjectLink>,
}

/// A directed, qualified object relationship used as context only.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub struct ObjectRelation {
    /// Source object.
    pub from: String,
    /// Target object.
    pub to: String,
    /// Source qualifier, including the valid empty string.
    pub qualifier: String,
}

/// Epistemic basis of the asserted quantity, distinct from a synthetic fixture.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Basis {
    /// Explicitly measured or recorded use.
    Observed,
    /// A recipe or other stated assumption.
    Assumed,
    /// A separate execution engine's stated output.
    Simulated,
}

/// Resource semantics; movement is not consumption.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum UseKind {
    /// Explicitly recorded consumable quantity.
    Consumption,
    /// Explicit occupied quantity; never inferred from queue/arrival duration.
    Occupancy,
    /// Contextual movement, excluded from costing readiness.
    Transfer,
}

/// Exact nonnegative rational spelling, with no floating-point conversion.
///
/// This boundary checks unsigned decimal digits (at most 96 each) and a nonzero
/// denominator. It does not reduce, calculate, split or round the quantity.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Quantity {
    /// Unsigned decimal numerator, including explicit zero.
    pub numerator: String,
    /// Unsigned, nonzero decimal denominator.
    pub denominator: String,
}

/// Which interval endpoints are outside the declared observation coverage.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Censoring {
    /// Both endpoints are observed.
    None,
    /// Start is unknown, end is observed.
    Left,
    /// Start is observed, end is unknown.
    Right,
    /// Neither endpoint is observed.
    Both,
}

/// Explicit source-event pairing. Ordering alone never creates a pair.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Extent {
    /// A single observed anchor.
    Point {
        /// Existing source event ID.
        event_id: String,
    },
    /// A half-open occupancy or explicit consumption interval.
    Interval {
        /// Observed start anchor, absent only for left/both censoring.
        start_event_id: Option<String>,
        /// Observed end anchor, absent only for right/both censoring.
        end_event_id: Option<String>,
        /// Mandatory, exact declaration of the missing endpoints.
        censoring: Censoring,
    },
}

/// Corrections are represented so that the unsupported actions fail visibly.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Correction {
    /// An assertion in the explicitly selected source snapshot.
    Original,
    /// Unsupported until a separately qualified correction protocol exists.
    Replace {
        /// Identity the caller intended to replace.
        use_id: String,
    },
    /// Unsupported; never encoded as an ordinary negative quantity.
    Retract {
        /// Identity the caller intended to retract.
        use_id: String,
    },
}

/// Exactly one assertion for one underlying use, irrespective of object count.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UseAssertion {
    /// Stable use ID within the source namespace/revision.
    pub id: String,
    /// Explicit resource identity, not guessed from an activity name.
    pub resource_id: String,
    /// Explicit, case-sensitive unit; no conversion is performed.
    pub unit: String,
    /// Consumption, occupancy or transfer.
    pub kind: UseKind,
    /// Observed, assumed or simulated; preserved without promotion.
    pub basis: Basis,
    /// Missing is unknown, distinct from zero; blocks costing readiness.
    pub quantity: Option<Quantity>,
    /// Explicit anchors and censoring.
    pub extent: Extent,
    /// Source-declared context; not allocation recipients or multipliers.
    pub object_ids: Vec<String>,
    /// Explicit correction action; only original assertions are supported.
    pub correction: Correction,
}

/// A caller-prepared projection for contract checking, not a decoded event log.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Snapshot {
    /// Retained raw-source identity.
    pub source: SourceIdentity,
    /// Explicit coverage boundary.
    pub window: ObservationWindow,
    /// Object identity registry.
    pub objects: Vec<ObjectRef>,
    /// Event anchors and their many-to-many context.
    pub events: Vec<EventRef>,
    /// Directed, qualified object relationships.
    pub relations: Vec<ObjectRelation>,
    /// One row per use, never one row per related object or flattened trace.
    pub uses: Vec<UseAssertion>,
}

/// Stable error categories; no raw source values are put in error paths.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ErrorCode {
    /// Empty, untrimmed, oversized or control-bearing identifier/token.
    InvalidToken,
    /// Invalid SHA-256 spelling (not a digest mismatch verification).
    InvalidDigest,
    /// Invalid range or fractional precision for an already-decoded instant.
    InvalidInstant,
    /// Collection or aggregate reference limit exceeded.
    LimitExceeded,
    /// Duplicate object/event/use identity, even if the records are identical.
    DuplicateIdentity,
    /// Duplicate qualified edge or repeated use-object association.
    DuplicateRelationship,
    /// Referenced event/object does not exist.
    UnknownReference,
    /// Event has no timestamp.
    MissingTimestamp,
    /// Observation window or complete interval is empty or backwards.
    InvalidInterval,
    /// Observed event is outside the declared window.
    OutsideWindow,
    /// Missing endpoints disagree with the declared censoring.
    CensoringMismatch,
    /// Occupancy supplied without an explicit interval.
    OccupancyNeedsInterval,
    /// Replacement/retraction is unsupported in this profile.
    UnsupportedCorrection,
    /// Invalid exact quantity spelling or zero denominator.
    InvalidQuantity,
    /// An incomplete interval cannot enter a complete costing selection.
    CensoredUse,
    /// An unknown quantity cannot become zero or elapsed duration.
    MissingQuantity,
    /// Assumed/simulated use cannot be relabelled as observed use.
    NonObservedUse,
    /// Transfers are contextual, not costable consumption.
    TransferNotCostable,
    /// Empty use selection cannot claim costing readiness.
    NoUses,
}

/// A fail-closed error, with an index-based path into the supplied contract.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ContractError {
    /// Stable category.
    pub code: ErrorCode,
    /// Structural path, without private/raw values.
    pub path: String,
}

impl fmt::Display for ContractError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:?} at {}", self.code, self.path)
    }
}

impl std::error::Error for ContractError {}

/// An immutable normalized contract. This is not an import qualification.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValidatedContract {
    snapshot: Snapshot,
}

impl ValidatedContract {
    /// Borrow all validated assertions and contextual relationships.
    pub fn snapshot(&self) -> &Snapshot {
        &self.snapshot
    }

    /// Require every use to be complete, explicitly quantified and observed.
    ///
    /// No partial list is returned if any use is censored, unmeasured, a
    /// transfer, assumed or simulated. These borrowed assertions are still
    /// pre-valuation: quotes, service dates, allocation and core validation
    /// remain the integrator's responsibility. No monetary result is produced.
    pub fn require_costing_ready(&self) -> Result<&[UseAssertion], ContractError> {
        if self.snapshot.uses.is_empty() {
            return fail(ErrorCode::NoUses, "/uses");
        }
        for (i, usage) in self.snapshot.uses.iter().enumerate() {
            let path = format!("/uses/{i}");
            if usage.kind == UseKind::Transfer {
                return fail(ErrorCode::TransferNotCostable, &path);
            }
            if usage.basis != Basis::Observed {
                return fail(ErrorCode::NonObservedUse, &path);
            }
            if matches!(usage.extent, Extent::Interval { censoring, .. } if censoring != Censoring::None)
            {
                return fail(ErrorCode::CensoredUse, &path);
            }
            if usage.quantity.is_none() {
                return fail(ErrorCode::MissingQuantity, &path);
            }
        }
        Ok(&self.snapshot.uses)
    }
}

fn fail<T>(code: ErrorCode, path: &str) -> Result<T, ContractError> {
    Err(ContractError {
        code,
        path: path.to_owned(),
    })
}

fn token(value: &str, path: &str, empty_ok: bool) -> Result<(), ContractError> {
    if (!empty_ok && value.is_empty())
        || value.len() > 128
        || value.trim() != value
        || value.chars().any(char::is_control)
    {
        return fail(ErrorCode::InvalidToken, path);
    }
    Ok(())
}

fn instant(value: Instant, path: &str) -> Result<(), ContractError> {
    if !(-62_135_596_800..=253_402_300_799).contains(&value.unix_seconds)
        || value.nanosecond >= 1_000_000_000
    {
        return fail(ErrorCode::InvalidInstant, path);
    }
    Ok(())
}

fn quantity(value: &Quantity, path: &str) -> Result<(), ContractError> {
    for part in [&value.numerator, &value.denominator] {
        if part.is_empty() || part.len() > 96 || !part.bytes().all(|v| v.is_ascii_digit()) {
            return fail(ErrorCode::InvalidQuantity, path);
        }
    }
    if value.denominator.bytes().all(|v| v == b'0') {
        return fail(ErrorCode::InvalidQuantity, path);
    }
    Ok(())
}

fn unique_ids<'a>(
    values: impl Iterator<Item = &'a str>,
    path: &str,
) -> Result<BTreeSet<&'a str>, ContractError> {
    let mut seen = BTreeSet::new();
    for (i, value) in values.enumerate() {
        let path = format!("{path}/{i}/id");
        token(value, &path, false)?;
        if !seen.insert(value) {
            return fail(ErrorCode::DuplicateIdentity, &path);
        }
    }
    Ok(seen)
}

fn object_reference(
    id: &str,
    objects: &BTreeSet<&str>,
    path: &str,
) -> Result<(), ContractError> {
    if !objects.contains(id) {
        return fail(ErrorCode::UnknownReference, path);
    }
    Ok(())
}

fn event_time(
    id: &str,
    events: &BTreeMap<&str, Instant>,
    path: &str,
) -> Result<Instant, ContractError> {
    events.get(id).copied().ok_or_else(|| ContractError {
        code: ErrorCode::UnknownReference,
        path: path.to_owned(),
    })
}

fn extent(
    value: &Extent,
    kind: UseKind,
    events: &BTreeMap<&str, Instant>,
    path: &str,
) -> Result<(), ContractError> {
    match value {
        Extent::Point { event_id } => {
            if kind == UseKind::Occupancy {
                return fail(ErrorCode::OccupancyNeedsInterval, path);
            }
            event_time(event_id, events, &format!("{path}/event_id"))?;
        }
        Extent::Interval {
            start_event_id,
            end_event_id,
            censoring,
        } => {
            let expected = match (start_event_id.is_some(), end_event_id.is_some()) {
                (true, true) => Censoring::None,
                (false, true) => Censoring::Left,
                (true, false) => Censoring::Right,
                (false, false) => Censoring::Both,
            };
            if *censoring != expected {
                return fail(ErrorCode::CensoringMismatch, path);
            }
            let start = start_event_id
                .as_deref()
                .map(|id| event_time(id, events, &format!("{path}/start_event_id")))
                .transpose()?;
            let end = end_event_id
                .as_deref()
                .map(|id| event_time(id, events, &format!("{path}/end_event_id")))
                .transpose()?;
            if let (Some(start), Some(end)) = (start, end)
                && start >= end
            {
                return fail(ErrorCode::InvalidInterval, path);
            }
        }
    }
    Ok(())
}

/// Validate and normalize a caller-prepared observation contract atomically.
///
/// Exact duplicate identities are rejected along with conflicting duplicates.
/// Set-like collections are sorted only after validation. Same-time events are
/// preserved, and no event order, resource quantity or allocation is inferred.
///
/// This function has no file, network, native parser, clock or monetary path.
pub fn validate_contract(mut snapshot: Snapshot) -> Result<ValidatedContract, ContractError> {
    let lengths = [
        snapshot.objects.len(),
        snapshot.events.len(),
        snapshot.relations.len(),
        snapshot.uses.len(),
    ];
    if lengths.iter().any(|v| *v > MAX_COLLECTION) || lengths.iter().sum::<usize>() > MAX_AGGREGATE
    {
        return fail(ErrorCode::LimitExceeded, "/");
    }
    let nested = snapshot
        .events
        .iter()
        .map(|v| v.objects.len())
        .chain(snapshot.uses.iter().map(|v| v.object_ids.len()));
    let mut total = 0usize;
    for count in nested {
        if count > MAX_COLLECTION || count > MAX_AGGREGATE - total {
            return fail(ErrorCode::LimitExceeded, "/");
        }
        total += count;
    }
    token(&snapshot.source.namespace, "/source/namespace", false)?;
    token(&snapshot.source.revision, "/source/revision", false)?;
    let digest = snapshot.source.content_digest.strip_prefix("sha256:");
    if !digest.is_some_and(|v| {
        v.len() == 64
            && v.bytes()
                .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
    }) {
        return fail(ErrorCode::InvalidDigest, "/source/content_digest");
    }
    instant(snapshot.window.start, "/window/start")?;
    instant(snapshot.window.end, "/window/end")?;
    if snapshot.window.start >= snapshot.window.end {
        return fail(ErrorCode::InvalidInterval, "/window");
    }
    let objects = unique_ids(snapshot.objects.iter().map(|v| v.id.as_str()), "/objects")?;
    unique_ids(snapshot.events.iter().map(|v| v.id.as_str()), "/events")?;
    unique_ids(snapshot.uses.iter().map(|v| v.id.as_str()), "/uses")?;
    for (i, object) in snapshot.objects.iter().enumerate() {
        token(&object.kind, &format!("/objects/{i}/kind"), false)?;
    }
    let mut events = BTreeMap::new();
    for (i, event) in snapshot.events.iter().enumerate() {
        let path = format!("/events/{i}");
        let at = event.at.ok_or_else(|| ContractError {
            code: ErrorCode::MissingTimestamp,
            path: format!("{path}/at"),
        })?;
        instant(at, &format!("{path}/at"))?;
        if at < snapshot.window.start || at > snapshot.window.end {
            return fail(ErrorCode::OutsideWindow, &format!("{path}/at"));
        }
        events.insert(event.id.as_str(), at);
        let mut links = BTreeSet::new();
        for (j, link) in event.objects.iter().enumerate() {
            let path = format!("{path}/objects/{j}");
            object_reference(&link.object_id, &objects, &format!("{path}/object_id"))?;
            token(&link.qualifier, &format!("{path}/qualifier"), true)?;
            if !links.insert(link) {
                return fail(ErrorCode::DuplicateRelationship, &path);
            }
        }
    }
    let mut relations = BTreeSet::new();
    for (i, relation) in snapshot.relations.iter().enumerate() {
        let path = format!("/relations/{i}");
        object_reference(&relation.from, &objects, &format!("{path}/from"))?;
        object_reference(&relation.to, &objects, &format!("{path}/to"))?;
        token(&relation.qualifier, &format!("{path}/qualifier"), true)?;
        if !relations.insert(relation) {
            return fail(ErrorCode::DuplicateRelationship, &path);
        }
    }
    for (i, usage) in snapshot.uses.iter().enumerate() {
        let path = format!("/uses/{i}");
        token(&usage.resource_id, &format!("{path}/resource_id"), false)?;
        token(&usage.unit, &format!("{path}/unit"), false)?;
        if usage.correction != Correction::Original {
            return fail(
                ErrorCode::UnsupportedCorrection,
                &format!("{path}/correction"),
            );
        }
        if let Some(value) = &usage.quantity {
            quantity(value, &format!("{path}/quantity"))?;
        }
        extent(
            &usage.extent,
            usage.kind,
            &events,
            &format!("{path}/extent"),
        )?;
        let mut seen = BTreeSet::new();
        for (j, id) in usage.object_ids.iter().enumerate() {
            let path = format!("{path}/object_ids/{j}");
            object_reference(id, &objects, &path)?;
            if !seen.insert(id) {
                return fail(ErrorCode::DuplicateRelationship, &path);
            }
        }
    }
    snapshot.objects.sort_by(|a, b| a.id.cmp(&b.id));
    snapshot.events.sort_by(|a, b| a.id.cmp(&b.id));
    for event in &mut snapshot.events {
        event.objects.sort();
    }
    snapshot.relations.sort();
    snapshot.uses.sort_by(|a, b| a.id.cmp(&b.id));
    for usage in &mut snapshot.uses {
        usage.object_ids.sort();
    }
    Ok(ValidatedContract { snapshot })
}
