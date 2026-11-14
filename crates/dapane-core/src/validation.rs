use std::collections::{BTreeMap, BTreeSet};

use chrono::{Datelike, NaiveDate};
use num_rational::BigRational;
use num_traits::Zero;

use crate::{DapaneError, Event, Request, SourceRef, Usage, numeric};

const MAX_COLLECTION: usize = 10_000;
const MAX_TOTAL_RECORDS: usize = 20_000;

pub(crate) fn text(value: &str, path: &str) -> Result<(), DapaneError> {
    if value.is_empty()
        || value.len() > 128
        || value.trim() != value
        || value.chars().any(char::is_control)
    {
        return Err(DapaneError::new(
            "invalid_identifier",
            "Expected a nonempty, trimmed identifier of at most 128 UTF-8 bytes without control characters",
            path,
        ));
    }
    Ok(())
}

fn collection(size: usize, path: &str) -> Result<(), DapaneError> {
    if size > MAX_COLLECTION {
        return Err(DapaneError::new(
            "input_limit",
            "Collection exceeds 10000 records",
            path,
        ));
    }
    Ok(())
}

fn date(value: &str, path: &str) -> Result<NaiveDate, DapaneError> {
    let bytes = value.as_bytes();
    let valid_shape = bytes.len() == 10
        && bytes[4] == b'-'
        && bytes[7] == b'-'
        && bytes
            .iter()
            .enumerate()
            .all(|(index, byte)| index == 4 || index == 7 || byte.is_ascii_digit());
    if !valid_shape {
        return Err(DapaneError::new(
            "invalid_date",
            "Expected a calendar date in YYYY-MM-DD format",
            path,
        ));
    }
    let parsed = NaiveDate::parse_from_str(value, "%Y-%m-%d")
        .map_err(|_| DapaneError::new("invalid_date", "Invalid calendar date", path))?;
    if !(1..=9999).contains(&parsed.year()) {
        return Err(DapaneError::new(
            "invalid_date",
            "Year must be between 0001 and 9999",
            path,
        ));
    }
    Ok(parsed)
}

fn currency(value: &str, path: &str) -> Result<(), DapaneError> {
    if value.len() != 3 || !value.bytes().all(|v| v.is_ascii_uppercase()) {
        return Err(DapaneError::new(
            "invalid_currency",
            "Currency must contain three uppercase ASCII letters",
            path,
        ));
    }
    Ok(())
}

fn year(value: u16, path: &str) -> Result<(), DapaneError> {
    if !(1..=9999).contains(&value) {
        return Err(DapaneError::new(
            "invalid_price_year",
            "Price year must be between 1 and 9999",
            path,
        ));
    }
    Ok(())
}

fn source(value: &SourceRef, path: &str) -> Result<(), DapaneError> {
    text(&value.id, &format!("{path}/id"))?;
    text(&value.version, &format!("{path}/version"))?;
    if let Some(digest) = &value.content_digest {
        let Some(hex) = digest.strip_prefix("sha256:") else {
            return Err(DapaneError::new(
                "invalid_source_digest",
                "Expected sha256: and 64 lowercase hexadecimal characters",
                &format!("{path}/content_digest"),
            ));
        };
        if hex.len() != 64
            || !hex
                .bytes()
                .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
        {
            return Err(DapaneError::new(
                "invalid_source_digest",
                "Expected sha256: and 64 lowercase hexadecimal characters",
                &format!("{path}/content_digest"),
            ));
        }
    }
    if let Some(locator) = &value.locator
        && (locator.is_empty()
            || locator.len() > 2048
            || locator.trim() != locator
            || locator.chars().any(char::is_control))
    {
        return Err(DapaneError::new(
            "invalid_source_locator",
            "Source locator must be nonempty, trimmed, at most 2048 bytes and contain no control characters",
            &format!("{path}/locator"),
        ));
    }
    Ok(())
}

