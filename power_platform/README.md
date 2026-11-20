# Manual costing file exchange

An operator can transfer a synthetic CareOps costing request and its result using files. Dapane's CLI performs the valuation. The installed Python wheel replays it when the result is imported. The local example produces AUD 150.00. Hosted tenant acceptance is open.

## Run the example

Use the installed wheel, schema dependencies and matching CLI from the [quickstart](../docs/quickstart.md). Pick an empty exchange directory for the example.

```sh
python power_platform/manual_exchange.py export --input power_platform/fixtures/manual-input.json --out exchange/input.json
python power_platform/manual_exchange.py run --input exchange/input.json --cli target/release/dapane --archive exchange/result
python power_platform/manual_exchange.py import --input exchange/input.json --archive exchange/result --out exchange/list-row.json
```

The export preserves the submitted UTF-8 bytes. The result directory contains the exact CLI stdout in `report.json`, a replayable [run bundle](../docs/run-bundle-v0.1.md) in `bundle.json`, and SHA-256 file identities in `receipt.json`. The run and import verify the full history, source revision, rate releases and numerical result. Supply existing envelopes in `history` for a replacement. A retry accepts identical bytes. A changed revision needs a distinct destination.

## Configure the manual SharePoint surface

1. At the selected site create a versioned document library for synthetic costing exchanges. Give the submitter access to the input folder and the importing operator access to result folders. Use the site's existing access controls. Preserve earlier file versions.
2. Create a list for run summaries. Use unique single-line text `BundleDigest` for the result revision. Add single-line text columns for `ProjectKey`, `ScenarioId`, `InputRevision`, `RunId`, `SeriesId`, `BundleId`, `OutputContentHash`, `CalculationContractVersion`, `NativeStatus`, `Total` and `Currency`. Keep the rounded amount as text for exact transport. Add a `JobState` choice with submitted, running, completed, incomplete, failed and cancelled. Store `ExcludedInputs` and `IncompleteCapacityPools` in multiline text and add a hyperlink for the archived file.
3. Upload the exported input into a revision-specific folder. Download that file to the CLI host and run the example with the downloaded file. Upload the three result files together to a new result revision. Download them and import with the original input. Enter the resulting row, and resolve its `OutputFile` relative to the uploaded result directory. Use the library link in the list.
4. Use `incomplete` for excluded inputs or incomplete capacity observations. The row names the gaps and leaves the total blank. A rejected evaluation or import produces an error. Record the failure against the submitted job and retain the input for correction. An operator can cancel an unprocessed job before running it.
5. To roll back the optional surface, suspend new submissions and retain files, links and list history. The archived request still evaluates with the standalone CLI. A separately selected worker, connector or PCF control would need its own deployment and entitlement evidence.

CareOps' source mapping identifies projects by `ProjectCode` and scenarios by `ScenarioId`. Carry the project code in the output library's `ProjectKey`, along with the scenario and input revision. Its document-generation form is separate from the calculation exchange. The inspected mapping is at CareOps revision `40a34712350ff563c7aca95d77c98b5e60a72127`. [CareOps source mapping](https://github.com/edithatogo/careops/blob/40a34712350ff563c7aca95d77c98b5e60a72127/modules/careops-costing/contracts/sharepoint-project-scenario.mapping.json)

The synthetic local round trip verifies software and file identities. Site permissions, live list entry, downloaded files and operator visibility require a selected tenant, site and permitted-data scope. Publication and tenant activation have separate owners.
