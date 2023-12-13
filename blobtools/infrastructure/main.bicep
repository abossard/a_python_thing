param project string = 'idxt'
param prefix string = 'anbo'
param storageAccountName string = '${prefix}${project}st'
param location string = resourceGroup().location
var inventoryContainerName = 'inventory'
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }

  
  resource blobServices 'blobServices' = {
    name: 'default'
    resource saga 'containers' = {
      name: 'saga'
    }
    resource inventory 'containers' = {
      name: inventoryContainerName
    }
    resource timeseries 'containers' = {
      name: 'timeseries'
    }
  }

  resource queueServices 'queueServices' = {
    name: 'default'
    resource newSagaQueue 'queues' = {
      name: 'new-saga'
    }
    resource completedSagaQueue 'queues' = {
      name: 'completed-saga'
    }
  }
}

resource inventory 'Microsoft.Storage/storageAccounts/inventoryPolicies@2023-01-01' = {
  name: 'default'
  parent: storageAccount
  properties: {
    policy: {
      enabled: true
      type: 'Inventory'
      rules: [
        {
          destination: storageAccount::blobServices::inventory.name
          enabled: true
          name: 'inventory'
          definition: {
            format: 'Csv'
            schedule: 'Daily'
            objectType: 'Blob'
            schemaFields: [
              'Name'
              'Content-Length'
              'LeaseStatus'
              'Tags'
              'TagCount'
            ]
            filters: {
              blobTypes: [
                'blockBlob'
              ]
              prefixMatch: []
            }
          }
        }
      ]
    }
  }
}

resource systemTopicsBlobEvents 'Microsoft.EventGrid/systemTopics@2022-06-15' = {
  name: '${prefix}${project}blobEvents'
  location: location
  properties: {
    source: storageAccount.id
    topicType: 'Microsoft.Storage.StorageAccounts'
  }
  resource sagaQueueSubscription 'eventSubscriptions' = {
    name: 'sagaQueueSubscription'
    properties: {
      destination: {
        properties: {
          resourceId: storageAccount.id
          queueName: storageAccount::queueServices::newSagaQueue.name
        }
        endpointType: 'StorageQueue'
      }
      filter: {
        includedEventTypes: [
          'Microsoft.Storage.BlobCreated'
          'Microsoft.Storage.BlobDeleted'
          'Microsoft.Storage.BlobRenamed'
        ]
        enableAdvancedFilteringOnArrays: true
      }
      labels: []
      eventDeliverySchema: 'CloudEventSchemaV1_0'
      retryPolicy: {
        maxDeliveryAttempts: 30
        eventTimeToLiveInMinutes: 1440
      }
    }
  }
}

var primaryKey = storageAccount.listKeys().keys[0].value
var connectionString = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${primaryKey};EndpointSuffix=${environment().suffixes.storage}'

output deployEnvironment string = join([
    'STORAGE_ACCOUNT_CONNECTION_STRING="${connectionString}"'
    'STORAGE_ACCOUNT_NAME=${storageAccount.name}'
    'NEW_SAGA_QUEUE_NAME=${storageAccount::queueServices::newSagaQueue.name}'
    'COMPLETED_SAGA_QUEUE_NAME=${storageAccount::queueServices::completedSagaQueue.name}'
    'SAGA_CONTAINER_NAME=${storageAccount::blobServices::saga.name}'
    'TIMESERIES_CONTAINER_NAME=${storageAccount::blobServices::timeseries.name}'
    'AZURE_SDK_TRACING_IMPLEMENTATION=opentelemetry'
  ], '\n')
