//! Exact microcosting and valuation, independent of simulation and language wrappers.
//!
//! The supported contract is documented in docs/contract-v0.1.md. All monetary
//! arithmetic uses bounded arbitrary-precision rational numbers; observations and
//! weighted activity remain distinct. Object context never multiplies values.

#![forbid(unsafe_code)]

mod capacity;
mod json;
mod numeric;
mod types;
mod validation;

use std::collections::BTreeMap;
use std::fmt;

use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{ToPrimitive, Zero};
use serde::{Deserialize, Serialize};

pub use types::*;

pub const SCHEMA_VERSION: &str = "0.1";
pub const METHOD_VERSION: &str = "dapane-exact-v0.1.0";
pub const CAPACITY_SCHEMA_VERSION: &str = "0.2";
pub const CAPACITY_METHOD_VERSION: &str = "dapane-exact-v0.2.0";
pub const ENGINE_VERSION: &str = env!("CARGO_PKG_VERSION");
pub const MAX_JSON_BYTES: usize = 4 * 1024 * 1024;

/// A machine-readable error shared by native, command-line and binding callers.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct DapaneError {
    pub code: String,
    pub message: String,
    pub path: String,
}

impl DapaneError {
    pub fn new(code: &str, message: &str, path: &str) -> Self {
        Self {
            code: code.to_owned(),
            message: message.to_owned(),
            path: path.to_owned(),
        }
    }
}

impl fmt::Display for DapaneError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        let serialized = serde_json::to_string(self).map_err(|_| fmt::Error)?;
        formatter.write_str(&serialized)
    }
}
impl std::error::Error for DapaneError {}

/// Parse a strict versioned request and return a deterministic JSON report.
pub fn evaluate_json(input: &str) -> Result<String, DapaneError> {
    let request = json::parse(input)?;
    json::canonical(&json::value(&evaluate(&request)?)?)
}

struct LineValue {
    exact: BigRational,
    minor: BigInt,
}

#[derive(Default)]
struct ObjectValue {
    direct: BigInt,
    allocated: BigInt,
}

fn invariant(message: &str) -> DapaneError {
    DapaneError::new("internal_invariant", message, "/")
}