fn unique_ids<'a>(
    ids: impl IntoIterator<Item = &'a str>,
    path: &str,
) -> Result<BTreeSet<&'a str>, DapaneError> {
    let mut seen = BTreeSet::new();
    for (index, id) in ids.into_iter().enumerate() {
        text(id, &format!("{path}/{index}/id"))?;
        if !seen.insert(id) {
            return Err(DapaneError::new(
                "duplicate_id",
                &format!("Duplicate identifier {id}"),
                &format!("{path}/{index}/id"),
            ));
        }
    }
    Ok(seen)
}

fn reference(value: &str, registry: &BTreeSet<&str>, path: &str) -> Result<(), DapaneError> {
    text(value, path)?;
    if !registry.contains(value) {
        return Err(DapaneError::new(
            "unknown_reference",
            &format!("Unknown reference {value}"),
            path,
        ));
    }
    Ok(())
}

fn object_refs(values: &[String], objects: &BTreeSet<&str>, path: &str) -> Result<(), DapaneError> {
    collection(values.len(), path)?;
    let mut seen = BTreeSet::new();
    for (index, value) in values.iter().enumerate() {
        reference(value, objects, &format!("{path}/{index}"))?;
        if !seen.insert(value) {
            return Err(DapaneError::new(
                "duplicate_reference",
                "Repeated object reference",
                &format!("{path}/{index}"),
            ));
        }
    }
    Ok(())
}

fn context<'a>(
    usage: &'a Usage,
    events: &'a BTreeMap<&str, &Event>,
) -> (Option<&'a str>, Option<&'a str>) {
    let event = usage.event_id.as_deref().and_then(|id| events.get(id));
    (
        usage
            .process_id
            .as_deref()
            .or_else(|| event.and_then(|e| e.process_id.as_deref())),
        usage
            .activity_id
            .as_deref()
            .or_else(|| event.and_then(|e| e.activity_id.as_deref())),
    )
}

fn same_use(
    first: &Usage,
    next: &Usage,
    first_quantity: &BigRational,
    next_quantity: &BigRational,
    events: &BTreeMap<&str, &Event>,
) -> bool {
    first.kind == next.kind
        && first.target == next.target
        && first.unit == next.unit
        && first_quantity == next_quantity
        && first.service_date == next.service_date
        && first.source == next.source
        && first.event_id == next.event_id
        && context(first, events) == context(next, events)
        && first.object_ids.iter().collect::<BTreeSet<_>>()
            == next.object_ids.iter().collect::<BTreeSet<_>>()
        && first.attribution_object_id == next.attribution_object_id
}

