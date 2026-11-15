//! D1: explicit joint parameter draws evaluated by the existing Rust core.
//!
//! These functions do not sample parameters, infer dependence, execute an outcome
//! model, pool subgroups/replications or select a decision-provider method.

use std::collections::{BTreeMap, BTreeSet};

use dapane_core::{DapaneError, Rational, RoundingPolicy, ValuationBasis};
use num_traits::Signed;
use serde::{Deserialize, Serialize};
use serde_json::Value;

use crate::common::{self, Identity, PairKey, error};

/// Adapter envelope version; the core's schemas are unchanged.
pub const SCHEMA_VERSION: &str = "dapane-paired-draws/0.1";
/// Pure preparation, native valuation and exact-key pairing method.
pub const METHOD_VERSION: &str = "dapane-paired-draws-v0.1.0";
/// Maximum Cartesian design size, including explicit draws.
pub const MAX_EVALUATIONS: usize = 256;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum DrawAxis {
    EpistemicParameters,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum ReplicationAxis {
    ConditionalReplication,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Draw {
    draw_id: String,
    values: BTreeMap<String, Rational>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct DrawSet {
    id: String,
    version: String,
    axis: DrawAxis,
    dependence_id: String,
    generator: Identity,
    seed: Option<String>,
    parameters: BTreeMap<String, String>,
    rows: Vec<Draw>,
}

impl DrawSet {
    fn validate(&mut self) -> Result<(), DapaneError> {
        common::identifier(&self.id, "/draws/id")?;
        common::identifier(&self.version, "/draws/version")?;
        common::identifier(&self.dependence_id, "/draws/dependence_id")?;
        self.generator.validate("/draws/generator")?;
        if let Some(seed) = &self.seed {
            common::identifier(seed, "/draws/seed")?;
        }
        if self.parameters.is_empty()
            || self.parameters.len() > 128
            || self.rows.is_empty()
            || self.rows.len() > MAX_EVALUATIONS
        {
            return Err(error(
                "input_limit",
                "Require 1..128 parameters and 1..256 draws",
                "/draws",
            ));
        }
        for (id, unit) in &self.parameters {
            common::identifier(id, "/draws/parameters")?;
            common::identifier(unit, "/draws/parameters")?;
        }
        let mut ids = BTreeSet::new();
        for draw in &self.rows {
            common::identifier(&draw.draw_id, "/draws/rows")?;
            if !ids.insert(&draw.draw_id) {
                return Err(error("duplicate_identity", "Repeated draw ID", "/draws/rows"));
            }
            if !draw.values.keys().eq(self.parameters.keys()) {
                return Err(error(
                    "draw_parameters",
                    "Every joint draw must supply the same declared parameters",
                    "/draws/rows",
                ));
            }
            for v in draw.values.values() {
                common::exact(v, "/draws/rows/values")?;
            }
        }
        self.rows.sort_by(|a, b| a.draw_id.cmp(&b.draw_id));
        Ok(())
    }

    fn digest(&self) -> Result<String, DapaneError> {
        common::digest("dapane:paired-draw-set:0.1\n", self)
    }
}

/// Validate and fingerprint supplied joint draws for the independent outcome model.
///
/// The fingerprint binds the complete finite support, parameter units, draw IDs,
/// dependence declaration and generator identity. It is not scientific admission.
pub fn draw_set_digest_json(input: &str) -> Result<String, DapaneError> {
    let mut draws: DrawSet = common::parse(input)?;
    draws.validate()?;
    draws.digest()
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(deny_unknown_fields)]
struct Cell {
    scenario_id: String,
    strategy_id: String,
    replication_id: String,
    perspective: String,
    subgroup_id: String,
}

impl Cell {
    fn key(&self, draw: &str) -> PairKey {
        PairKey {
            scenario_id: self.scenario_id.clone(),
            strategy_id: self.strategy_id.clone(),
            draw_id: draw.to_owned(),
            replication_id: self.replication_id.clone(),
            perspective: self.perspective.clone(),
            subgroup_id: self.subgroup_id.clone(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Design {
    scenarios: Vec<String>,
    strategies: Vec<String>,
    replications: Vec<String>,
    perspectives: Vec<String>,
    subgroups: Vec<String>,
    replication_axis: ReplicationAxis,
}

impl Design {
    fn cells(&mut self, draws: usize) -> Result<BTreeSet<Cell>, DapaneError> {
        let mut count = draws;
        for axis in [
            &mut self.scenarios,
            &mut self.strategies,
            &mut self.replications,
            &mut self.perspectives,
            &mut self.subgroups,
        ] {
            if axis.is_empty() {
                return Err(error(
                    "empty_axis",
                    "Every design axis is explicit and nonempty",
                    "/design",
                ));
            }
            count = count
                .checked_mul(axis.len())
                .ok_or_else(|| error("input_limit", "Design size overflow", "/design"))?;
            if count > MAX_EVALUATIONS {
                return Err(error("input_limit", "Design exceeds 256 evaluations", "/design"));
            }
            for id in axis.iter() {
                common::identifier(id, "/design")?;
            }
            axis.sort();
            if axis.windows(2).any(|w| w[0] == w[1]) {
                return Err(error(
                    "duplicate_identity",
                    "Repeated design axis value",
                    "/design",
                ));
            }
        }
        let mut cells = BTreeSet::new();
        for scenario in &self.scenarios {
            for strategy in &self.strategies {
                for replication in &self.replications {
                    for perspective in &self.perspectives {
                        for subgroup in &self.subgroups {
                            cells.insert(Cell {
                                scenario_id: scenario.clone(),
                                strategy_id: strategy.clone(),
                                replication_id: replication.clone(),
                                perspective: perspective.clone(),
                                subgroup_id: subgroup.clone(),
                            });
                        }
                    }
                }
            }
        }
        Ok(cells)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct MoneyContext {
    currency: String,
    price_year: u16,
    basis: ValuationBasis,
    rounding: RoundingPolicy,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum CostMethod {
    Point,
    Intervals,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(rename_all = "snake_case")]
enum BindingKind {
    QuoteAmount,
    UsageQuantity,
    IntervalQuantity,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(deny_unknown_fields)]
struct Binding {
    parameter_id: String,
    kind: BindingKind,
    target_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct CostModel {
    cell: Cell,
    model: Identity,
    method: CostMethod,
    // Retain raw core shape, including the historical 0.1 capacity-field prohibition.
    request: Value,
    bindings: Vec<Binding>,
}

impl CostModel {
    fn validate(
        &mut self,
        draws: &DrawSet,
        money: &MoneyContext,
        path: &str,
    ) -> Result<(), DapaneError> {
        self.cell.key("validation-only").validate(path)?;
        self.model.validate(path)?;
        synthetic_sources(&self.request, path)?;
        let policy = match self.method {
            CostMethod::Point => &self.request["policy"],
            CostMethod::Intervals => &self.request["request"]["policy"],
        };
        if policy["perspective"].as_str() != Some(&self.cell.perspective)
            || policy["currency"].as_str() != Some(&money.currency)
            || policy["price_year"].as_u64() != Some(u64::from(money.price_year))
            || policy["basis"] != common::value(&money.basis)?
            || policy["rounding"] != common::value(&money.rounding)?
        {
            return Err(error(
                "valuation_context_mismatch",
                "Model policy must match cell perspective and shared monetary context",
                path,
            ));
        }
        let mut targets = BTreeSet::new();
        for b in &self.bindings {
            common::identifier(&b.parameter_id, path)?;
            common::identifier(&b.target_id, path)?;
            if !targets.insert((b.kind, &b.target_id)) {
                return Err(error("duplicate_binding", "A model field has more than one binding", path));
            }
            let parameter_unit = draws.parameters.get(&b.parameter_id)
                .ok_or_else(|| error("unknown_parameter", "Binding parameter is undeclared", path))?;
            let (array_path, field, unit_field) = self.binding_location(b.kind, path)?;
            let rows = self.request.pointer(&array_path).and_then(Value::as_array)
                .ok_or_else(|| error("binding_target", "Target collection is missing", path))?;
            let found: Vec<_> = rows.iter()
                .filter(|v| v["id"].as_str() == Some(&b.target_id))
                .collect();
            if found.len() != 1 || found[0].get(field).is_none() {
                return Err(error(
                    "binding_target",
                    "Binding must replace exactly one existing field by stable ID",
                    path,
                ));
            }
            if found[0][unit_field].as_str() != Some(parameter_unit) {
                return Err(error(
                    "binding_unit",
                    "Parameter unit must equal the target quantity unit or quotation currency",
                    path,
                ));
            }
        }
        self.bindings.sort();
        // A binding cannot rescue an invalid template or conceal a bad default.
        self.evaluate(&self.request).map_err(|mut e| {
            e.path = format!("{path}/template{}", e.path);
            e
        })?;
        Ok(())
    }

    fn binding_location(
        &self,
        kind: BindingKind,
        path: &str,
    ) -> Result<(String, &'static str, &'static str), DapaneError> {
        let prefix = if self.method == CostMethod::Intervals { "/request" } else { "" };
        match kind {
            BindingKind::QuoteAmount => Ok((format!("{prefix}/quotes"), "amount", "currency")),
            BindingKind::UsageQuantity => Ok((format!("{prefix}/usage"), "quantity", "unit")),
            BindingKind::IntervalQuantity if self.method == CostMethod::Intervals => {
                Ok(("/intervals".to_owned(), "quantity", "unit"))
            }
            _ => Err(error("binding_target", "Interval binding requires interval method", path)),
        }
    }

    fn prepare(&self, draw: &Draw, path: &str) -> Result<Value, DapaneError> {
        let mut request = self.request.clone();
        for b in &self.bindings {
            let number = common::exact(&draw.values[&b.parameter_id], path)?;
            if number.is_negative() {
                return Err(error(
                    "negative_cost_parameter",
                    "Core quantities and quotation amounts must be nonnegative",
                    path,
                ));
            }
            let (array_path, field, _) = self.binding_location(b.kind, path)?;
            let rows = request.pointer_mut(&array_path).and_then(Value::as_array_mut)
                .ok_or_else(|| error("binding_target", "Missing validated target collection", path))?;
            let row = rows.iter_mut()
                .find(|v| v["id"].as_str() == Some(&b.target_id))
                .ok_or_else(|| error("binding_target", "Missing validated target", path))?;
            row[field] = common::value(&common::wire(&number))?;
        }
        Ok(request)
    }

    fn evaluate(&self, request: &Value) -> Result<Value, DapaneError> {
        let input = common::canonical(request)?;
        let report = match self.method {
            CostMethod::Point => dapane_core::evaluate_json(&input)?,
            CostMethod::Intervals => dapane_core::evaluate_intervals_json(&input)?,
        };
        serde_json::from_str(&report).map_err(|e| error("core_report", &e.to_string(), "/"))
    }
}

fn synthetic_sources(v: &Value, path: &str) -> Result<(), DapaneError> {
    match v {
        Value::Object(map) => {
            if let Some(source) = map.get("source")
                && (source["evidence"] != "synthetic"
                    || source["access"] != "public"
                    || source["validation"] != "unvalidated")
            {
                return Err(error(
                    "synthetic_only",
                    "This lane accepts only public, unvalidated synthetic source declarations",
                    path,
                ));
            }
            for v in map.values() {
                synthetic_sources(v, path)?;
            }
        }
        Value::Array(rows) => {
            for v in rows {
                synthetic_sources(v, path)?;
            }
        }
        _ => {}
    }
    Ok(())
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct OutcomeRow {
    key: PairKey,
    value: Rational,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Outcomes {
    model: Identity,
    measure_id: String,
    unit: String,
    draw_set_digest: String,
    rows: Vec<OutcomeRow>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    schema_version: String,
    run_id: String,
    draws: DrawSet,
    design: Design,
    money: MoneyContext,
    models: Vec<CostModel>,
    outcomes: Outcomes,
}

/// Evaluate every explicit draw/cell and join outcomes using all six identity axes.
///
/// The complete Cartesian panel is mandatory. Missing, surplus or duplicate rows
/// fail before a result is returned. Native reports retain their own rounding,
/// source snapshots and method identities without numerical transformation.
pub fn evaluate_paired_json(input: &str) -> Result<String, DapaneError> {
    let mut input: Input = common::parse(input)?;
    if input.schema_version != SCHEMA_VERSION {
        return Err(error("unsupported_schema", "Unsupported paired-draw schema", "/schema_version"));
    }
    common::identifier(&input.run_id, "/run_id")?;
    if !matches!(input.money.basis, ValuationBasis::EconomicCost | ValuationBasis::FinancialCost) {
        return Err(error(
            "unsupported_basis",
            "Cost pairing does not admit funding or charge as resource costs",
            "/money/basis",
        ));
    }
    input.draws.validate()?;
    let draw_digest = input.draws.digest()?;
    if input.outcomes.draw_set_digest != draw_digest {
        return Err(error(
            "draw_digest_mismatch",
            "Outcomes must identify the complete supplied joint draw set",
            "/outcomes/draw_set_digest",
        ));
    }
    let cells = input.design.cells(input.draws.rows.len())?;
    if input.models.len() != cells.len()
        || input.models.iter().map(|m| m.cell.clone()).collect::<BTreeSet<_>>() != cells
    {
        return Err(error(
            "model_panel_mismatch",
            "Exactly one cost model is required per design cell",
            "/models",
        ));
    }
    input.outcomes.model.validate("/outcomes/model")?;
    common::identifier(&input.outcomes.measure_id, "/outcomes/measure_id")?;
    common::identifier(&input.outcomes.unit, "/outcomes/unit")?;
    let keys: BTreeSet<_> = cells.iter()
        .flat_map(|cell| input.draws.rows.iter().map(move |d| cell.key(&d.draw_id)))
        .collect();
    if input.outcomes.rows.len() != keys.len()
        || input.outcomes.rows.iter().map(|o| o.key.clone()).collect::<BTreeSet<_>>() != keys
    {
        return Err(error(
            "pairing_mismatch",
            "Outcome keys must match every model/draw cell exactly once",
            "/outcomes/rows",
        ));
    }
    for row in &input.outcomes.rows {
        row.key.validate("/outcomes/rows/key")?;
        common::exact(&row.value, "/outcomes/rows/value")?;
    }
    input.models.sort_by(|a, b| a.cell.cmp(&b.cell));
    input.outcomes.rows.sort_by(|a, b| a.key.cmp(&b.key));
    for (i, model) in input.models.iter_mut().enumerate() {
        model.validate(&input.draws, &input.money, &format!("/models/{i}"))?;
    }
    let input_digest = common::digest("dapane:paired-input:0.1\n", &input)?;
    let outcomes: BTreeMap<_, _> = input.outcomes.rows.iter().map(|r| (&r.key, r)).collect();
    let mut results = BTreeMap::new();
    let mut output_bytes = common::encoded_size(&input, common::OUTPUT_BYTES)?;
    for (i, model) in input.models.iter().enumerate() {
        for draw in &input.draws.rows {
            let path = format!("/models/{i}/draws/{}", draw.draw_id);
            let prepared = model.prepare(draw, &path)?;
            let report = model.evaluate(&prepared).map_err(|mut e| {
                e.path = format!("{path}{}", e.path);
                e
            })?;
            let key = model.cell.key(&draw.draw_id);
            let row = serde_json::json!({
                "key": key,
                "cost_model": model.model,
                "cost_method": model.method,
                "parameter_draw_digest": common::digest("dapane:paired-parameter-draw:0.1\n", draw)?,
                "prepared_request": prepared,
                "cost_report": report,
                "outcome": outcomes[&key],
            });
            output_bytes = output_bytes
                .saturating_add(common::encoded_size(&row, common::OUTPUT_BYTES)?);
            if output_bytes > common::OUTPUT_BYTES {
                return Err(error("output_limit", "Batch report exceeds 16 MiB", "/"));
            }
            results.insert(key, row);
        }
    }
    let mut report = serde_json::json!({
        "schema_version": SCHEMA_VERSION,
        "method_version": METHOD_VERSION,
        "run_id": input.run_id,
        "status": "complete",
        "input_digest": input_digest,
        "draw_set_digest": draw_digest,
        "draws": input.draws,
        "design": input.design,
        "money": input.money,
        "models": input.models,
        "outcome_contract": {
            "model": input.outcomes.model,
            "measure_id": input.outcomes.measure_id,
            "unit": input.outcomes.unit,
        },
        "rows": results.into_values().collect::<Vec<_>>(),
    });
    report["output_digest"] =
        Value::String(common::digest("dapane:paired-output:0.1\n", &report)?);
    common::encoded_size(&report, common::OUTPUT_BYTES)?;
    common::canonical(&report)
}
