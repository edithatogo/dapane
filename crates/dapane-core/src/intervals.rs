//! Explicit, bounded calendar-day exposure and rate-boundary preparation.
//!
//! The separately versioned envelope preserves parent identity before expansion.
//! All valuation and allocation are delegated to the unchanged scalar evaluator.

use std::collections::{BTreeMap, BTreeSet};

use chrono::NaiveDate;
use num_bigint::BigInt;
use num_rational::BigRational;
use serde::{Deserialize, Serialize};

use crate::{
    DapaneError, ExactNumber, MeasureKind, Rational, Report, Request, SourceRef, UnitQuote,
    Usage, MAX_JSON_BYTES, evaluate, json, numeric, validation,
};

pub const INTERVAL_SCHEMA_VERSION: &str = "0.1";
pub const INTERVAL_METHOD_VERSION: &str = "dapane-intervals-v0.1.0";
const MAX_SEGMENTS: usize = 10_000;

/// The caller explicitly assumes uniform exposure per Gregorian calendar day.
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum IntervalExposure {
    UniformCalendarDay,
}

/// One original use and a pinned, nonoverlapping quotation series.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct IntervalUsage {
    pub id: String,
    pub use_id: String,
    pub kind: MeasureKind,
    pub target: String,
    pub unit: String,
    pub quantity: ExactNumber,
    pub start: String,
    pub end: String,
    pub quote_ids: Vec<String>,
    pub exposure: IntervalExposure,
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

impl IntervalUsage {
    fn point(
        &self,
        id: String,
        use_id: String,
        quantity: ExactNumber,
        service_date: String,
        quote_id: String,
    ) -> Usage {
        Usage {
            id,
            use_id,
            kind: self.kind,
            target: self.target.clone(),
            unit: self.unit.clone(),
            quantity,
            service_date,
            quote_id,
            source: self.source.clone(),
            event_id: self.event_id.clone(),
            process_id: self.process_id.clone(),
            activity_id: self.activity_id.clone(),
            object_ids: self.object_ids.clone(),
            attribution_object_id: self.attribution_object_id.clone(),
        }
    }
}

/// Independently versioned interval envelope around an ordinary 0.1/0.2 request.
/// Allocation source IDs name original point or interval line IDs.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct IntervalRequest {
    pub schema_version: String,
    pub request: Request,
    pub intervals: Vec<IntervalUsage>,
}

/// Auditable relationship between an original use and a derived source line.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct IntervalSegment {
    pub interval_id: String,
    pub use_id: String,
    pub line_id: String,
    pub start: String,
    pub end: String,
    pub quote_id: String,
    pub quantity: Rational,
}

/// Original snapshots, explicit preparation, and a replayable scalar report.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct IntervalReport {
    pub schema_version: String,
    pub method_version: String,
    pub input_digest: String,
    pub output_digest: String,
    pub request_snapshot: Request,
    pub interval_snapshots: Vec<IntervalUsage>,
    pub segments: Vec<IntervalSegment>,
    pub expanded_request: Request,
    pub report: Report,
}

struct SelectedSegment<'a> {
    start: NaiveDate,
    end: NaiveDate,
    quote: &'a UnitQuote,
}

fn failure(code: &str, message: &str, path: &str) -> DapaneError {
    DapaneError::new(code, message, path)
}

fn inner_error(mut error: DapaneError, prefix: &str) -> DapaneError {
    error.path = format!("{prefix}{}", error.path);
    error
}

fn parent_error(mut error: DapaneError, point_count: usize) -> DapaneError {
    if let Some(rest) = error.path.strip_prefix("/usage/") {
        let (index, field) = rest.split_once('/').unwrap_or((rest, ""));
        if let Ok(index) = index.parse::<usize>()
            && index >= point_count
        {
            let field = match field {
                "service_date" => "start",
                "quote_id" => "quote_ids",
                field => field,
            };
            error.path = format!("/intervals/{}", index - point_count);
            if !field.is_empty() {
                error.path.push('/');
                error.path.push_str(field);
            }
            return error;
        }
    }
    inner_error(error, "/request")
}

