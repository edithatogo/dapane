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
Follow the [38-second lab setup tutorial](lab-setup.mp4) or its
[text walkthrough](lab-setup.md) using the synthetic panel example.

## Promote a dashboard image

Dispatch the Installed genomics package workflow on `main` with
`retain_dashboard=true` to export the Linux amd64 image that passed the
network-disabled smoke test. The workflow checks that the exported OCI
manifest references the tested container's image configuration. Download
`genomics-dashboard-image` and `genomics-dashboard-receipt` from that run.
The receipt identifies the source commit, image manifest, configuration
and archive SHA-256.

For live promotion, verify the archive with the receipt's checksum and
copy it into the approved registry. Require digest preservation, for
example with [Skopeo `copy --preserve-digests`](https://github.com/podman-container-tools/skopeo/blob/main/docs/skopeo-copy.1.md)
and its `oci-archive:` transport. Read back the manifest digest from the
registry and use that exact image reference in the dispatch.

The Genomics dashboard promotion workflow accepts the tested run ID as
`package_run` and the image reference as `image`. It verifies the digest
against the retained receipt from the successful GitHub-hosted package
run on the same `main` commit. It also checks the official GitHub-hosted
offline source scan and image advisory review for that commit. Keep the
image digest and source commit in the deployment record.

The default dispatch is evidence-only. An authorised operator selects
`deploy` after configuring the repository's `GENOMICS_DEPLOY_ENABLED` flag
and the applicable GitHub environment. The environment sets
`IMAGE_REPOSITORY` to the permitted image repository without a tag or
digest and supplies the scoped OIDC identity and runtime variables below.

| Environment | Identity and target |
| --- | --- |
| `genomics-aws` | `AWS_ROLE_ARN`, `AWS_REGION`, `ECS_CLUSTER` and `ECS_SERVICE`. Supply the prepared task definition revision ARN. The candidate must match the running revision's task settings and carry the selected image. |
| `genomics-azure` | `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_GROUP` and `AZURE_APP`. Update the existing internal single-revision app and read the latest ready revision. |

The workflow checks service stability and the selected image after
promotion. Keep the previous ECS task revision or Azure image digest for
recovery. Restore it using the existing provider deployment procedure,
then check readiness and read the expected prepared table list.

### Promotion options

| Option | Use when | Work to qualify |
| --- | --- | --- |
| Evidence-only dispatch | The repository has a retained candidate and live deployment is pending. | Verify the tested image manifest and retain the installed-package and official offline-security results for the exact commit. Keep the archive for a digest-preserving import to the approved registry. |
| Azure Container Apps | An authorised private Container Apps environment, registry and Azure Files share are already available. | Verify managed-identity image pull, internal TLS access and the read-only prepared-data mount. Record the ready revision, running digest and previous image for rollback. [Managed identity image pull](https://learn.microsoft.com/azure/container-apps/managed-identity-image-pull) [Revisions](https://learn.microsoft.com/azure/container-apps/revisions) |
| Amazon ECS on Fargate | An authorised private ECS service, ECR repository and EFS access point are already available. | Prepare the exact task revision and scoped task roles. Verify private connectivity, the running digest and restart behaviour. Retain the previous task revision and verify rollback. [Fargate networking](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-task-networking.html) [ECS deployment](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-ecs.html) |

Keep promotion evidence-only while deployment is pending. When an authorised
target exists, choose the provider whose private environment and durable
storage are already maintained. Use a synthetic data revision for the first
staging run. With an immutable digest and the existing OIDC workflow, check
readiness, authenticated readback, role restrictions, persisted receipts
and rollback. Carry the same qualified digest into any separately authorised
production promotion.

## Installed coverage

The Installed genomics package workflow can produce a Codecov report
from the installed wheel and the full packaged synthetic suite. For an
authorised `main` dispatch set `upload_coverage` after enabling
`GENOMICS_CODECOV_ENABLED` in the repository. The upload job uses an OIDC
token and one explicit XML input with repository-relative source paths.
It reports the `genomics-installed` flag. The inherited private suite
retains its separate local coverage evidence.
