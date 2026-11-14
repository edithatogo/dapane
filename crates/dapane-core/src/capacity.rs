//! Explicit capacity allocation for 0.2. No utilisation or economic proration is inferred.

use std::collections::BTreeMap;

use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{ToPrimitive, Zero};

use crate::{
    CapacityAllocation, CapacityAllocationResult, CapacityQuantity, CapacityShare, DapaneError,
    LineValue, invariant, numeric, validation,
};

pub(crate) fn quantity(
    value: &CapacityQuantity,
    path: &str,
) -> Result<Option<BigRational>, DapaneError> {
    match value {
        CapacityQuantity::Known { quantity } => {
            numeric::parse(quantity, &format!("{path}/quantity")).map(Some)
        }
        CapacityQuantity::Unknown { reason } => {
            validation::text(reason, &format!("{path}/reason"))?;
            Ok(None)
        }
    }
}

pub(crate) struct Evaluation {
    pub report: CapacityAllocationResult,
    pub assigned: Vec<(String, BigInt)>,
}

pub(crate) fn evaluate(
    allocation: &CapacityAllocation,
    lines: &BTreeMap<&str, LineValue>,
    scale: u8,
) -> Result<Evaluation, DapaneError> {
    let path = "/capacity_allocations";
    let mut pool_exact = BigRational::zero();
    let mut pool_minor = BigInt::zero();
    for id in &allocation.source_line_ids {
        let line = lines
            .get(id.as_str())
            .ok_or_else(|| invariant("Validated capacity source disappeared"))?;
        pool_exact = numeric::bounded(pool_exact + &line.exact, path)?;
        pool_minor += &line.minor;
    }
    let available = quantity(&allocation.available_capacity, path)?;
    let observations = allocation
        .use_records
        .iter()
        .map(|r| quantity(&r.quantity, path))
        .collect::<Result<Vec<_>, _>>()?;
    let accounted = observations
        .iter()
        .flatten()
        .try_fold(BigRational::zero(), |sum, value| {
            numeric::bounded(sum + value, path)
        })?;
    let unaccounted = available
        .as_ref()
        .map(|value| numeric::bounded(value - &accounted, path))
        .transpose()?;
    let pool_money = numeric::from_minor(&pool_minor, scale);
    let mut shares = Vec::with_capacity(observations.len());
    let mut assigned = Vec::with_capacity(observations.len());

    // Bucket 0 is unallocated value, followed by recipients in canonical ID order.
    // Unknown observations never acquire a rounding cent. Missing capacity leaves
    // the whole rounded pool unallocated, even when some use quantities are known.
    let mut raw_minor = vec![BigRational::zero(); observations.len() + 1];
    if let Some(denominator) = &available {
        let mut assigned_raw = BigRational::zero();
        for (index, observation) in observations.iter().enumerate() {
            if let Some(value) = observation {
                raw_minor[index + 1] = numeric::bounded(
                    BigRational::from_integer(pool_minor.clone()) * value / denominator,
                    path,
                )?;
                assigned_raw = numeric::bounded(assigned_raw + &raw_minor[index + 1], path)?;
            }
        }
        raw_minor[0] = numeric::bounded(
            BigRational::from_integer(pool_minor.clone()) - assigned_raw,
            path,
        )?;
    } else {
        raw_minor[0] = BigRational::from_integer(pool_minor.clone());
    }
    let mut rounded: Vec<_> = raw_minor.iter().map(BigRational::to_integer).collect();
    let floor_sum: BigInt = rounded.iter().sum();
    let remaining = (&pool_minor - floor_sum)
        .to_usize()
        .ok_or_else(|| invariant("Capacity rounding remainder is out of range"))?;
    let mut remainders: Vec<_> = raw_minor
        .iter()
        .zip(&rounded)
        .enumerate()
        .map(|(i, (raw, floor))| (i, raw - BigRational::from_integer(floor.clone())))
        .collect();
    remainders.sort_by(|(ai, a), (bi, b)| b.cmp(a).then_with(|| ai.cmp(bi)));
    if remaining > remainders.len() {
        return Err(invariant(
            "Capacity rounding remainder exceeds bucket count",
        ));
    }
    for (index, _) in remainders.iter().take(remaining) {
        rounded[*index] += 1;
    }
    if rounded.iter().sum::<BigInt>() != pool_minor {
        return Err(invariant(
            "Capacity allocation did not conserve the rounded pool",
        ));
    }
    let divisor = BigRational::from_integer(numeric::ten_pow(scale));
    for (index, record) in allocation.use_records.iter().enumerate() {
        let known = available.is_some() && observations[index].is_some();
        shares.push(CapacityShare {
            object_id: record.object_id.clone(),
            quantity: record.quantity.clone(),
            exact_share: if known {
                Some(numeric::wire(&numeric::bounded(
                    &raw_minor[index + 1] / &divisor,
                    path,
                )?))
            } else {
                None
            },
            rounded: known.then(|| numeric::format_minor(&rounded[index + 1], scale)),
        });
        if known {
            assigned.push((record.object_id.clone(), rounded[index + 1].clone()));
        }
    }
    let unallocated_exact = numeric::bounded(&raw_minor[0] / &divisor, path)?;
    if unallocated_exact > pool_money {
        return Err(invariant("Unallocated value exceeds capacity pool"));
    }
    Ok(Evaluation {
        report: CapacityAllocationResult {
            id: allocation.id.clone(),
            source_line_ids: allocation.source_line_ids.clone(),
            unit: allocation.unit,
            observation_coverage: allocation.observation_coverage,
            available_capacity: allocation.available_capacity.clone(),
            source: allocation.source.clone(),
            pool_exact: numeric::wire(&pool_exact),
            pool_rounded: numeric::format_minor(&pool_minor, scale),
            accounted_quantity: numeric::wire(&accounted),
            unaccounted_quantity: unaccounted.as_ref().map(numeric::wire),
            shares,
            unallocated_exact: numeric::wire(&unallocated_exact),
            unallocated: numeric::format_minor(&rounded[0], scale),
        },
        assigned,
    })
}
