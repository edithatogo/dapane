# Manual costing file exchange

This repository baseline prepares and checks a synthetic CareOps costing exchange. The Rust CLI values the request and the installed Python wheel replays the downloaded result. The complete example produces AUD 150.00. The SharePoint pilot is deferred.

## Run the local example

Install the wheel, schema dependencies and matching CLI from the [quickstart](../docs/quickstart.md). These commands use a fictional SharePoint address to prepare list fields. All exchange files stay local.

```sh
exchange_dir="$(mktemp -d)"
.venv/bin/python power_platform/manual_exchange.py export \
  --input power_platform/fixtures/manual-input.json --out "$exchange_dir/input.json" \
  --sharepoint-plan > "$exchange_dir/upload-plan.json"
.venv/bin/python power_platform/manual_exchange.py run \
  --input "$exchange_dir/input.json" --cli target/release/dapane \
  --archive "$exchange_dir/result"
.venv/bin/python power_platform/manual_exchange.py import \
  --input "$exchange_dir/input.json" --archive "$exchange_dir/result" \
  --sharepoint-library 'https://example.sharepoint.com/sites/synthetic-costing/Run%20Bundles' \
  --out "$exchange_dir/list-fields.json"
```

The export preserves the submitted UTF-8 bytes. The result directory contains the exact CLI stdout in `report.json`, a replayable [run bundle](../docs/run-bundle-v0.1.md) in `bundle.json`, and SHA-256 file identities in `receipt.json`. The import verifies all three downloaded files against the retained original export and replays the full bundle history with the installed wheel. For a correction, use a new `InputRevision` and supply the existing native envelopes in `history`.

The `--sharepoint-plan` and `--sharepoint-library` options produce upload paths and manual List form values. The default export digest and import JSON remain available to existing callers.

## Set up a future SharePoint pilot

1. Use a versioned document library and results list in the authorised pilot site. The [SharePoint exchange contract](sharepoint-contract.json) specifies the library layout, internal column names, field types and required settings. Use the list's built-in `Title` column and enforce uniqueness on `ExchangeKey`. Confirm the chosen operators can perform their assigned uploads, downloads and list operations under the site's access controls. [Microsoft list column guidance](https://support.microsoft.com/en-us/sharepoint/lists/data-and-lists/list-and-library-column-types-and-options)
2. Retain the original export and upload a byte-identical copy at `InputPath` from the upload plan. Download that copy to the CLI host. Run the CLI and upload all three files to the plan's `ResultFolder`. Each `ExchangeKey` identifies the exact project, scenario and input revision. On a retry, reuse matching files and list values. A conflict requires a new input revision and preservation of the earlier files and item.
3. Download the result folder and import it against the retained original input. Use the direct library root URL for `--sharepoint-library`. Copy the generated field values into the list form and confirm that the `OutputLink` opens the replayed bundle for an authorised reader. Keep `Total` as text to preserve the exact rounded amount. Leave it blank when the result is incomplete. Counts in the list identify exclusions or incomplete capacity pools, with the full details in the archive.
4. Read back the exact native paths, downloaded hashes, list fields and item version. Verify a complete case, an incomplete case and an identical retry. Use the existing job record for submitted, running, failed or cancelled jobs. The results list records successful replay with a `completed` or `incomplete` state.
5. To roll back, suspend new submissions and retain the archived files, links and list history. The original request can still run through the CLI. The manual handoff uses files and list fields without a flow, custom connector or Canvas calculation. A future app or worker would require separate entitlement and host checks. [SharePoint connector reference](https://learn.microsoft.com/en-us/connectors/sharepoint/)

CareOps identifies projects by `ProjectCode` and scenarios by `ScenarioId`. Carry the project code as `ProjectKey` and record the exact input revision as text for this exchange. CareOps' maintained document-generation outputs have their own column contract and issued history. [CareOps source mapping](https://github.com/edithatogo/careops/blob/9872cad0e7d20bfb4ea764e4748cb76843b1ba45/modules/careops-costing/contracts/sharepoint-project-scenario.mapping.json)
