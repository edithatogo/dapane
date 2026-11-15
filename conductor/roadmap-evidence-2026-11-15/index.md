# Roadmap execution evidence — 15 November 2026

These are immutable copies of actual hosted qualification receipts and selected
command logs. Both source histories remain visible. The first attempt's failed
aggregates remain failed after the shared layout correction. Downloaded archives,
tracked source inventories and all retained members were independently verified.

Text receipts do not publish packages. Native binaries remain in the identified
GitHub Actions artifacts, with the recorded 30-day retention. Future qualification
or Julia distribution must retain and identify its accepted artifact bytes.

| Attempt | PR | Exact executed source | Lane commands | Aggregate | Raw receipt | Selected logs |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | #21 | `90b96b12382baf6fbc7615567c4680e7ce43fe5e` | failed | failure | [receipt](attempt-1/pr21/qualification.json) | [execution](attempt-1/pr21/execution.json) |
| 2 | #21 | `63e3f8368510641513b5fd84ae3074bb80e79c6f` | failed | failure | [receipt](attempt-2/pr21/qualification.json) | [execution](attempt-2/pr21/execution.json) |
| 1 | #22 | `2e7f6b33c04ad49fcf3e073fa88aa38146de3cf3` | passed | failure | [receipt](attempt-1/pr22/qualification.json) | [execution](attempt-1/pr22/execution.json) |
| 2 | #22 | `720807a66b206ba16cc863480807986e22f125f3` | passed | success | [receipt](attempt-2/pr22/qualification.json) | [execution](attempt-2/pr22/execution.json) |
| 1 | #23 | `d7ca218869ac5374f74a96bf1885fde43e927d27` | failed | failure | [receipt](attempt-1/pr23/qualification.json) | [execution](attempt-1/pr23/execution.json) |
| 2 | #23 | `f9f85e5f54a38447eab91ae459aad2f372bcbb7e` | failed | failure | [receipt](attempt-2/pr23/qualification.json) | [execution](attempt-2/pr23/execution.json) |
| 1 | #24 | `03378bff41b812d016fb0ac93bb8bb4ed07591f6` | failed | failure | [receipt](attempt-1/pr24/qualification.json) | [execution](attempt-1/pr24/execution.json) |
| 2 | #24 | `237ddb238997b0babe12266cb7775207c597dfd4` | failed | failure | [receipt](attempt-2/pr24/qualification.json) | [execution](attempt-2/pr24/execution.json) |
| 1 | #25 | `a76e9a1e96b3ef997b41c9ebd33344f317351d6e` | failed | failure | [receipt](attempt-1/pr25/qualification.json) | [execution](attempt-1/pr25/execution.json) |
| 2 | #25 | `8281042676c1d9cafab69e9c57cdfd064a9a5adf` | failed | failure | [receipt](attempt-2/pr25/qualification.json) | [execution](attempt-2/pr25/execution.json) |
| 1 | #26 | `8e1687960efca8e7b6cced13b2a0e875c23ea40a` | failed | failure | [receipt](attempt-1/pr26/qualification.json) | [execution](attempt-1/pr26/execution.json) |
| 2 | #26 | `8716c423f15c6449940df902fbabfab870d38f4d` | failed | failure | [receipt](attempt-2/pr26/qualification.json) | [execution](attempt-2/pr26/execution.json) |
| 1 | #27 | `71ecabf21402f9f8cff62071a2ba6b8a04ba19c8` | passed | failure | [receipt](attempt-1/pr27/qualification.json) | [execution](attempt-1/pr27/execution.json) |
| 2 | #27 | `0fbed5e8b8d6d0ae24cf2fbf6720c003226f9b10` | passed | success | [receipt](attempt-2/pr27/qualification.json) | [execution](attempt-2/pr27/execution.json) |

## Complete static result records

The static result payloads are stored with lossless gzip compression. The
compression records preserve original byte counts and SHA-256 values; the
JSON content has not been edited. Failed, null, slower and unmeasured outcomes
remain in those records.

- First attempt: [results](attempt-1/pr24/static-results.json.gz), [compression identity](attempt-1/pr24/static-results-compression.json), [build receipt](attempt-1/pr24/static-build.json).
- Corrected head: [results](attempt-2/pr24/static-results.json.gz), [compression identity](attempt-2/pr24/static-results-compression.json), [build receipt](attempt-2/pr24/static-build.json).
