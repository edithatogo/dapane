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
