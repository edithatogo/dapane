# Dapane consumer of Kairos committed occupancy

The optional adapter consumes the staged DES usage contract at
[Kairos cdda8919](https://github.com/edithatogo/kairos/commit/cdda89112575a42aa8c8e67868f61379ea35d05d).
The manifest and lock select the exact source and crate versions outside Dapane's
default workspace. The provider binds physical quantity units, time scale and
model/run/replay identity. The downstream recipe supplies the resource class,
valuation unit, service date and quotation ID explicitly.

Call prepare_usage with a retained committed window and the recipe. The adapter
checks units, half-open bounds, closure, duplicate leases and exact unit-tick
totals. Each usage identity derives from the execution, lease and window. Its
source locator records the admission and release events and model revision.
Keep the source window, recipe and input digest with the valuation. Evaluate
again with another quote release to change the valuation of the same usage.
Use distinct non-overlapping windows for aggregate costs.

The synthetic installed-provider test schedules an instrument from tick 1 to
tick 4 with two ticks per hour. The same one-and-a-half instrument hours return
18.00 and 30.00 NZD under separate quotations. Censored scopes require resolution
before valuation. For rollback, retain the old quote and native execution or use
an explicitly selected observed/static recipe with its own source identity.

The supported provider slice is forward-only staged occupancy. Movement,
optimistic execution and transfers have separate contracts. The adapter's
dependency policy admits only the revision-pinned Kairos repository in its
separate dependency graph.

    cargo test --manifest-path adapters/kairos_usage/Cargo.toml --locked --offline --all-targets