/// Strict transport, including the legacy nested-request raw-field checks.
pub fn evaluate_intervals_json(input: &str) -> Result<String, DapaneError> {
    let value = json::parse_value(input)?;
    if let Some(request) = value.get("request") {
        // Preserve the raw 0.1 prohibition on capacity_allocations, even [].
        json::parse(&json::canonical(request)?)
            .map_err(|error| inner_error(error, "/request"))?;
    }
    let request: IntervalRequest = serde_json::from_value(value)
        .map_err(|error| failure("invalid_request", &error.to_string(), "/"))?;
    json::canonical(&json::value(&evaluate_intervals(&request)?)?)
}

fn select<'a>(
    usage: &IntervalUsage,
    quotes: &BTreeMap<&str, &'a UnitQuote>,
    cutoff: NaiveDate,
    path: &str,
) -> Result<Vec<SelectedSegment<'a>>, DapaneError> {
    let start = validation::date(&usage.start, &format!("{path}/start"))?;
    let end = validation::date(&usage.end, &format!("{path}/end"))?;
    if start >= end {
        return Err(failure(
            "invalid_interval",
            "Interval requires start < end",
            path,
        ));
    }
    if usage.quote_ids.is_empty() {
        return Err(failure(
            "missing_quote",
            "An interval requires an explicitly selected quotation series",
            &format!("{path}/quote_ids"),
        ));
    }
    let mut selected = Vec::with_capacity(usage.quote_ids.len());
    let mut seen = BTreeSet::new();
    let mut components = None;
    for (index, id) in usage.quote_ids.iter().enumerate() {
        let quote_path = format!("{path}/quote_ids/{index}");
        validation::text(id, &quote_path)?;
        if !seen.insert(id) {
            return Err(failure(
                "duplicate_reference",
                "Quotation selected more than once",
                &quote_path,
            ));
        }
        let quote = quotes.get(id.as_str()).copied().ok_or_else(|| {
            failure("missing_quote", "Selected quotation does not exist", &quote_path)
        })?;
        if usage.kind != quote.kind || usage.target != quote.target || usage.unit != quote.unit {
            return Err(failure(
                "quote_mismatch",
                "Interval kind, target and unit must match every selected quotation",
                &quote_path,
            ));
        }
        let covered: BTreeSet<_> = quote.components.iter().map(String::as_str).collect();
        if components.as_ref().is_some_and(|expected| expected != &covered) {
            return Err(failure(
                "component_mismatch",
                "One interval quotation series must preserve its component set",
                &quote_path,
            ));
        }
        components = Some(covered);
        if validation::date(&quote.known_from, &quote_path)? > cutoff {
            return Err(failure(
                "quote_not_known",
                "Selected quotation was not known by knowledge_cutoff",
                &quote_path,
            ));
        }
        let segment_start = start.max(validation::date(&quote.valid_from, &quote_path)?);
        let segment_end = end.min(validation::date(&quote.valid_to, &quote_path)?);
        if segment_start >= segment_end {
            return Err(failure(
                "quote_not_effective",
                "Every selected quotation must overlap the requested interval",
                &quote_path,
            ));
        }
        selected.push(SelectedSegment {
            start: segment_start,
            end: segment_end,
            quote,
        });
    }
    selected.sort_by(|a, b| {
        (&a.start, &a.end, &a.quote.id).cmp(&(&b.start, &b.end, &b.quote.id))
    });
    let mut cursor = start;
    for segment in &selected {
        if segment.start < cursor {
            return Err(failure(
                "quote_overlap",
                "Selected quotations overlap within the requested interval",
                &format!("{path}/quote_ids"),
            ));
        }
        if segment.start > cursor {
            return Err(failure(
                "quote_gap",
                "Selected quotations leave an uncovered interval",
                &format!("{path}/quote_ids"),
            ));
        }
        cursor = segment.end;
    }
    if cursor != end {
        return Err(failure(
            "quote_gap",
            "Selected quotations do not cover the interval end",
            &format!("{path}/quote_ids"),
        ));
    }
    Ok(selected)
}

fn generated_id(domain: &str, prefix: &str, parts: &[&str]) -> Result<String, DapaneError> {
    let digest = json::digest(domain, &json::value(&parts)?)?;
    let hex = digest.strip_prefix("sha256:").ok_or_else(|| {
        failure("internal_invariant", "Unexpected digest encoding", "/intervals")
    })?;
    Ok(format!("{prefix}{hex}"))
}

