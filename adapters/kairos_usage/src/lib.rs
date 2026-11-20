//! Project committed staged-DES occupancy into explicit Dapane usage inputs.

use dapane_core::{
    Evidence, ExactNumber, MeasureKind, Rational, SourceAccess, SourceRef, SourceValidation, Usage,
};
use kairo_ecs_des::{CommittedUsageWindow, STAGED_USAGE_VERSION};
use serde_json::json;
use sha2::{Digest, Sha256};
use std::{collections::BTreeSet, fmt};

/// Explicit downstream interpretation for one resource and observation window.
pub struct OccupancyRecipe<'a> {
    /// Expected physical quantity unit supplied by Kairos.
    pub quantity_unit: &'a str,
    /// Expected model time unit supplied by Kairos.
    pub time_unit: &'a str,
    /// Dapane resource classification for the resource.
    pub target: &'a str,
    /// Dapane unit for one quantity unit held for one time unit.
    pub valuation_unit: &'a str,
    /// Required quotation identity maintained by the caller.
    pub quote_id: &'a str,
    /// Service date chosen by the domain model for this window.
    pub service_date: &'a str,
    /// Access classification for the native execution evidence.
    pub access: SourceAccess,
}

/// A failed projection always leaves the valuation request unchanged.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ProjectionError {
    /// The version, expected clock or quantity unit disagrees with the export.
    UnsupportedContract,
    /// At least one occupancy has an unresolved release.
    Censored,
    /// Window extent, causal boundaries, identity or totals disagree.
    InconsistentWindow,
    /// Exact unit-tick multiplication or addition overflows.
    Overflow,
}

impl fmt::Display for ProjectionError {
    fn fmt(&self, output: &mut fmt::Formatter<'_>) -> fmt::Result {
        output.write_str(match self {
            Self::UnsupportedContract => "unsupported Kairos usage version or unit",
            Self::Censored => "a Kairos occupancy interval has an unresolved release",
            Self::InconsistentWindow => "inconsistent Kairos usage window",
            Self::Overflow => "Kairos unit-tick count exceeds the exact integer bound",
        })
    }
}
impl std::error::Error for ProjectionError {}

/// Project all closed occupancies in a single committed resource window.
///
/// The half-open intersection and tick scale determine exact quantities.
/// The caller retains the original window, resolves quotations separately,
/// and avoids summing projections from overlapping windows.
pub fn prepare_usage(
    window: &CommittedUsageWindow,
    recipe: &OccupancyRecipe<'_>,
) -> Result<Vec<Usage>, ProjectionError> {
    if window.version != STAGED_USAGE_VERSION
        || window.quantity_unit != recipe.quantity_unit
        || window.source.time_unit != recipe.time_unit
    {
        return Err(ProjectionError::UnsupportedContract);
    }
    if window.start >= window.end {
        return Err(ProjectionError::InconsistentWindow);
    }

    let mut seen = BTreeSet::new();
    let mut use_rows = Vec::with_capacity(window.occupancy.len());
    let mut total = 0_u128;
    for slice in &window.occupancy {
        let release = slice.release.ok_or(ProjectionError::Censored)?;
        let lease = (slice.request, slice.lease_revision);
        if slice.quantity == 0
            || slice.start != slice.admission.at.max(window.start)
            || slice.end != release.at.min(window.end)
            || slice.start >= slice.end
            || release.at > window.end
            || !seen.insert(lease)
        {
            return Err(ProjectionError::InconsistentWindow);
        }
        let unit_ticks = (slice.end.ticks() - slice.start.ticks())
            .checked_mul(u128::from(slice.quantity))
            .ok_or(ProjectionError::Overflow)?;
        total = total
            .checked_add(unit_ticks)
            .ok_or(ProjectionError::Overflow)?;
        let lineage = json!([
            window.version,
            window.source.run,
            window.source.scenario,
            window.source.branch,
            window.source.engine_revision,
            window.source.model_revision,
            window.source.rng_revision,
            window.resource.index,
            window.resource.generation,
            slice.request.index,
            slice.request.generation,
            slice.lease_revision,
            window.start.ticks().to_string(),
            window.end.ticks().to_string(),
        ]);
        let digest = Sha256::digest(lineage.to_string().as_bytes())
            .iter()
            .map(|byte| format!("{byte:02x}"))
            .collect::<String>();
        let id = format!("kairos-{digest}");
        use_rows.push(Usage {
            id: id.clone(),
            use_id: id.clone(),
            kind: MeasureKind::ResourceUse,
            target: recipe.target.into(),
            unit: recipe.valuation_unit.into(),
            quantity: ExactNumber::Rational(Rational {
                numerator: unit_ticks.to_string(),
                denominator: window.source.ticks_per_time_unit.to_string(),
            }),
            service_date: recipe.service_date.into(),
            quote_id: recipe.quote_id.into(),
            source: SourceRef {
                id,
                version: window.source.engine_revision.clone(),
                evidence: Evidence::Derived,
                access: recipe.access,
                validation: SourceValidation::Unvalidated,
                content_digest: None,
                locator: Some(format!(
                    "Kairos staged usage v{}; admission {}:{}; release {}:{}; model {}",
                    window.version,
                    slice.admission.event.index,
                    slice.admission.event.generation,
                    release.event.index,
                    release.event.generation,
                    window.source.model_revision,
                )),
            },
            event_id: None,
            process_id: None,
            activity_id: None,
            object_ids: Vec::new(),
            attribution_object_id: None,
        });
    }
    if total != window.occupied_unit_ticks {
        return Err(ProjectionError::InconsistentWindow);
    }
    Ok(use_rows)
}
