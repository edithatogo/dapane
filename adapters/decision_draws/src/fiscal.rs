//! T1: exact synthetic incremental accounting with explicit transfer boundaries.
//!
//! This implements a small synthetic reference contract, not a Tobac consumer,
//! excise/GST calculator, cohort model or decision-provider method.

use std::collections::BTreeSet;

use dapane_core::{DapaneError, Rational};
use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Signed, Zero};
use serde::{Deserialize, Serialize};
use serde_json::Value;

use crate::common::{self, Identity, PairKey, error};

/// Isolated fiscal envelope; no shared core schema is extended.
pub const SCHEMA_VERSION: &str = "dapane-fiscal/0.1";
/// Exact effective-rate-per-step discounting and explicit accounting.
pub const METHOD_VERSION: &str = "dapane-fiscal-exact-steps-v0.1.0";
/// Bound on monetary lines and separately supplied health flows.
pub const MAX_FLOWS: usize = 256;
/// Maximum explicit integer discount step; precision bounds apply separately.
pub const MAX_TIME_STEP: u16 = 1200;

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum Perspective {
    HealthSystem,
    PublicFinance,
    Societal,
}

impl Perspective {
    fn as_str(self) -> &'static str {
        match self {
            Self::HealthSystem => "health_system",
            Self::PublicFinance => "public_finance",
            Self::Societal => "societal",
        }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum Rule {
    HealthSystemDirectOnly,
    PublicFinanceNetOutlay,
    SocietalNetDomesticTransfers,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "UPPERCASE")]
enum Currency {
    Aud,
    Nzd,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "UPPERCASE")]