fn expand_sources<'a>(
    ids: &'a [String],
    children: &'a BTreeMap<String, Vec<String>>,
) -> Vec<&'a str> {
    let mut result = Vec::new();
    for id in ids {
        if let Some(generated) = children.get(id) {
            result.extend(generated.iter().map(String::as_str));
        } else {
            result.push(id.as_str());
        }
    }
    result
}

fn reserve_bytes(current: &mut usize, removed: usize, added: usize) -> Result<(), DapaneError> {
    let next = current.checked_sub(removed).and_then(|n| n.checked_add(added));
    let Some(next) = next.filter(|n| *n <= MAX_JSON_BYTES) else {
        return Err(failure(
            "input_limit",
            "Expanded request exceeds 4 MiB before materialization",
            "/intervals",
        ));
    };
    *current = next;
    Ok(())
}

fn varying_size(usage: &Usage) -> Result<usize, DapaneError> {
    Ok(json::encoded_size(&usage.id)?
        + json::encoded_size(&usage.use_id)?
        + json::encoded_size(&usage.quantity)?
        + json::encoded_size(&usage.service_date)?
        + json::encoded_size(&usage.quote_id)?)
}

fn replace_sources(
    ids: &mut Vec<String>,
    children: &BTreeMap<String, Vec<String>>,
    budget: &mut usize,
) -> Result<(), DapaneError> {
    let replacement = expand_sources(ids, children);
    reserve_bytes(budget, json::encoded_size(ids)?, json::encoded_size(&replacement)?)?;
    *ids = replacement.into_iter().map(str::to_owned).collect();
    Ok(())
}

fn normalize(request: &IntervalRequest) -> IntervalRequest {
    let mut result = request.clone();
    result.request = validation::normalize(&result.request);
    result.intervals.sort_by(|a, b| a.id.cmp(&b.id));
    for usage in &mut result.intervals {
        usage.quote_ids.sort();
        usage.object_ids.sort();
    }
    result
}

