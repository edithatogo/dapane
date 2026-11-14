//! Exact interval exposure with explicit source selection and parent-line rounding.

use std::collections::{BTreeMap, BTreeSet};

use chrono::NaiveDate;
use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::Zero;

use crate::{
    DapaneError, IntervalUsage, Request, UnitQuote, Usage, ValuationSegment, numeric, validation,
};

const MAX_SEGMENTS: usize = 20_000;

struct Selection<'a> {
    start: NaiveDate,
    end: NaiveDate,
    quote: &'a UnitQuote,
}

fn schedule<'a>(
    usage: &IntervalUsage,
    quotes: &BTreeMap<&str, &'a UnitQuote>,
    cutoff: &str,
    path: &str,
) -> Result<Vec<Selection<'a>>, DapaneError> {
    let start = validation::date(&usage.start_date, &format!("{path}/start_date"))?;
    let end = validation::date(&usage.end_date, &format!("{path}/end_date"))?;
    if start >= end {
        return Err(DapaneError::new(
            "invalid_interval",
            "Interval usage requires start_date < end_date",
            path,
        ));
    }
    validation::collection(usage.quote_ids.len(), &format!("{path}/quote_ids"))?;
    if usage.quote_ids.is_empty() {
        return Err(DapaneError::new(
            "missing_quote",
            "An interval requires an explicitly selected quotation schedule",
            &format!("{path}/quote_ids"),
        ));
    }
    let mut selected = BTreeSet::new();
    let mut selections = Vec::with_capacity(usage.quote_ids.len());
    let mut components = None;
    for (index, id) in usage.quote_ids.iter().enumerate() {
        let quote_path = format!("{path}/quote_ids/{index}");
        validation::text(id, &quote_path)?;
        if !selected.insert(id) {
            return Err(DapaneError::new(
                "duplicate_reference",
                "Repeated interval quotation reference",
                &quote_path,
            ));
        }
        let quote = *quotes.get(id.as_str()).ok_or_else(|| {
            DapaneError::new("missing_quote", "Unknown interval quotation", &quote_path)
        })?;
        if usage.kind != quote.kind || usage.target != quote.target || usage.unit != quote.unit {
            return Err(DapaneError::new(
                "quote_mismatch",
                "Interval kind, target and unit must match every selected quotation",
                &quote_path,
            ));
        }
        if quote.known_from.as_str() > cutoff {
            return Err(DapaneError::new(
                "quote_not_known",
                "Selected interval quotation was not known by knowledge_cutoff",
                &quote_path,
            ));
        }
        let current: BTreeSet<_> = quote.components.iter().map(String::as_str).collect();
        if let Some(first) = &components {
            if first != &current {
                return Err(DapaneError::new(
                    "inconsistent_components",
                    "Every rate in an interval schedule must cover the same components",
                    &quote_path,
                ));
            }
        } else {
            components = Some(current);
        }
        let segment_start = start.max(validation::date(&quote.valid_from, &quote_path)?);
        let segment_end = end.min(validation::date(&quote.valid_to, &quote_path)?);
        if segment_start >= segment_end {
            return Err(DapaneError::new(
                "invalid_interval_quote",
                "Every selected quotation must intersect the usage interval",
                &quote_path,
            ));
        }
        selections.push(Selection {
            start: segment_start,
            end: segment_end,
            quote,
        });
    }
    selections.sort_by(|a, b| (a.start, a.end, &a.quote.id).cmp(&(b.start, b.end, &b.quote.id)));
    let mut cursor = start;
    for selection in &selections {
        if selection.start < cursor {
            return Err(DapaneError::new(
                "interval_overlap",
                "Selected quotation periods overlap within the usage interval",
                &format!("{path}/quote_ids"),
            ));
        }
        if selection.start > cursor {
            return Err(DapaneError::new(
                "interval_gap",
                "Selected quotations leave part of the usage interval uncovered",
                &format!("{path}/quote_ids"),
            ));
        }
        cursor = selection.end;
    }
    if cursor != end {
        return Err(DapaneError::new(
            "interval_gap",
            "Selected quotations do not cover the end of the usage interval",
            &format!("{path}/quote_ids"),
        ));
    }
    Ok(selections)
}

