// Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
@description('Existing Container Apps managed environment resource ID.')
param environmentId string

@description('Dashboard image including its SHA-256 digest.')
param image string

@description('Read-only Azure Files storage registered with the environment.')
param preparedStorageName string

@description('Container app name.')
param appName string = 'genomics-dashboard'

param location string = resourceGroup().location

resource dashboard 'Microsoft.App/containerApps@2025-01-01' = {
  name: appName
  location: location
  properties: {
    managedEnvironmentId: environmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: false
        allowInsecure: false
        targetPort: 8080
        transport: 'http'
      }
    }
    template: {
      containers: [
        {
          name: 'genomics'
          image: image
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          volumeMounts: [
            {
              volumeName: 'prepared'
              mountPath: '/prepared'
            }
          ]
          probes: [
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 8080
              }
              initialDelaySeconds: 5
              periodSeconds: 10
              timeoutSeconds: 3
              failureThreshold: 3
            }
          ]
        }
      ]
      volumes: [
        {
          name: 'prepared'
          storageType: 'AzureFile'
          storageName: preparedStorageName
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
  }
}