/// Split explicitly uniform exposure at pinned rate boundaries and evaluate it.
///
/// Quantity conservation is exact. Monetary rounding is per generated source
/// line, followed by the ordinary evaluator's conserving allocation rules.
/// Any failure returns no partial report. This function has no clock or IO.
pub fn evaluate_intervals(request: &IntervalRequest) -> Result<IntervalReport, DapaneError> {
    json::check_typed_size(request)?;
    if request.schema_version != INTERVAL_SCHEMA_VERSION {
        return Err(failure(
            "unsupported_schema",
            "Supported interval schema_version is 0.1",
            "/schema_version",
        ));
    }
    if request.intervals.is_empty() {
        return Err(failure(
            "invalid_interval",
            "At least one explicit interval is required",
            "/intervals",
        ));
    }
    if request.intervals.len() > MAX_SEGMENTS {
        return Err(failure("input_limit", "Too many intervals", "/intervals"));
    }
    let point_count = request.request.usage.len();
    let segment_count = request.intervals.iter().try_fold(point_count, |count, usage| {
        count.checked_add(usage.quote_ids.len()).ok_or_else(|| {
            failure("input_limit", "Interval expansion count overflow", "/intervals")
        })
    })?;
    if segment_count > MAX_SEGMENTS {
        return Err(failure(
            "input_limit",
            "Original point rows plus selected interval segments exceed 10000",
            "/intervals",
        ));
    }

    let expanded_records = [
        request.request.quotes.len(),
        segment_count,
        request.request.objects.len(),
        request.request.processes.len(),
        request.request.events.len(),
        request.request.object_relations.len(),
        request.request.allocations.len(),
        request.request.capacity_allocations.len(),
    ].iter().sum::<usize>();
    if expanded_records > 20_000 {
        return Err(failure(
            "input_limit",
            "Expanded top-level record count exceeds 20000",
            "/intervals",
        ));
    }

    // First validate all supplied quotes and original point/context records.
    // Parent allocation references are validated after representative rows exist.
    let mut preliminary = request.request.clone();
    preliminary.allocations.clear();
    preliminary.capacity_allocations.clear();
    validation::validate(&preliminary).map_err(|error| inner_error(error, "/request"))?;
    let cutoff = validation::date(&request.request.knowledge_cutoff, "/request/knowledge_cutoff")?;
    let quotes: BTreeMap<_, _> = request.request.quotes.iter().map(|q| (q.id.as_str(), q)).collect();
    let point_uses: BTreeSet<_> = request.request.usage.iter().map(|u| u.use_id.as_str()).collect();
    let mut source_line_ids: BTreeSet<_> = request.request.usage.iter().map(|u| u.id.clone()).collect();
    let mut source_use_ids = point_uses.clone();
    let mut spans = BTreeMap::new();
    for (index, usage) in request.intervals.iter().enumerate() {
        let path = format!("/intervals/{index}");
        validation::text(&usage.id, &format!("{path}/id"))?;
        validation::text(&usage.use_id, &format!("{path}/use_id"))?;
        if !source_line_ids.insert(usage.id.clone()) {
            return Err(failure(
                "duplicate_id",
                "Original point and interval line IDs must be unique",
                &format!("{path}/id"),
            ));
        }
        if point_uses.contains(usage.use_id.as_str()) {
            return Err(failure(
                "inconsistent_use",
                "One underlying use cannot be supplied as both a point and an interval",
                &format!("{path}/use_id"),
            ));
        }
        if let Some((start, end)) = spans.insert(
            usage.use_id.as_str(),
            (usage.start.as_str(), usage.end.as_str()),
        )
            && (start != usage.start || end != usage.end)
        {
            return Err(failure(
                "inconsistent_use",
                "Interval rows sharing use_id must have identical start and end",
                &format!("{path}/use_id"),
            ));
        }
        source_use_ids.insert(usage.use_id.as_str());
    }

    let mut parent = request.request.clone();
    let mut selections = Vec::with_capacity(request.intervals.len());
    for (index, usage) in request.intervals.iter().enumerate() {
        let path = format!("/intervals/{index}");
        let selected = select(usage, &quotes, cutoff, &path)?;
        parent.usage.push(usage.point(
            usage.id.clone(),
            usage.use_id.clone(),
            usage.quantity.clone(),
            usage.start.clone(),
            selected[0].quote.id.clone(),
        ));
        selections.push(selected);
    }
    // Reuse exact quantity, resolved context, component and pool exclusivity
    // validation on the ORIGINAL identities before generating child identities.
    json::check_typed_size(&parent)?;
    validation::validate(&parent).map_err(|error| parent_error(error, point_count))?;

    // Only small generated identifiers are materialized in this prepass.
    // Parent validation ensures each pooled source is selected at most once.
    let mut children = BTreeMap::new();
    let mut generated_lines = BTreeSet::new();
    for (usage, selected) in request.intervals.iter().zip(&selections) {
        let ids = selected.iter().map(|segment| {
            generated_id(
                "dapane:interval-line:0.1\n",
                "il-",
                &[&usage.id, &segment.start.to_string(), &segment.end.to_string()],
            )
        }).collect::<Result<Vec<_>, _>>()?;
        for id in &ids {
            if source_line_ids.contains(id) || !generated_lines.insert(id.clone()) {
                return Err(failure(
                    "identifier_collision",
                    "Generated line identity collides with another identity",
                    "/intervals",
                ));
            }
        }
        children.insert(usage.id.clone(), ids);
    }
    let mut expanded = request.request.clone();
    let mut expanded_size = json::encoded_size(&expanded)?;
    // Apply all shrinking replacements first, so temporary ordering cannot reject
    // a final request that fits the byte bound. Each source belongs to one pool.
    for shrinking in [true, false] {
        for allocation in &mut expanded.allocations {
            let replacement = expand_sources(&allocation.source_line_ids, &children);
            let smaller = json::encoded_size(&replacement)?
                < json::encoded_size(&allocation.source_line_ids)?;
            if smaller == shrinking {
                replace_sources(&mut allocation.source_line_ids, &children, &mut expanded_size)?;
            }
        }
        for allocation in &mut expanded.capacity_allocations {
            let replacement = expand_sources(&allocation.source_line_ids, &children);
            let smaller = json::encoded_size(&replacement)?
                < json::encoded_size(&allocation.source_line_ids)?;
            if smaller == shrinking {
                replace_sources(&mut allocation.source_line_ids, &children, &mut expanded_size)?;
            }
        }
    }
    let mut segments = Vec::with_capacity(segment_count - point_count);
    let mut generated_uses = BTreeMap::new();
    for (index, (usage, selected)) in request.intervals.iter().zip(selections).enumerate() {
        let path = format!("/intervals/{index}/quantity");
        let quantity = numeric::parse(&usage.quantity, &path)?;
        let start = validation::date(&usage.start, &format!("/intervals/{index}/start"))?;
        let end = validation::date(&usage.end, &format!("/intervals/{index}/end"))?;
        let total_days = (end - start).num_days();
        let template = &parent.usage[point_count + index];
        let fixed_size = json::encoded_size(template)? - varying_size(template)?;
        for segment in selected {
            let start = segment.start.to_string();
            let end = segment.end.to_string();
            let days = (segment.end - segment.start).num_days();
            let exact = numeric::bounded(
                &quantity * BigRational::new(BigInt::from(days), BigInt::from(total_days)),
                &path,
            )?;
            let quantity_wire = numeric::wire(&exact);
            let transport = ExactNumber::Rational(quantity_wire.clone());
            // Expanded requests are public replay inputs and must obey the
            // same 96-digit input limits as externally supplied point rows.
            numeric::parse(&transport, &path)?;
            let line_id = generated_id(
                "dapane:interval-line:0.1\n",
                "il-",
                &[&usage.id, &start, &end],
            )?;
            let use_id = generated_id(
                "dapane:interval-use:0.1\n",
                "iu-",
                &[&usage.use_id, &start, &end],
            )?;
            if source_use_ids.contains(use_id.as_str()) {
                return Err(failure(
                    "identifier_collision",
                    "Generated use identity collides with a supplied use identity",
                    "/intervals",
                ));
            }
            let identity = (usage.use_id.clone(), start.clone(), end.clone());
            if let Some(previous) = generated_uses.insert(use_id.clone(), identity.clone())
                && previous != identity
            {
                return Err(failure(
                    "identifier_collision",
                    "Distinct parent segments share a generated use identity",
                    "/intervals",
                ));
            }
            let row_size = fixed_size
                + json::encoded_size(&line_id)?
                + json::encoded_size(&use_id)?
                + json::encoded_size(&transport)?
                + json::encoded_size(&start)?
                + json::encoded_size(&segment.quote.id)?;
            reserve_bytes(
                &mut expanded_size,
                0,
                row_size + usize::from(!expanded.usage.is_empty()),
            )?;
            // Source/context cloning happens only after its exact byte budget fits.
            expanded.usage.push(usage.point(
                line_id.clone(),
                use_id,
                transport,
                start.clone(),
                segment.quote.id.clone(),
            ));
            segments.push(IntervalSegment {
                interval_id: usage.id.clone(),
                use_id: usage.use_id.clone(),
                line_id,
                start,
                end,
                quote_id: segment.quote.id.clone(),
                quantity: quantity_wire,
            });
        }
    }
    if json::encoded_size(&expanded)? != expanded_size {
        return Err(failure(
            "internal_invariant",
            "Expanded byte accounting disagrees with serialized request",
            "/intervals",
        ));
    }
    let expanded = validation::normalize(&expanded);
    // This checks expanded byte/record/numeric limits and computes all money
    // through the existing exact kernel, including capacity residuals.
    let report = evaluate(&expanded).map_err(|error| inner_error(error, "/expanded_request"))?;
    let normalized = normalize(request);
    let input_digest = json::digest("dapane:interval-input:0.1\n", &json::value(&normalized)?)?;
    segments.sort_by(|a, b| {
        (&a.interval_id, &a.start, &a.end, &a.quote_id)
            .cmp(&(&b.interval_id, &b.start, &b.end, &b.quote_id))
    });
    let mut result = IntervalReport {
        schema_version: INTERVAL_SCHEMA_VERSION.to_owned(),
        method_version: INTERVAL_METHOD_VERSION.to_owned(),
        input_digest,
        output_digest: String::new(),
        request_snapshot: normalized.request,
        interval_snapshots: normalized.intervals,
        segments,
        expanded_request: expanded,
        report,
    };
    let mut value = json::value(&result)?;
    value.as_object_mut().ok_or_else(|| {
        failure("internal_invariant", "Interval report is not an object", "/")
    })?.remove("output_digest");
    result.output_digest = json::digest("dapane:interval-output:0.1\n", &value)?;
    Ok(result)
}