pub(crate) fn validate(request: &Request) -> Result<(), DapaneError> {
    if request.schema_version != "0.1" {
        return Err(DapaneError::new(
            "unsupported_schema",
            "Supported schema_version is 0.1",
            "/schema_version",
        ));
    }
    text(&request.run_id, "/run_id")?;
    let cutoff = date(&request.knowledge_cutoff, "/knowledge_cutoff")?;
    let sizes = [
        (request.quotes.len(), "/quotes"),
        (request.usage.len(), "/usage"),
        (request.objects.len(), "/objects"),
        (request.processes.len(), "/processes"),
        (request.events.len(), "/events"),
        (request.object_relations.len(), "/object_relations"),
        (request.allocations.len(), "/allocations"),
    ];
    for (size, path) in sizes {
        collection(size, path)?;
    }
    if sizes.iter().map(|(size, _)| size).sum::<usize>() > MAX_TOTAL_RECORDS {
        return Err(DapaneError::new(
            "input_limit",
            "Total top-level record count exceeds 20000",
            "/",
        ));
    }
    let policy = &request.policy;
    text(&policy.id, "/policy/id")?;
    text(&policy.version, "/policy/version")?;
    text(&policy.perspective, "/policy/perspective")?;
    currency(&policy.currency, "/policy/currency")?;
    year(policy.price_year, "/policy/price_year")?;
    if policy.rounding.scale > 12 {
        return Err(DapaneError::new(
            "unsupported_rounding",
            "Rounding scale must be between 0 and 12",
            "/policy/rounding/scale",
        ));
    }

    let objects = unique_ids(request.objects.iter().map(|v| v.id.as_str()), "/objects")?;
    for (index, object) in request.objects.iter().enumerate() {
        text(&object.kind, &format!("/objects/{index}/kind"))?;
    }
    let processes = unique_ids(
        request.processes.iter().map(|v| v.id.as_str()),
        "/processes",
    )?;
    for (index, process) in request.processes.iter().enumerate() {
        text(&process.model_id, &format!("/processes/{index}/model_id"))?;
        text(
            &process.model_version,
            &format!("/processes/{index}/model_version"),
        )?;
    }
    let event_ids = unique_ids(request.events.iter().map(|v| v.id.as_str()), "/events")?;
    let events: BTreeMap<_, _> = request.events.iter().map(|e| (e.id.as_str(), e)).collect();
    for (index, event) in request.events.iter().enumerate() {
        let path = format!("/events/{index}");
        date(&event.occurred_on, &format!("{path}/occurred_on"))?;
        if let Some(process_id) = &event.process_id {
            reference(process_id, &processes, &format!("{path}/process_id"))?;
        }
        if let Some(activity_id) = &event.activity_id {
            text(activity_id, &format!("{path}/activity_id"))?;
            if event.process_id.is_none() {
                return Err(DapaneError::new(
                    "invalid_context",
                    "An event activity requires a process instance",
                    &format!("{path}/activity_id"),
                ));
            }
        }
        object_refs(&event.object_ids, &objects, &format!("{path}/object_ids"))?;
    }
    let mut relations = BTreeSet::new();
    for (index, relation) in request.object_relations.iter().enumerate() {
        let path = format!("/object_relations/{index}");
        reference(
            &relation.from_object_id,
            &objects,
            &format!("{path}/from_object_id"),
        )?;
        reference(
            &relation.to_object_id,
            &objects,
            &format!("{path}/to_object_id"),
        )?;
        text(&relation.relationship, &format!("{path}/relationship"))?;
        if !relations.insert((
            &relation.from_object_id,
            &relation.to_object_id,
            &relation.relationship,
        )) {
            return Err(DapaneError::new(
                "duplicate_relation",
                "Repeated object relationship",
                &path,
            ));
        }
    }

    unique_ids(request.quotes.iter().map(|q| q.id.as_str()), "/quotes")?;
    let quotes: BTreeMap<_, _> = request.quotes.iter().map(|q| (q.id.as_str(), q)).collect();
    for (index, quote) in request.quotes.iter().enumerate() {
        let path = format!("/quotes/{index}");
        text(&quote.target, &format!("{path}/target"))?;
        text(&quote.unit, &format!("{path}/unit"))?;
        numeric::parse(&quote.amount, &format!("{path}/amount"))?;
        if numeric::parse(&quote.per_quantity, &format!("{path}/per_quantity"))?.is_zero() {
            return Err(DapaneError::new(
                "invalid_quote",
                "Quotation per_quantity must be positive",
                &format!("{path}/per_quantity"),
            ));
        }
        currency(&quote.currency, &format!("{path}/currency"))?;
        year(quote.price_year, &format!("{path}/price_year"))?;
        if quote.currency != policy.currency
            || quote.price_year != policy.price_year
            || quote.basis != policy.basis
        {
            return Err(DapaneError::new(
                "valuation_mismatch",
                "Quote currency, price year and valuation basis must match the policy",
                &path,
            ));
        }
        collection(quote.components.len(), &format!("{path}/components"))?;
        if quote.components.is_empty() {
            return Err(DapaneError::new(
                "invalid_components",
                "At least one explicit component is required",
                &format!("{path}/components"),
            ));
        }
        let mut seen = BTreeSet::new();
        for (component_index, component) in quote.components.iter().enumerate() {
            text(component, &format!("{path}/components/{component_index}"))?;
            if !seen.insert(component) {
                return Err(DapaneError::new(
                    "duplicate_component",
                    "Repeated quotation component",
                    &format!("{path}/components/{component_index}"),
                ));
            }
        }
        let start = date(&quote.valid_from, &format!("{path}/valid_from"))?;
        let end = date(&quote.valid_to, &format!("{path}/valid_to"))?;
        if start >= end {
            return Err(DapaneError::new(
                "invalid_interval",
                "Quotation interval must have valid_from < valid_to",
                &path,
            ));
        }
        date(&quote.known_from, &format!("{path}/known_from"))?;
        source(&quote.source, &format!("{path}/source"))?;
    }

    unique_ids(request.usage.iter().map(|u| u.id.as_str()), "/usage")?;
    let usage_by_id: BTreeMap<_, _> = request.usage.iter().map(|u| (u.id.as_str(), u)).collect();
    let mut uses: BTreeMap<&str, (&Usage, BigRational, BTreeSet<&str>)> = BTreeMap::new();
    for (index, usage) in request.usage.iter().enumerate() {
        let path = format!("/usage/{index}");
        text(&usage.use_id, &format!("{path}/use_id"))?;
        text(&usage.target, &format!("{path}/target"))?;
        text(&usage.unit, &format!("{path}/unit"))?;
        text(&usage.quote_id, &format!("{path}/quote_id"))?;
        let quantity = numeric::parse(&usage.quantity, &format!("{path}/quantity"))?;
        let service_date = date(&usage.service_date, &format!("{path}/service_date"))?;
        let quote = quotes.get(usage.quote_id.as_str()).ok_or_else(|| {
            DapaneError::new(
                "missing_quote",
                "No quotation has the selected quote_id",
                &format!("{path}/quote_id"),
            )
        })?;
        if usage.kind != quote.kind || usage.target != quote.target || usage.unit != quote.unit {
            return Err(DapaneError::new(
                "quote_mismatch",
                "Usage kind, target and unit must match the selected quotation exactly",
                &path,
            ));
        }
        if service_date < date(&quote.valid_from, &path)?
            || service_date >= date(&quote.valid_to, &path)?
        {
            return Err(DapaneError::new(
                "quote_not_effective",
                "Service date is outside the selected quotation's half-open interval",
                &format!("{path}/service_date"),
            ));
        }
        if date(&quote.known_from, &path)? > cutoff {
            return Err(DapaneError::new(
                "quote_not_known",
                "Selected quotation was not known by knowledge_cutoff",
                &format!("{path}/quote_id"),
            ));
        }
        source(&usage.source, &format!("{path}/source"))?;
        if let Some(event_id) = &usage.event_id {
            reference(event_id, &event_ids, &format!("{path}/event_id"))?;
        }
        if let Some(process_id) = &usage.process_id {
            reference(process_id, &processes, &format!("{path}/process_id"))?;
        }
        if let Some(activity_id) = &usage.activity_id {
            text(activity_id, &format!("{path}/activity_id"))?;
        }
        if let Some(event) = usage.event_id.as_deref().and_then(|id| events.get(id)) {
            if let (Some(explicit), Some(inherited)) = (&usage.process_id, &event.process_id)
                && explicit != inherited
            {
                return Err(DapaneError::new(
                    "invalid_context",
                    "Usage process disagrees with its event's process",
                    &format!("{path}/process_id"),
                ));
            }
            if let (Some(explicit), Some(inherited)) = (&usage.activity_id, &event.activity_id)
                && explicit != inherited
            {
                return Err(DapaneError::new(
                    "invalid_context",
                    "Usage activity disagrees with its event's activity",
                    &format!("{path}/activity_id"),
                ));
            }
        }
        let (process, activity) = context(usage, &events);
        if activity.is_some() && process.is_none() {
            return Err(DapaneError::new(
                "invalid_context",
                "An activity requires a process instance, directly or through its event",
                &format!("{path}/activity_id"),
            ));
        }
        object_refs(&usage.object_ids, &objects, &format!("{path}/object_ids"))?;
        if let Some(object_id) = &usage.attribution_object_id {
            reference(
                object_id,
                &objects,
                &format!("{path}/attribution_object_id"),
            )?;
        }
        if let Some((first, first_quantity, components)) = uses.get_mut(usage.use_id.as_str()) {
            if !same_use(first, usage, first_quantity, &quantity, &events) {
                return Err(DapaneError::new(
                    "inconsistent_use",
                    "Lines sharing use_id must describe the same underlying quantity, source and context",
                    &format!("{path}/use_id"),
                ));
            }
            for component in &quote.components {
                if !components.insert(component) {
                    return Err(DapaneError::new(
                        "component_overlap",
                        &format!(
                            "Underlying use {} already includes component {component}",
                            usage.use_id
                        ),
                        &format!("{path}/quote_id"),
                    ));
                }
            }
        } else {
            uses.insert(
                &usage.use_id,
                (
                    usage,
                    quantity,
                    quote.components.iter().map(String::as_str).collect(),
                ),
            );
        }
    }

    unique_ids(
        request.allocations.iter().map(|a| a.id.as_str()),
        "/allocations",
    )?;
    let mut pooled = BTreeSet::new();
    for (index, allocation) in request.allocations.iter().enumerate() {
        let path = format!("/allocations/{index}");
        collection(
            allocation.source_line_ids.len(),
            &format!("{path}/source_line_ids"),
        )?;
        collection(allocation.weights.len(), &format!("{path}/weights"))?;
        if allocation.source_line_ids.is_empty() || allocation.weights.is_empty() {
            return Err(DapaneError::new(
                "invalid_allocation",
                "An allocation requires source lines and recipient weights",
                &path,
            ));
        }
        for (line_index, line_id) in allocation.source_line_ids.iter().enumerate() {
            let line_path = format!("{path}/source_line_ids/{line_index}");
            text(line_id, &line_path)?;
            let usage = usage_by_id.get(line_id.as_str()).ok_or_else(|| {
                DapaneError::new(
                    "unknown_reference",
                    "Allocation refers to an unknown source line",
                    &line_path,
                )
            })?;
            if usage.attribution_object_id.is_some() {
                return Err(DapaneError::new(
                    "allocation_overlap",
                    "A directly attributed line cannot also be pooled",
                    &line_path,
                ));
            }
            if !pooled.insert(line_id) {
                return Err(DapaneError::new(
                    "allocation_overlap",
                    "Source line appears in more than one allocation entry",
                    &line_path,
                ));
            }
        }
        let mut recipients = BTreeSet::new();
        let mut has_positive_weight = false;
        for (weight_index, weight) in allocation.weights.iter().enumerate() {
            let weight_path = format!("{path}/weights/{weight_index}");
            reference(
                &weight.object_id,
                &objects,
                &format!("{weight_path}/object_id"),
            )?;
            if !recipients.insert(&weight.object_id) {
                return Err(DapaneError::new(
                    "duplicate_recipient",
                    "Object occurs twice in the allocation weights",
                    &format!("{weight_path}/object_id"),
                ));
            }
            has_positive_weight |=
                !numeric::parse(&weight.weight, &format!("{weight_path}/weight"))?.is_zero();
        }
        if !has_positive_weight {
            return Err(DapaneError::new(
                "zero_weights",
                "At least one allocation weight must be positive",
                &format!("{path}/weights"),
            ));
        }
    }
    Ok(())
}

pub(crate) fn normalize(request: &Request) -> Request {
    let mut result = request.clone();
    result.quotes.sort_by(|a, b| a.id.cmp(&b.id));
    for quote in &mut result.quotes {
        quote.components.sort();
    }
    result.usage.sort_by(|a, b| a.id.cmp(&b.id));
    for usage in &mut result.usage {
        usage.object_ids.sort();
    }
    result.objects.sort_by(|a, b| a.id.cmp(&b.id));
    result.processes.sort_by(|a, b| a.id.cmp(&b.id));
    result.events.sort_by(|a, b| a.id.cmp(&b.id));
    for event in &mut result.events {
        event.object_ids.sort();
    }
    result.object_relations.sort_by(|a, b| {
        (&a.from_object_id, &a.to_object_id, &a.relationship).cmp(&(
            &b.from_object_id,
            &b.to_object_id,
            &b.relationship,
        ))
    });
    result.allocations.sort_by(|a, b| a.id.cmp(&b.id));
    for allocation in &mut result.allocations {
        allocation.source_line_ids.sort();
        allocation
            .weights
            .sort_by(|a, b| a.object_id.cmp(&b.object_id));
    }
    result
}
