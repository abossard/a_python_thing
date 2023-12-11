param project string = 'idxt'
param prefix string = 'anbo'
param storageAccountName string = '${prefix}${project}st'
param location string = resourceGroup().location

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

output deployEnvironment string = join([
  'STORAGE_ACCOUNT_CONNECTION_STRING=${storageAccount.properties.primaryEndpoints.blob}'
  'STORAGE_QUEUE_CONNECTION_STRING=${storageAccount.properties.primaryEndpoints.queue}'
  'STORAGE_ACCOUNT_NAME=${storageAccount.name}'
  'NEW_SAGA_QUEUE_NAME=${storageAccount::queueServices::newSagaQueue.name}'
  'COMPLETED_SAGA_QUEUE_NAME=${storageAccount::queueServices::completedSagaQueue.name}'
  'SAGA_CONTAINER_NAME=${storageAccount::blobServices::saga.name}'
  'TIMESERIES_CONTAINER_NAME=${storageAccount::blobServices::timeseries.name}'
], '\n')
