# Dashboard deployment templates

Build the image from the genomics adapter directory. CPython 3.15.1, the uv
build image and Python packages are pinned. The image reads authorised prepared
Parquet tables from a volume. Supply the tables separately.

~~~sh
docker build --tag genomics-dashboard .
docker run --rm --read-only --tmpfs /tmp:mode=1777 --cap-drop ALL \
  --publish 127.0.0.1:8080:8080 \
  --mount type=bind,source="$PWD/example-prepared",target=/prepared,readonly \
  genomics-dashboard
~~~

Use an existing synthetic prepared directory for a smoke test. Check
`/health` and `/api/tables` before opening the dashboard. The dashboard and its
export routes are designed for a trusted network. Restrict access at the
service boundary before making research data available. `/tmp` holds transient
worker files, metrics and logs. Export operational logs through the host if
retention is required.

The [Fargate task template](ecs-task.yml) uses an existing read-only EFS access
point, task and execution roles, and log group. Reference its task definition
from a service in private subnets, with public IP assignment disabled. Grant
the task role only the authorised EFS mount and configure access for UID 10001.
[Amazon ECS task definition reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-ecs-taskdefinition.html)

The [Azure Container Apps template](container-app.bicep) uses internal ingress
and an existing environment with a read-only Azure Files mount. The environment
must be able to pull the specified image by digest.
[Azure Container Apps resource reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.app/2025-01-01/containerapps)

Record the running image digest and prepared-data revision during deployment.
To roll back, restore the previous task or app revision, its read-only volume
and its access settings, then check readiness and the expected table list.

## Authenticated dashboard and operational API

To enable access control, mount a private JSON file and set
`GENOMICS_WEB_ACCESS_FILE` to its path. Its `users` map contains one entry
per login with `role` and `password_hash`. Generate hashes with
`werkzeug.security.generate_password_hash` on the dashboard's Python
using its default scrypt parameters. Keep the file outside the prepared
tables. Set `requests_per_minute` to the authenticated per-account limit
(default 120), and optionally set `audit_file` to a writable JSON Lines file
in private storage.

Use HTTP Basic over TLS on a trusted private network with the supplied
single-worker server. A viewer can read tables and operational reports. An
analyst or admin can also export and run diagnostics. `/health` exposes a
status for readiness checks when authentication is configured. The
authenticated monitoring endpoint exposes the component checks.

Set `GENOMICS_OPERATIONS_STORE` to a writable SQLite file path on a private
volume to enable operations. Use a separate volume from the read-only
prepared files. Each run persists a versioned receipt with its request ID.
Use that ID to find the corresponding audit event. Audit events contain
the account, route, status and identity of the request. Quality receipts
contain aggregate counts and sheet names. Rotate the logs and back up the
receipt store with the deployment's other operational records.

All endpoints in the following table use the prefix `/api/microcosting`.
`date_range` and `time_range` are optional JSON query parameters with
inclusive UTC dates, for example `{"start":"2026-11-01","end":"2026-11-30"}`.
History returns at most 100 recent matching receipts per result list.

| Method and path | Inputs or result |
| --- | --- |
| `POST /tests/run` | `test_type` is `integration`, `end_to_end` or `performance`. Optional `analysis_modules` selects from `cost_driver`, `dsa`, `psa` and `voi`. Runs bounded synthetic diagnostics against the installed analyses. |
| `GET /tests/results` | Optional `test_type`, `analysis_module` and `date_range` filters. |
| `POST /performance/benchmark` | `data_set_size` sizes the cost-driver workload. `iterations` sizes the seeded Monte Carlo workload. Both are integers from 1 to 10,000. |
| `GET /performance/metrics` | Optional `analysis_type` and `time_range` filters on diagnostic and benchmark timings. |
| `GET /monitoring/health` | Read the underlying health checks and overall status. |
| `GET /monitoring/metrics` | Optional `metric_type` selects `cpu`, `memory` or `execution_time`. |
| `GET /monitoring/data-quality` | Read quality receipts, optionally filtered by `sheet_name`. |
| `POST /data-quality/validate` | Select prepared `sheet_names` and `validation_types` from `integrity`, `consistency` and `anomalies`. Consistency compares paired CSV and Parquet when both exist. |
| `GET /data-quality/reports` | Read retained aggregate quality reports with an optional `date_range`. |

The lab template page at `/models` walks through model selection, a
profile and a final download. Enter JSON, choose or drop a file, or build a
profile with the on-page editor. The downloaded input template includes
the selected local categories and leaves cost values for the lab to supply.
