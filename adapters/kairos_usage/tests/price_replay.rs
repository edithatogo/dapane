//! Installed-provider trajectory and price-only revaluation oracles.

use dapane_core::{SourceAccess, evaluate_json};
use dapane_kairos_usage::{OccupancyRecipe, ProjectionError, prepare_usage};
use kairo_ecs_des::{StagedResourceRuntime, StagedUsageSource};
use kairo_ecs_types::SimTime;
use serde_json::{Value, json};
use std::num::NonZeroU128;

const REVISION: &str = "cdda89112575a42aa8c8e67868f61379ea35d05d";
fn recipe() -> OccupancyRecipe<'static> {
    OccupancyRecipe {
        quantity_unit: "instrument",
        time_unit: "hour",
        target: "assay-instrument",
        valuation_unit: "instrument-hour",
        quote_id: "rate",
        service_date: "2026-06-15",
        access: SourceAccess::Public,
    }
}

fn tick(steps: u128) -> SimTime {
    SimTime::from_ticks(steps)
}

fn runtime() -> StagedResourceRuntime {
    StagedResourceRuntime::new_with_usage(StagedUsageSource {
        run: "synthetic-kairos-occupancy".into(),
        scenario: "single-resource".into(),
        branch: "base".into(),
        engine_revision: REVISION.into(),
        model_revision: "staged-instrument-v1".into(),
        rng_revision: "deterministic".into(),
        time_unit: "hour".into(),
        ticks_per_time_unit: NonZeroU128::new(2).unwrap(),
    })
    .unwrap()
}

#[test]
fn two_quote_releases_revalue_the_same_executed_usage() {
    let mut sim = runtime();
    let actor = sim.spawn_actor().unwrap();
    let resource = sim.create_resource_with_unit(1, "instrument").unwrap();
    let request = sim.submit(resource, actor, tick(1)).unwrap();
    assert_eq!(sim.run_for(1).unwrap(), 1);
    let lease = sim.request(request).unwrap().lease.unwrap();
    sim.release(lease, tick(4)).unwrap();
    assert_eq!(sim.run_for(1).unwrap(), 1);
    let execution = sim.committed_usage(resource, tick(0), tick(4)).unwrap();
    let usage = prepare_usage(&execution, &recipe()).unwrap();
    assert_eq!(execution.occupied_unit_ticks, 3);
    assert_eq!(usage.len(), 1);
    let mut payload = json!({
        "schema_version": "0.1", "run_id": "kairos-price-only",
        "knowledge_cutoff": "2026-06-15",
        "policy": {
            "id":"explicit-nz-provider","version":"1","currency":"NZD",
            "price_year":2026,"perspective":"provider","basis":"financial_cost",
            "rounding":{"scale":2,"mode":"half_even"}
        },
        "quotes": [{
            "id":"rate","kind":"resource_use","target":"assay-instrument",
            "unit":"instrument-hour","amount":"12","per_quantity":"1",
            "currency":"NZD","price_year":2026,"basis":"financial_cost","components":["equipment"],
            "valid_from":"2026-01-01","valid_to":"2027-01-01","known_from":"2026-01-01",
            "source":{"id":"synthetic-rate","version":"1","evidence":"synthetic","access":"public","validation":"unvalidated"}
        }],
        "usage": usage
    });
    let baseline: Value =
        serde_json::from_str(&evaluate_json(&payload.to_string()).unwrap()).unwrap();
    payload["quotes"][0]["amount"] = json!("20");
    payload["quotes"][0]["source"]["version"] = json!("2");
    let revised: Value =
        serde_json::from_str(&evaluate_json(&payload.to_string()).unwrap()).unwrap();
    assert_eq!(baseline["totals"]["rounded"], "18.00");
    assert_eq!(revised["totals"]["rounded"], "30.00");
    assert_eq!(
        baseline["lines"][0]["use_id"],
        payload["usage"][0]["use_id"]
    );
    assert_eq!(
        baseline["lines"][0]["use_id"],
        revised["lines"][0]["use_id"]
    );
    assert_ne!(baseline["output_digest"], revised["output_digest"]);
    assert_eq!(
        sim.committed_usage(resource, tick(0), tick(4)).unwrap(),
        execution
    );
}

#[test]
fn unresolved_release_and_wrong_units_are_visible() {
    let mut sim = runtime();
    let actor = sim.spawn_actor().unwrap();
    let resource = sim.create_resource_with_unit(1, "instrument").unwrap();
    let marker = sim.create_resource(1).unwrap();
    sim.submit(resource, actor, tick(1)).unwrap();
    sim.submit(marker, actor, tick(4)).unwrap();
    sim.run_for(2).unwrap();
    let execution = sim.committed_usage(resource, tick(0), tick(4)).unwrap();
    assert_eq!(
        prepare_usage(&execution, &recipe()),
        Err(ProjectionError::Censored)
    );
    let mut wrong = recipe();
    wrong.time_unit = "minute";
    assert_eq!(
        prepare_usage(&execution, &wrong),
        Err(ProjectionError::UnsupportedContract)
    );
}
