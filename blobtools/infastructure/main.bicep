param storageAccountName string = 'anboidxtgs'
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
    resource input 'containers' = {
      name: 'input'
    }
    resource middle 'containers' = {
      name: 'middle'
    }
    resource output 'containers' = {
      name: 'output'
    }
  }

  resource queueServices 'queueServices' = {
    name: 'default'
    resource step1 'queues' = {
      name: 'step1'
    }
    resource step2 'queues' = {
      name: 'step2'
    }
  }
}

resource systemTopicsBlobEvents 'Microsoft.EventGrid/systemTopics@2022-06-15' = {
  name: 'anboidxtgs-blob-events'
  location: location
  properties: {
    source: storageAccount.id
    topicType: 'Microsoft.Storage.StorageAccounts'
  }
  resource step1QueueSubscription 'eventSubscriptions' = {
    name: 'step1QueueSubscription'
    properties: {
      destination: {
        properties: {
          resourceId: storageAccount.id
          queueName: storageAccount::queueServices::step1.name
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

output storageAccountConnectionString string = storageAccount.properties.primaryEndpoints.blob
output storageQueueConnectionString string = storageAccount.properties.primaryEndpoints.queue
