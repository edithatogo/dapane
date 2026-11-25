#!/usr/bin/env bash
# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
set -euo pipefail

fail() {
  printf '%s\n' "$1" >&2
  exit 2
}

case "${1:-}" in
  aws|azure) provider=$1 ;;
  *) fail 'Choose aws or azure' ;;
esac
[[ "${IMAGE:?Select an image by digest}" =~ ^[a-z0-9][a-z0-9./:_-]+@sha256:[0-9a-f]{64}$ ]] \
  || fail 'Select an image by digest'
[[ "${IMAGE%@*}" == "${IMAGE_REPOSITORY:?Configure the environment image repository}" ]] \
  || fail 'The candidate image is outside the configured repository'
digest=${IMAGE##*@}

ecs_service() {
  aws ecs describe-services --cluster "$ECS_CLUSTER" --services "$ECS_SERVICE" \
    --query 'services[0]' --output json
}

ecs_task() {
  aws ecs describe-task-definition --task-definition "$1" \
    --query taskDefinition --output json
}

ecs_settings() {
  jq -S 'del(
    .taskDefinitionArn, .revision, .registeredAt, .registeredBy, .deregisteredAt,
    .containerDefinitions[].image
  )'
}

azure_app() {
  az containerapp show --name "$AZURE_APP" --resource-group "$AZURE_GROUP" \
    --only-show-errors --output json
}

if [[ "$provider" == aws ]]; then
  : "${ECS_CLUSTER:?Configure an existing ECS cluster}"
  : "${ECS_SERVICE:?Configure an existing ECS service}"
  [[ "${ECS_TASK:?Supply a task definition revision ARN}" =~ ^arn:aws[^:]*:ecs:[^:]+:[0-9]{12}:task-definition/[a-zA-Z0-9_-]+:[1-9][0-9]*$ ]] \
    || fail 'Supply a task definition revision ARN'
  service=$(ecs_service)
  current=$(jq -er 'select(
    .status == "ACTIVE" and .desiredCount > 0 and .deploymentController.type == "ECS"
    and .networkConfiguration.awsvpcConfiguration.assignPublicIp == "DISABLED"
  ).taskDefinition' <<< "$service") || fail 'Expected an active private ECS service'
  previous=$(ecs_task "$current")
  candidate=$(ecs_task "$ECS_TASK")
  jq -e --arg image "$IMAGE" '(.containerDefinitions | length == 1)
    and (.containerDefinitions[0] | .name == "genomics" and .image == $image
    and any(.mountPoints[]; .containerPath == "/prepared" and .readOnly == true))' \
    <<< "$candidate" >/dev/null || fail 'The candidate does not match the image and prepared mount'
  previous_settings=$(ecs_settings <<< "$previous")
  candidate_settings=$(ecs_settings <<< "$candidate")
  [[ "$previous_settings" == "$candidate_settings" ]] \
    || fail 'The candidate changes task settings other than the image'
  before=$(jq -er '.containerDefinitions[0].image | split("@")[-1]' <<< "$previous")
  if [[ "$current" != "$ECS_TASK" ]]; then
    aws ecs update-service --cluster "$ECS_CLUSTER" --service "$ECS_SERVICE" \
      --task-definition "$ECS_TASK" --output json >/dev/null
  fi
  aws ecs wait services-stable --cluster "$ECS_CLUSTER" --services "$ECS_SERVICE"
  ecs_service | jq -e --arg task "$ECS_TASK" '.taskDefinition == $task and .runningCount > 0' >/dev/null \
    || fail 'The service stabilized on a different task revision'
else
  : "${AZURE_APP:?Configure an existing Container App}"
  : "${AZURE_GROUP:?Configure the existing resource group}"
  app=$(azure_app)
  previous_image=$(jq -er 'select(.properties.configuration.ingress.external == false
    and .properties.configuration.activeRevisionsMode == "Single")
    | .properties.template.containers | select(length == 1)
    | .[0] | select(.name == "genomics").image' <<< "$app") \
    || fail 'Expected a private single-revision genomics application'
  before=${previous_image##*@}
  if [[ "$previous_image" != "$IMAGE" ]]; then
    az containerapp update --name "$AZURE_APP" --resource-group "$AZURE_GROUP" \
      --container-name genomics --image "$IMAGE" --only-show-errors --output none
  fi
  ready=false
  for _ in {1..30}; do
    if azure_app | jq -e --arg image "$IMAGE" '
      .properties | .provisioningState == "Succeeded"
      and (.latestReadyRevisionName != null)
      and (.latestReadyRevisionName == .latestRevisionName)
      and any(.template.containers[]; .name == "genomics" and .image == $image)
    ' >/dev/null; then
      ready=true
      break
    fi
    sleep 10
  done
  [[ "$ready" == true ]] || fail 'Azure has not reported the requested ready revision'
fi

printf 'Promoted %s on %s\n' "$digest" "$provider"
if [[ "$before" =~ ^sha256:[0-9a-f]{64}$ ]]; then
  printf 'Previous image digest %s\n' "$before"
fi