enum Jurisdiction {
    Au,
    Nz,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum MoneyUnit {
    Currency,
    CurrencyPerQaly,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum AccountingBasis {
    EconomicCost,
    PublicExpenditure,
    FiscalTransfer,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Money {
    amount: Rational,
    currency: Currency,
    price_year: u16,
    unit: MoneyUnit,
}

impl Money {
    fn validate(
        &self,
        currency: Currency,
        year: u16,
        unit: MoneyUnit,
        path: &str,
    ) -> Result<BigRational, DapaneError> {
        if self.currency != currency || self.price_year != year || self.unit != unit {
            return Err(error(
                "monetary_context",
                "Currency, price year and monetary unit must match the declared purpose",
                path,
            ));
        }
        common::exact(&self.amount, path)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum DiscountMethod {
    EffectiveRatePerStep,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Discount {
    method: DiscountMethod,
    origin_id: String,
    step_years: Rational,
    resource_rate: Rational,
    health_rate: Rational,
    transfer_rate: Rational,
    source: Identity,
}

struct Rates {
    step_years: BigRational,
    resource: BigRational,
    health: BigRational,
    transfer: BigRational,
}

impl Discount {
    fn validate(&self) -> Result<Rates, DapaneError> {
        common::identifier(&self.origin_id, "/discount/origin_id")?;
        self.source.validate("/discount/source")?;
        let step_years = common::exact(&self.step_years, "/discount/step_years")?;
        if step_years <= BigRational::zero() || step_years > BigRational::one() {
            return Err(error(
                "discount_step",
                "Explicit annual/subannual step length must be in (0, 1] years",
                "/discount/step_years",
            ));
        }
        let rate = |v, path| -> Result<BigRational, DapaneError> {
            let r = common::exact(v, path)?;
            if r < BigRational::zero() || r > BigRational::one() {
                return Err(error(
                    "discount_rate",
                    "This bounded contract supports effective per-step rates in [0, 1]",
                    path,
                ));
            }
            Ok(r)
        };
        Ok(Rates {
            step_years,
            resource: rate(&self.resource_rate, "/discount/resource_rate")?,
            health: rate(&self.health_rate, "/discount/health_rate")?,
            transfer: rate(&self.transfer_rate, "/discount/transfer_rate")?,
        })
    }
}

fn factor(rate: &BigRational, step: u16, path: &str) -> Result<BigRational, DapaneError> {
    if step > MAX_TIME_STEP {
        return Err(error("input_limit", "Discount step exceeds 1200", path));
    }
    let mut power = step;
    let mut base = common::bounded((BigRational::one() + rate).recip(), path)?;
    let mut result = BigRational::one();
    // Bound each multiplication instead of allocating an unbounded rational power.
    while power > 0 {
        if power % 2 == 1 {
            result = common::bounded(result * &base, path)?;
        }
        power /= 2;
        if power > 0 {
            base = common::bounded(&base * &base, path)?;
        }
    }
    Ok(result)
}

fn time_years(step: u16, years: &BigRational) -> Result<Rational, DapaneError> {
    Ok(common::wire(&common::bounded(
        years * BigInt::from(step),
        "/discount/step_years",
    )?))
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum LineKind {
    HealthSystemDirectCost,
    EnforcementResourceCost,
    DiscountedTaxTransfer,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(rename_all = "snake_case")]
enum Tax {
    Excise,
    Gst,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum Boundary {
    DomesticEconomy,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum Payer {
    DomesticHouseholds,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum Recipient {
    DomesticGovernment,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Transfer {
    tax: Tax,
    boundary: Boundary,
    payer: Payer,
    recipient: Recipient,
}

/// Cohort state-occupancy entry: tracks how many individuals are in a given
/// health state at a given time step, indexed by parameter draw.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct CohortStateEntry {
    id: String,
    time_step: u16,
    from_state: String,
    to_state: String,
    population_count: Rational,
    perspective: Perspective,
    basis: AccountingBasis,
    undiscounted_amount: Money,
    source: Identity,
}

/// Cessation-resource schedule entry: resources consumed for cessation
/// intervention at a given time step, indexed by parameter draw.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct CessationResourceEntry {
    id: String,
    time_step: u16,
    resource_type: String,
    quantity: Rational,
    perspective: Perspective,
    basis: AccountingBasis,
    undiscounted_amount: Money,
    source: Identity,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Line {
    id: String,
    kind: LineKind,
    time_step: u16,
    perspective: Perspective,
    basis: AccountingBasis,
    undiscounted_amount: Money,
    source: Identity,
    transfer: Option<Transfer>,
}

impl Line {
    fn validate(
        &self,
        currency: Currency,
        year: u16,
        resource_basis: AccountingBasis,
        path: &str,
    ) -> Result<BigRational, DapaneError> {
        common::identifier(&self.id, path)?;
        self.source.validate(path)?;
        let valid = match self.kind {
            LineKind::HealthSystemDirectCost => {
                self.perspective == Perspective::HealthSystem
                    && self.transfer.is_none()
                    && self.basis == resource_basis
            }
            LineKind::EnforcementResourceCost => {
                self.perspective == Perspective::PublicFinance
                    && self.transfer.is_none()
                    && self.basis == resource_basis
            }
            LineKind::DiscountedTaxTransfer => {
                self.perspective == Perspective::PublicFinance
                    && self.transfer.is_some()
                    && self.basis == AccountingBasis::FiscalTransfer
            }
        };
        if !valid {
            return Err(error(
                "accounting_kind",
                "Line kind, source perspective and explicit transfer metadata are incompatible",
                path,
            ));
        }
        self.undiscounted_amount
            .validate(currency, year, MoneyUnit::Currency, path)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
enum HealthUnit {
    #[serde(rename = "QALY")]
    Qaly,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct HealthFlow {
    id: String,
    time_step: u16,
    value: Rational,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Health {
    model: Identity,
    unit: HealthUnit,
    flows: Vec<HealthFlow>,
    threshold: Money,
    threshold_source: Identity,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    schema_version: String,
    run_id: String,
    key: PairKey,
    comparator_strategy_id: String,
    draw_set_digest: String,
    jurisdiction: Jurisdiction,
    currency: Currency,
    price_year: u16,
    perspective: Perspective,
    aggregation_rule: Rule,
    resource_basis: AccountingBasis,
    discount: Discount,
    lines: Vec<Line>,
    health: Option<Health>,
    /// Optional occupancy schedule. Omitted input means an empty schedule.
    #[serde(default)]
    cohort_states: Vec<CohortStateEntry>,
    /// Optional cessation-resource schedule. Omitted input means an empty schedule.
    #[serde(default)]
    cessation_resources: Vec<CessationResourceEntry>,
}

impl Input {
    fn validate(&mut self) -> Result<Rates, DapaneError> {
        if self.schema_version != SCHEMA_VERSION {
            return Err(error(
                "unsupported_schema",
                "Unsupported fiscal contract",
                "/schema_version",
            ));
        }
        common::identifier(&self.run_id, "/run_id")?;
        self.key.validate("/key")?;
        common::identifier(&self.comparator_strategy_id, "/comparator_strategy_id")?;
        if self.key.strategy_id == self.comparator_strategy_id {
            return Err(error(
                "comparator",
                "Incremental flows require a distinct explicit comparator",
                "/comparator_strategy_id",
            ));
        }
        common::digest_field(&self.draw_set_digest, "/draw_set_digest")?;
        if self.key.perspective != self.perspective.as_str() {
            return Err(error(
                "perspective_key",
                "Pair key must retain the selected perspective",
                "/key/perspective",
            ));
        }
        if !matches!(
            (self.perspective, self.aggregation_rule),
            (Perspective::HealthSystem, Rule::HealthSystemDirectOnly)
                | (Perspective::PublicFinance, Rule::PublicFinanceNetOutlay)
                | (Perspective::Societal, Rule::SocietalNetDomesticTransfers)
        ) {
            return Err(error(
                "perspective_rule",
                "An explicit compatible accounting rule is required",
                "/aggregation_rule",
            ));
        }
        let basis_ok = match self.perspective {
            Perspective::HealthSystem => matches!(
                self.resource_basis,
                AccountingBasis::EconomicCost | AccountingBasis::PublicExpenditure
            ),
            Perspective::PublicFinance => self.resource_basis == AccountingBasis::PublicExpenditure,
            Perspective::Societal => self.resource_basis == AccountingBasis::EconomicCost,
        };
        if !basis_ok {
            return Err(error(
                "resource_basis",
                "Public finance requires public expenditure; societal valuation requires economic costs; transfers are never a resource basis",
                "/resource_basis",
            ));
        }
        if !(1900..=9999).contains(&self.price_year)
            || !matches!(
                (self.jurisdiction, self.currency),
                (Jurisdiction::Au, Currency::Aud) | (Jurisdiction::Nz, Currency::Nzd)
            )
        {
            return Err(error(
                "monetary_context",
                "Require explicit 1900..9999 price year and the declared AU/AUD or NZ/NZD context",
                "/currency",
            ));
        }
        if self.lines.is_empty() || self.lines.len() > MAX_FLOWS {
            return Err(error(
                "input_limit",
                "Require 1..256 explicit accounting lines, including explicit zero if applicable",
                "/lines",
            ));
        }
        let mut ids = BTreeSet::new();
        for line in &self.lines {
            if !ids.insert(&line.id) {
                return Err(error(
                    "duplicate_identity",
                    "Each underlying accounting flow must appear once",
                    "/lines",
                ));
            }
        }
        let taxes: BTreeSet<_> = self
            .lines
            .iter()
            .filter(|line| line.kind == LineKind::DiscountedTaxTransfer)
            .filter_map(|line| line.transfer.as_ref().map(|t| t.tax))
            .collect();
        if !self
            .lines
            .iter()
            .any(|line| line.kind == LineKind::HealthSystemDirectCost)
            || !self
                .lines
                .iter()
                .any(|line| line.kind == LineKind::EnforcementResourceCost)
            || taxes != BTreeSet::from([Tax::Excise, Tax::Gst])
        {
            return Err(error(
                "incomplete_ledger",
                "Require explicit medical, enforcement, excise and GST flows; use labelled zero flows for known zero, never omission",
                "/lines",
            ));
        }
        self.lines.sort_by(|a, b| a.id.cmp(&b.id));
        match (self.perspective, &mut self.health) {
            (Perspective::PublicFinance, None) => {}
            (Perspective::HealthSystem | Perspective::Societal, Some(health)) => {
                health.model.validate("/health/model")?;
                health
                    .threshold_source
                    .validate("/health/threshold_source")?;
                if health
                    .threshold
                    .validate(
                        self.currency,
                        self.price_year,
                        MoneyUnit::CurrencyPerQaly,
                        "/health/threshold",
                    )?
                    .is_negative()
                {
                    return Err(error(
                        "negative_threshold",
                        "Willingness-to-pay threshold must be nonnegative",
                        "/health/threshold",
                    ));
                }
                if health.flows.is_empty() || health.flows.len() > MAX_FLOWS {
                    return Err(error(
                        "input_limit",
                        "Require 1..256 explicit health flows, including explicit zero if applicable",
                        "/health/flows",
                    ));
                }
                let mut ids = BTreeSet::new();
                for flow in &health.flows {
                    common::identifier(&flow.id, "/health/flows")?;
                    if !ids.insert(&flow.id) {
                        return Err(error(
                            "duplicate_identity",
                            "Repeated health flow ID",
                            "/health/flows",
                        ));
                    }
                }
                health.flows.sort_by(|a, b| a.id.cmp(&b.id));
            }
            _ => {
                return Err(error(
                    "health_contract",
                    "Health/societal views require a health contract; the pure fiscal view requires health to be null",
                    "/health",
                ));
            }
        }
        if self.cohort_states.len() > MAX_FLOWS {
            return Err(error(
                "input_limit",
                "Cohort occupancy schedule exceeds 256 entries",
                "/cohort_states",
            ));
        }
        let mut cohort_ids = BTreeSet::new();
        for state in &self.cohort_states {
            let path = format!("/cohort_states/{}", state.id);
            common::identifier(&state.id, "/cohort_states/id")?;
            common::identifier(&state.from_state, "/cohort_states/from_state")?;
            common::identifier(&state.to_state, "/cohort_states/to_state")?;
            if !cohort_ids.insert(&state.id) {
                return Err(error(
                    "duplicate_identity",
                    "Each cohort state entry must appear once",
                    "/cohort_states",
                ));
            }
            nonnegative(&state.population_count, &format!("{path}/population_count"))?;
            state.source.validate(&format!("{path}/source"))?;
            state.undiscounted_amount.validate(
                self.currency,
                self.price_year,
                MoneyUnit::Currency,
                &format!("{path}/undiscounted_amount"),
            )?;
        }
        self.cohort_states.sort_by(|a, b| a.id.cmp(&b.id));
        if self.cessation_resources.len() > MAX_FLOWS {
            return Err(error(
                "input_limit",
                "Cessation-resource schedule exceeds 256 entries",
                "/cessation_resources",
            ));
        }
        let mut cessation_ids = BTreeSet::new();
        for resource in &self.cessation_resources {
            let path = format!("/cessation_resources/{}", resource.id);
            common::identifier(&resource.id, "/cessation_resources/id")?;
            common::identifier(
                &resource.resource_type,
                "/cessation_resources/resource_type",
            )?;
            if !cessation_ids.insert(&resource.id) {
                return Err(error(
                    "duplicate_identity",
                    "Each cessation-resource entry must appear once",
                    "/cessation_resources",
                ));
            }
            nonnegative(&resource.quantity, &format!("{path}/quantity"))?;
            resource.source.validate(&format!("{path}/source"))?;
            resource.undiscounted_amount.validate(
                self.currency,
                self.price_year,
                MoneyUnit::Currency,
                &format!("{path}/undiscounted_amount"),
            )?;
        }
        self.cessation_resources.sort_by(|a, b| a.id.cmp(&b.id));
        self.discount.validate()
    }
}

fn nonnegative(value: &Rational, path: &str) -> Result<BigRational, DapaneError> {
    let exact = common::exact(value, path)?;
    if exact.is_negative() {
        return Err(error(
            "invalid_quantity",
            "Occupancy and resource quantities must be nonnegative",
            path,
        ));
    }
    Ok(exact)
}

/// Evaluate one fully identified synthetic incremental fiscal packet.
///
/// Positive transfers are additional government receipts and equal negative
/// payer flows; negative amounts reverse both signs. Societal accounting nets
/// both legs within the domestic boundary. The pure fiscal view returns public
/// net outlay, never health NMB. Every value remains exact without rounding.
pub fn evaluate_fiscal_json(input: &str) -> Result<String, DapaneError> {
    let mut input: Input = common::parse(input)?;
    let rates = input.validate()?;
    let input_digest = common::digest("dapane:fiscal-input:0.1\n", &input)?;
    let mut medical = BigRational::zero();
    let mut enforcement = BigRational::zero();
    let mut receipts = BigRational::zero();
    let mut payer = BigRational::zero();
    let mut valued_lines = Vec::with_capacity(input.lines.len());
    let mut excluded = Vec::new();
    for (i, line) in input.lines.iter().enumerate() {
        let path = format!("/lines/{i}");
        let amount = line.validate(
            input.currency,
            input.price_year,
            input.resource_basis,
            &path,
        )?;
        let rate = if line.kind == LineKind::DiscountedTaxTransfer {
            &rates.transfer
        } else {
            &rates.resource
        };
        let discount_factor = factor(rate, line.time_step, &path)?;
        let discounted = common::bounded(amount * &discount_factor, &path)?;
        let (government_receipt, payer_outflow) = match line.kind {
            LineKind::HealthSystemDirectCost => {
                medical = common::bounded(medical + &discounted, &path)?;
                (None, None)
            }
            LineKind::EnforcementResourceCost => {
                enforcement = common::bounded(enforcement + &discounted, &path)?;
                if input.perspective == Perspective::HealthSystem {
                    excluded.push(line.id.clone());
                }
                (None, None)
            }
            LineKind::DiscountedTaxTransfer => {
                receipts = common::bounded(receipts + &discounted, &path)?;
                payer = common::bounded(payer - &discounted, &path)?;
                if input.perspective != Perspective::PublicFinance {
                    excluded.push(line.id.clone());
                }
                (
                    Some(common::wire(&discounted)),
                    Some(common::wire(&(-&discounted))),
                )
            }
        };
        valued_lines.push(serde_json::json!({
            "id": line.id,
            "kind": line.kind,
            "source_perspective": line.perspective,
            "basis": line.basis,
            "time_step": line.time_step,
            "valuation_time_years": time_years(line.time_step, &rates.step_years)?,
            "discount_factor": common::wire(&discount_factor),
            "discounted_amount": common::wire(&discounted),
            "government_receipt": government_receipt,
            "payer_outflow": payer_outflow,
            "transfer": line.transfer,
            "source": line.source,
        }));
    }
    let all_resources = common::bounded(&medical + &enforcement, "/resources")?;
    let net_transfer = common::bounded(&receipts + &payer, "/tax_transfers")?;
    if !net_transfer.is_zero() {
        return Err(error(
            "accounting_invariant",
            "Declared internal transfer does not balance",
            "/tax_transfers",
        ));
    }
    let selected_resource = if input.perspective == Perspective::HealthSystem {
        &medical
    } else {
        &all_resources
    };
    let mut valued_health = Vec::new();
    let mut discounted_qalys = None;
    let mut nmb = None;
    if let Some(health) = &input.health {
        let mut qaly = BigRational::zero();
        for (i, flow) in health.flows.iter().enumerate() {
            let path = format!("/health/flows/{i}");
            let discount_factor = factor(&rates.health, flow.time_step, &path)?;
            let discounted =
                common::bounded(common::exact(&flow.value, &path)? * &discount_factor, &path)?;
            qaly = common::bounded(qaly + &discounted, &path)?;
            valued_health.push(serde_json::json!({
                "id": flow.id,
                "time_step": flow.time_step,
                "valuation_time_years": time_years(flow.time_step, &rates.step_years)?,
                "discount_factor": common::wire(&discount_factor),
                "discounted_qalys": common::wire(&discounted),
            }));
        }
        let threshold = common::exact(&health.threshold.amount, "/health/threshold")?;
        let monetized_health = common::bounded(&qaly * threshold, "/net_monetary_benefit")?;
        nmb = Some(common::wire(&common::bounded(
            monetized_health - selected_resource - &net_transfer,
            "/net_monetary_benefit",
        )?));
        discounted_qalys = Some(common::wire(&qaly));
    }
    let mut valued_cohort_states = Vec::new();
    for (i, state) in input.cohort_states.iter().enumerate() {
        let path = format!("/cohort_states/{i}");
        let amount = state.undiscounted_amount.validate(
            input.currency,
            input.price_year,
            MoneyUnit::Currency,
            &path,
        )?;
        let discount_factor = factor(&rates.resource, state.time_step, &path)?;
        let discounted = common::bounded(amount * &discount_factor, &path)?;
        valued_cohort_states.push(serde_json::json!({
            "id": state.id,
            "draw_id": input.key.draw_id,
            "strategy_id": input.key.strategy_id,
            "subgroup_id": input.key.subgroup_id,
            "time_step": state.time_step,
            "from_state": state.from_state,
            "to_state": state.to_state,
            "population_count": common::wire(&nonnegative(&state.population_count, &path)?),
            "perspective": state.perspective,
            "basis": state.basis,
            "time_step_years": time_years(state.time_step, &rates.step_years)?,
            "discount_factor": common::wire(&discount_factor),
            "discounted_amount": common::wire(&discounted),
            "source": state.source,
        }));
    }
    let mut valued_cessation_resources = Vec::new();
    for (i, resource) in input.cessation_resources.iter().enumerate() {
        let path = format!("/cessation_resources/{i}");
        let amount = resource.undiscounted_amount.validate(
            input.currency,
            input.price_year,
            MoneyUnit::Currency,
            &path,
        )?;
        let discount_factor = factor(&rates.resource, resource.time_step, &path)?;
        let discounted = common::bounded(amount * &discount_factor, &path)?;
        valued_cessation_resources.push(serde_json::json!({
            "id": resource.id,
            "draw_id": input.key.draw_id,
            "strategy_id": input.key.strategy_id,
            "subgroup_id": input.key.subgroup_id,
            "time_step": resource.time_step,
            "resource_type": resource.resource_type,
            "quantity": common::wire(&nonnegative(&resource.quantity, &path)?),
            "perspective": resource.perspective,
            "basis": resource.basis,
            "time_step_years": time_years(resource.time_step, &rates.step_years)?,
            "discount_factor": common::wire(&discount_factor),
            "discounted_amount": common::wire(&discounted),
            "source": resource.source,
        }));
    }
    let net_outlay = if input.perspective == Perspective::PublicFinance {
        Some(common::wire(&common::bounded(
            &all_resources - &receipts,
            "/net_public_outlay",
        )?))
    } else {
        None
    };
    let mut report = serde_json::json!({
        "schema_version": SCHEMA_VERSION,
        "method_version": METHOD_VERSION,
        "status": "complete",
        "accounting_basis": "signed_incremental_exact_discounted",
        "run_id": input.run_id,
        "key": input.key,
        "comparator_strategy_id": input.comparator_strategy_id,
        "draw_set_digest": input.draw_set_digest,
        "jurisdiction": input.jurisdiction,
        "currency": input.currency,
        "price_year": input.price_year,
        "perspective": input.perspective,
        "aggregation_rule": input.aggregation_rule,
        "resource_basis": input.resource_basis,
        "input_digest": input_digest,
        "resources": {
            "health_system_direct_cost": common::wire(&medical),
            "enforcement_resource_cost": common::wire(&enforcement),
            "all_resources": common::wire(&all_resources),
        },
        "tax_transfers": {
            "government_receipts": common::wire(&receipts),
            "payer_outflows": common::wire(&payer),
            "net_within_boundary": common::wire(&net_transfer),
        },
        "selected_resource_cost": common::wire(selected_resource),
        "excluded_line_ids": excluded,
        "net_monetary_benefit": nmb,
        "discounted_qalys": discounted_qalys,
        "net_public_outlay": net_outlay,
        "valued_lines": valued_lines,
        "valued_health": valued_health,
        "valued_cohort_states": valued_cohort_states,
        "valued_cessation_resources": valued_cessation_resources,
        "input_snapshot": input,
    });
    report["output_digest"] = Value::String(common::digest("dapane:fiscal-output:0.1\n", &report)?);
    common::encoded_size(&report, common::OUTPUT_BYTES)?;
    common::canonical(&report)
}

/// Equity-weighted sum across subgroup packets. Schema `dapane-fiscal-equity/0.1`.
///
/// Weights are exact and strictly positive. A weight of one for every subgroup
/// makes the weighted sum equal the unweighted sum. Subgroup rows stay separate;
/// this does not replace a subgroup identity with a pooled label.
pub const EQUITY_SCHEMA_VERSION: &str = "dapane-fiscal-equity/0.1";
/// Explicit weighted-sum method. It is not a normalised mean.
pub const EQUITY_METHOD_VERSION: &str = "dapane-fiscal-equity-weighted-sum-v0.1.0";
const MAX_EQUITY_PACKETS: usize = 32;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct EquityPacket {
    weight: Rational,
    fiscal: Value,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct EquityInput {
    schema_version: String,
    packets: Vec<EquityPacket>,
}

fn read_rational(value: &Value, path: &str) -> Result<BigRational, DapaneError> {
    let wire: Rational = serde_json::from_value(value.clone())
        .map_err(|_| error("invalid_number", "Expected an exact rational object", path))?;
    common::exact(&wire, path)
}

fn optional_rational(value: &Value, path: &str) -> Result<Option<BigRational>, DapaneError> {
    if value.is_null() {
        Ok(None)
    } else {
        read_rational(value, path).map(Some)
    }
}

fn add_optional(
    seen: &mut bool,
    total: &mut Option<BigRational>,
    next: Option<BigRational>,
    path: &str,
) -> Result<(), DapaneError> {
    let next = next.map(|value| common::bounded(value, path)).transpose()?;
    if !*seen {
        *seen = true;
        *total = next;
        return Ok(());
    }
    match (&mut *total, next) {
        (None, None) => Ok(()),
        (Some(total), Some(next)) => {
            *total = common::bounded(&*total + next, path)?;
            Ok(())
        }
        _ => Err(error(
            "health_contract",
            "Every subgroup packet must use the same health contract",
            path,
        )),
    }
}

fn wire_optional(value: &Option<BigRational>) -> Result<Value, DapaneError> {
    match value {
        Some(value) => common::value(&common::wire(value)),
        None => Ok(Value::Null),
    }
}

/// Sum exact fiscal results across explicitly weighted subgroup packets.
pub fn evaluate_equity_json(input: &str) -> Result<String, DapaneError> {
    let input: EquityInput = common::parse(input)?;
    if input.schema_version != EQUITY_SCHEMA_VERSION {
        return Err(error(
            "unsupported_schema",
            "Unsupported fiscal equity contract",
            "/schema_version",
        ));
    }
    if input.packets.is_empty() || input.packets.len() > MAX_EQUITY_PACKETS {
        return Err(error(
            "input_limit",
            "Require 1..32 subgroup packets",
            "/packets",
        ));
    }
    let mut rows = Vec::with_capacity(input.packets.len());
    let mut unweighted_cost = BigRational::zero();
    let mut weighted_cost = BigRational::zero();
    let mut unweighted_qaly = None;
    let mut weighted_qaly = None;
    let mut unweighted_nmb = None;
    let mut weighted_nmb = None;
    let mut saw_qaly = false;
    let mut saw_weighted_qaly = false;
    let mut saw_nmb = false;
    let mut saw_weighted_nmb = false;
    let mut axis: Option<Value> = None;
    let mut subgroups = BTreeSet::new();
    for (i, packet) in input.packets.iter().enumerate() {
        let path = format!("/packets/{i}");
        let weight = common::exact(&packet.weight, &format!("{path}/weight"))?;
        if weight <= BigRational::zero() {
            return Err(error(
                "invalid_weight",
                "Equity weights must be strictly positive",
                &format!("{path}/weight"),
            ));
        }
        let fiscal = common::canonical(&packet.fiscal)?;
        let report: Value =
            serde_json::from_str(&evaluate_fiscal_json(&fiscal)?).map_err(|_| {
                error(
                    "serialization_error",
                    "Fiscal report could not be read back",
                    &path,
                )
            })?;
        let key = &report["key"];
        let subgroup = key["subgroup_id"].as_str().ok_or_else(|| {
            error(
                "invalid_identifier",
                "Subgroup identity missing",
                &format!("{path}/fiscal/key/subgroup_id"),
            )
        })?;
        if !subgroups.insert(subgroup.to_owned()) {
            return Err(error(
                "duplicate_identity",
                "Each subgroup is aggregated once; identities are not pooled",
                &format!("{path}/fiscal/key/subgroup_id"),
            ));
        }
        let this_axis = serde_json::json!({
            "scenario_id": key["scenario_id"],
            "strategy_id": key["strategy_id"],
            "draw_id": key["draw_id"],
            "replication_id": key["replication_id"],
            "perspective": key["perspective"],
            "currency": report["currency"],
            "price_year": report["price_year"],
            "jurisdiction": report["jurisdiction"],
            "aggregation_rule": report["aggregation_rule"],
        });
        if let Some(expected) = &axis {
            if expected != &this_axis {
                return Err(error(
                    "subgroup_axis",
                    "Equity aggregation keeps one scenario, strategy, draw, replication and perspective",
                    &format!("{path}/fiscal/key"),
                ));
            }
        } else {
            axis = Some(this_axis);
        }
        let cost = read_rational(
            &report["selected_resource_cost"],
            &format!("{path}/selected_resource_cost"),
        )?;
        let qaly = optional_rational(
            &report["discounted_qalys"],
            &format!("{path}/discounted_qalys"),
        )?;
        let nmb = optional_rational(
            &report["net_monetary_benefit"],
            &format!("{path}/net_monetary_benefit"),
        )?;
        unweighted_cost = common::bounded(&unweighted_cost + &cost, &path)?;
        weighted_cost = common::bounded(&weighted_cost + &weight * &cost, &path)?;
        let qaly_path = format!("{path}/discounted_qalys");
        let nmb_path = format!("{path}/net_monetary_benefit");
        add_optional(
            &mut saw_qaly,
            &mut unweighted_qaly,
            qaly.clone(),
            &qaly_path,
        )?;
        add_optional(
            &mut saw_weighted_qaly,
            &mut weighted_qaly,
            qaly.clone().map(|value| &weight * value),
            &qaly_path,
        )?;
        add_optional(&mut saw_nmb, &mut unweighted_nmb, nmb.clone(), &nmb_path)?;
        add_optional(
            &mut saw_weighted_nmb,
            &mut weighted_nmb,
            nmb.clone().map(|value| &weight * value),
            &nmb_path,
        )?;
        rows.push(serde_json::json!({
            "subgroup_id": subgroup,
            "draw_id": key["draw_id"],
            "strategy_id": key["strategy_id"],
            "perspective": key["perspective"],
            "weight": common::wire(&weight),
            "selected_resource_cost": common::wire(&cost),
            "discounted_qalys": wire_optional(&qaly)?,
            "net_monetary_benefit": wire_optional(&nmb)?,
        }));
    }
    let mut report = serde_json::json!({
        "schema_version": EQUITY_SCHEMA_VERSION,
        "method_version": EQUITY_METHOD_VERSION,
        "status": "complete",
        "axis": axis,
        "subgroups": rows,
        "unweighted_sum": {
            "selected_resource_cost": common::wire(&unweighted_cost),
            "discounted_qalys": wire_optional(&unweighted_qaly)?,
            "net_monetary_benefit": wire_optional(&unweighted_nmb)?,
        },
        "weighted_sum": {
            "selected_resource_cost": common::wire(&weighted_cost),
            "discounted_qalys": wire_optional(&weighted_qaly)?,
            "net_monetary_benefit": wire_optional(&weighted_nmb)?,
        },
    });
    report["output_digest"] = Value::String(common::digest(
        "dapane:fiscal-equity-output:0.1\n",
        &report,
    )?);
    common::encoded_size(&report, common::OUTPUT_BYTES)?;
    common::canonical(&report)
}