/// Project only parent identity/context for the shared ledger validator. These
/// records are never evaluated, serialized, or substituted for the source input.
/// The complete schedule is checked before its first quote is used as a proxy
/// for the invariant component set. All arithmetic remains in `evaluate` below.
pub(crate) fn projections(
    request: &Request,
    quotes: &BTreeMap<&str, &UnitQuote>,
) -> Result<Vec<Usage>, DapaneError> {
    let selected_count = request
        .interval_usage
        .iter()
        .try_fold(0usize, |count, usage| {
            count.checked_add(usage.quote_ids.len()).ok_or_else(|| {
                DapaneError::new(
                    "input_limit",
                    "Interval schedule count overflow",
                    "/interval_usage",
                )
            })
        })?;
    if selected_count > MAX_SEGMENTS {
        return Err(DapaneError::new(
            "input_limit",
            "Aggregate interval quote selections exceed 20000",
            "/interval_usage",
        ));
    }
    let point_uses: BTreeSet<_> = request
        .usage
        .iter()
        .map(|usage| usage.use_id.as_str())
        .collect();
    let mut interval_uses: BTreeMap<&str, &IntervalUsage> = BTreeMap::new();
    let mut projections = Vec::with_capacity(request.interval_usage.len());
    for (index, usage) in request.interval_usage.iter().enumerate() {
        let path = format!("/interval_usage/{index}");
        validation::text(&usage.id, &format!("{path}/id"))?;
        validation::text(&usage.use_id, &format!("{path}/use_id"))?;
        if point_uses.contains(usage.use_id.as_str()) {
            return Err(DapaneError::new(
                "inconsistent_use",
                "A use_id cannot describe both point-date and interval exposure",
                &format!("{path}/use_id"),
            ));
        }
        if let Some(first) = interval_uses.get(usage.use_id.as_str()) {
            if first.start_date != usage.start_date
                || first.end_date != usage.end_date
                || first.exposure != usage.exposure
            {
                return Err(DapaneError::new(
                    "inconsistent_use",
                    "Lines sharing use_id must have identical intervals and exposure assumptions",
                    &format!("{path}/use_id"),
                ));
            }
        } else {
            interval_uses.insert(&usage.use_id, usage);
        }
        let selections = schedule(usage, quotes, &request.knowledge_cutoff, &path)?;
        let first = selections.first().ok_or_else(|| {
            DapaneError::new("missing_quote", "Interval schedule is empty", &path)
        })?;
        projections.push(Usage {
            id: usage.id.clone(),
            use_id: usage.use_id.clone(),
            kind: usage.kind,
            target: usage.target.clone(),
            unit: usage.unit.clone(),
            quantity: usage.quantity.clone(),
            service_date: usage.start_date.clone(),
            quote_id: first.quote.id.clone(),
            source: usage.source.clone(),
            event_id: usage.event_id.clone(),
            process_id: usage.process_id.clone(),
            activity_id: usage.activity_id.clone(),
            object_ids: usage.object_ids.clone(),
            attribution_object_id: usage.attribution_object_id.clone(),
        });
    }
    Ok(projections)
}

pub(crate) struct IntervalValue {
    pub quantity: BigRational,
    pub exact: BigRational,
    pub components: Vec<String>,
    pub segments: Vec<ValuationSegment>,
}

/// Partition on selected rate boundaries, never by iterating individual dates.
/// Day ratios multiply the exact total quantity; no segment is rounded.
pub(crate) fn evaluate(
    usage: &IntervalUsage,
    quotes: &BTreeMap<&str, &UnitQuote>,
    cutoff: &str,
    path: &str,
) -> Result<IntervalValue, DapaneError> {
    let selections = schedule(usage, quotes, cutoff, path)?;
    let start = validation::date(&usage.start_date, path)?;
    let end = validation::date(&usage.end_date, path)?;
    let total_days = BigInt::from((end - start).num_days());
    let quantity = numeric::parse(&usage.quantity, &format!("{path}/quantity"))?;
    let mut exact = BigRational::zero();
    let mut accounted_quantity = BigRational::zero();
    let mut segments = Vec::with_capacity(selections.len());
    let components = selections
        .first()
        .ok_or_else(|| DapaneError::new("missing_quote", "Empty interval schedule", path))?
        .quote
        .components
        .clone();
    for selection in selections {
        let days = BigInt::from((selection.end - selection.start).num_days());
        let segment_quantity =
            numeric::bounded(&quantity * BigRational::new(days, total_days.clone()), path)?;
        let amount = numeric::parse(&selection.quote.amount, path)?;
        let denominator = numeric::parse(&selection.quote.per_quantity, path)?;
        let segment_exact = numeric::bounded(&segment_quantity * amount / denominator, path)?;
        accounted_quantity = numeric::bounded(accounted_quantity + &segment_quantity, path)?;
        exact = numeric::bounded(exact + &segment_exact, path)?;
        segments.push(ValuationSegment {
            quote_id: selection.quote.id.clone(),
            start_date: selection.start.to_string(),
            end_date: selection.end.to_string(),
            quantity: numeric::wire(&segment_quantity),
            exact: numeric::wire(&segment_exact),
        });
    }
    if accounted_quantity != quantity {
        return Err(DapaneError::new(
            "internal_invariant",
            "Interval segments did not conserve the parent quantity",
            path,
        ));
    }
    Ok(IntervalValue {
        quantity,
        exact,
        components,
        segments,
    })
}