/// Validate and evaluate exact point-date quantities under one valuation policy.
///
/// The function is pure: it uses no current date, network access or random state.
/// It returns no partial financial result if validation or precision bounds fail.
pub fn evaluate(request: &Request) -> Result<Report, DapaneError> {
    json::check_typed_size(request)?;
    validation::validate(request)?;
    let request = validation::normalize(request);
    let input_digest = json::digest(
        &format!("dapane:input:{}\n", request.schema_version),
        &json::value(&request)?,
    )?;
    let scale = request.policy.rounding.scale;
    let quote_map: BTreeMap<_, _> = request
        .quotes
        .iter()
        .map(|quote| (quote.id.as_str(), quote))
        .collect();
    let event_map: BTreeMap<_, _> = request
        .events
        .iter()
        .map(|event| (event.id.as_str(), event))
        .collect();
    let mut line_values = BTreeMap::new();
    let mut lines = Vec::with_capacity(request.usage.len());
    let mut objects: BTreeMap<_, _> = request
        .objects
        .iter()
        .map(|object| (object.id.as_str(), ObjectValue::default()))
        .collect();
    let mut total_exact = BigRational::zero();
    let mut total_minor = BigInt::zero();
    let mut directly_attributed = BigInt::zero();

    for usage in &request.usage {
        let quote = quote_map
            .get(usage.quote_id.as_str())
            .ok_or_else(|| invariant("Validated quote disappeared"))?;
        let quantity = numeric::parse(&usage.quantity, "/usage")?;
        let amount = numeric::parse(&quote.amount, "/quotes")?;
        let per_quantity = numeric::parse(&quote.per_quantity, "/quotes")?;
        let exact = numeric::bounded(&quantity * amount / per_quantity, "/usage")?;
        let minor = numeric::rounded_minor(&exact, scale);
        let adjustment = numeric::bounded(numeric::from_minor(&minor, scale) - &exact, "/usage")?;
        total_exact = numeric::bounded(total_exact + &exact, "/usage")?;
        total_minor += &minor;
        if let Some(object_id) = &usage.attribution_object_id {
            objects
                .get_mut(object_id.as_str())
                .ok_or_else(|| invariant("Validated attribution object disappeared"))?
                .direct += &minor;
            directly_attributed += &minor;
        }
        let event = usage.event_id.as_deref().and_then(|id| event_map.get(id));
        let process_id = usage
            .process_id
            .clone()
            .or_else(|| event.and_then(|event| event.process_id.clone()));
        let activity_id = usage
            .activity_id
            .clone()
            .or_else(|| event.and_then(|event| event.activity_id.clone()));
        lines.push(ValuationLine {
            id: usage.id.clone(),
            use_id: usage.use_id.clone(),
            kind: usage.kind,
            target: usage.target.clone(),
            unit: usage.unit.clone(),
            quote_id: usage.quote_id.clone(),
            quantity: numeric::wire(&quantity),
            components: quote.components.clone(),
            service_date: usage.service_date.clone(),
            exact: numeric::wire(&exact),
            rounded: numeric::format_minor(&minor, scale),
            rounding_adjustment: numeric::wire(&adjustment),
            source: usage.source.clone(),
            event_id: usage.event_id.clone(),
            process_id,
            activity_id,
            object_ids: usage.object_ids.clone(),
            attribution_object_id: usage.attribution_object_id.clone(),
        });
        line_values.insert(usage.id.as_str(), LineValue { exact, minor });
    }

    let mut allocations = Vec::with_capacity(request.allocations.len());
    let mut allocated_minor = BigInt::zero();
    for allocation in &request.allocations {
        let mut pool_exact = BigRational::zero();
        let mut pool_minor = BigInt::zero();
        for line_id in &allocation.source_line_ids {
            let line = line_values
                .get(line_id.as_str())
                .ok_or_else(|| invariant("Validated pool source disappeared"))?;
            pool_exact = numeric::bounded(pool_exact + &line.exact, "/allocations")?;
            pool_minor += &line.minor;
        }
        let weights = allocation
            .weights
            .iter()
            .map(|weight| numeric::parse(&weight.weight, "/allocations"))
            .collect::<Result<Vec<_>, _>>()?;
        let total_weight = weights
            .iter()
            .try_fold(BigRational::zero(), |sum, weight| {
                numeric::bounded(sum + weight, "/allocations")
            })?;
        let mut raw_shares = Vec::with_capacity(weights.len());
        let mut rounded_shares = Vec::with_capacity(weights.len());
        let mut remainders = Vec::with_capacity(weights.len());
        let mut floor_sum = BigInt::zero();
        for (index, weight) in weights.iter().enumerate() {
            let raw_minor = numeric::bounded(
                BigRational::from_integer(pool_minor.clone()) * weight / &total_weight,
                "/allocations",
            )?;
            let floor = raw_minor.to_integer();
            let remainder = numeric::bounded(
                &raw_minor - BigRational::from_integer(floor.clone()),
                "/allocations",
            )?;
            floor_sum += &floor;
            rounded_shares.push(floor);
            raw_shares.push(numeric::bounded(
                raw_minor / BigRational::from_integer(numeric::ten_pow(scale)),
                "/allocations",
            )?);
            remainders.push((index, remainder));
        }
        let remaining = (&pool_minor - floor_sum)
            .to_usize()
            .ok_or_else(|| invariant("Allocation remainder is out of range"))?;
        if remaining > rounded_shares.len() {
            return Err(invariant("Allocation remainder exceeds recipient count"));
        }
        remainders.sort_by(|(a_index, a), (b_index, b)| {
            b.cmp(a).then_with(|| {
                allocation.weights[*a_index]
                    .object_id
                    .cmp(&allocation.weights[*b_index].object_id)
            })
        });
        for (index, _) in remainders.iter().take(remaining) {
            rounded_shares[*index] += 1;
        }
        let mut shares = Vec::with_capacity(weights.len());
        let mut allocated_pool = BigInt::zero();
        for (index, recipient) in allocation.weights.iter().enumerate() {
            let rounded = &rounded_shares[index];
            allocated_pool += rounded;
            objects
                .get_mut(recipient.object_id.as_str())
                .ok_or_else(|| invariant("Validated allocation object disappeared"))?
                .allocated += rounded;
            shares.push(AllocationShare {
                object_id: recipient.object_id.clone(),
                weight: numeric::wire(&weights[index]),
                exact_share: numeric::wire(&raw_shares[index]),
                rounded: numeric::format_minor(rounded, scale),
            });
        }
        if allocated_pool != pool_minor {
            return Err(invariant(
                "Allocation did not conserve the rounded source pool",
            ));
        }
        allocated_minor += &allocated_pool;
        allocations.push(AllocationResult {
            id: allocation.id.clone(),
            source_line_ids: allocation.source_line_ids.clone(),
            pool_exact: numeric::wire(&pool_exact),
            pool_rounded: numeric::format_minor(&pool_minor, scale),
            shares,
            residual: numeric::format_minor(&BigInt::zero(), scale),
        });
    }

    let mut capacity_allocations = Vec::with_capacity(request.capacity_allocations.len());
    for allocation in &request.capacity_allocations {
        let result = capacity::evaluate(allocation, &line_values, scale)?;
        for (object_id, minor) in &result.assigned {
            objects
                .get_mut(object_id.as_str())
                .ok_or_else(|| invariant("Validated capacity recipient disappeared"))?
                .allocated += minor;
            allocated_minor += minor;
        }
        capacity_allocations.push(result.report);
    }

    let unattributed = &total_minor - &directly_attributed - &allocated_minor;
    if unattributed < BigInt::zero() {
        return Err(invariant("Attributed views exceed the source ledger"));
    }
    let rounding_adjustment = numeric::bounded(
        numeric::from_minor(&total_minor, scale) - &total_exact,
        "/totals",
    )?;
    let object_totals = objects
        .into_iter()
        .map(|(id, object)| ObjectTotal {
            object_id: id.to_owned(),
            direct: numeric::format_minor(&object.direct, scale),
            allocated: numeric::format_minor(&object.allocated, scale),
            total: numeric::format_minor(&(object.direct + object.allocated), scale),
        })
        .collect();
    let mut report = Report {
        schema_version: request.schema_version.clone(),
        run_id: request.run_id,
        status: ReportStatus::Complete,
        engine_version: ENGINE_VERSION.to_owned(),
        method_version: if request.schema_version == CAPACITY_SCHEMA_VERSION {
            CAPACITY_METHOD_VERSION
        } else {
            METHOD_VERSION
        }
        .to_owned(),
        input_digest,
        output_digest: String::new(),
        policy: request.policy,
        lines,
        quote_snapshots: request.quotes,
        context: Context {
            objects: request.objects,
            processes: request.processes,
            events: request.events,
            object_relations: request.object_relations,
        },
        totals: Totals {
            exact: numeric::wire(&total_exact),
            rounded: numeric::format_minor(&total_minor, scale),
            rounding_adjustment: numeric::wire(&rounding_adjustment),
            directly_attributed: numeric::format_minor(&directly_attributed, scale),
            allocated: numeric::format_minor(&allocated_minor, scale),
            unattributed: numeric::format_minor(&unattributed, scale),
        },
        allocations,
        capacity_allocations,
        object_totals,
    };
    let mut output_value = json::value(&report)?;
    output_value
        .as_object_mut()
        .ok_or_else(|| invariant("Report did not serialize to an object"))?
        .remove("output_digest");
    report.output_digest = json::digest(
        &format!("dapane:output:{}\n", report.schema_version),
        &output_value,
    )?;
    Ok(report)
}
