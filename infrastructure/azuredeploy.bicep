param namespaces_anbopizza_name string = 'anbopizza'
param location string = resourceGroup().location
param components_anbo_pizza_appi_name_param string = 'anbo-pizza-appi'
param storageAccounts_anbopizzastore_name string = 'anbopizzastore'
param workspaces_anbo_pizza_law_name string = 'anbo-pizza-law'
param databaseAccounts_anbo_pizza_mongodb_name string = 'anbo-pizza-mongodb'
param managedEnvironments_anbo_pizza_app_env_name_param string = 'anbo-pizza-app-env'
param containerapps_anbo_pizza_web_name_param string = 'anbo-pizza-web'
param pizza_orders_queue_name string = 'pizza-orders'

resource components_anbo_pizza_appi_name 'microsoft.insights/components@2020-02-02' = {
  name: components_anbo_pizza_appi_name_param
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Flow_Type: 'Redfield'
    Request_Source: 'IbizaAIExtension'
    RetentionInDays: 30
    WorkspaceResourceId: workspaces_anbo_pizza_law_name_resource.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

resource databaseAccounts_anbo_pizza_mongodb_name_resource 'Microsoft.DocumentDB/databaseAccounts@2023-09-15' = {
  name: databaseAccounts_anbo_pizza_mongodb_name
  location: location
  tags: {
    defaultExperience: 'Azure Cosmos DB for MongoDB API'
    'hidden-cosmos-mmspecial': ''
  }
  kind: 'MongoDB'
  identity: {
    type: 'None'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
    isVirtualNetworkFilterEnabled: false
    virtualNetworkRules: []
    disableKeyBasedMetadataWriteAccess: false
    enableFreeTier: true
    enableAnalyticalStorage: false
    analyticalStorageConfiguration: {
      schemaType: 'FullFidelity'
    }
    databaseAccountOfferType: 'Standard'
    defaultIdentity: 'FirstPartyIdentity'
    networkAclBypass: 'None'
    disableLocalAuth: false
    enablePartitionMerge: false
    enableBurstCapacity: false
    minimalTlsVersion: 'Tls12'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
      maxIntervalInSeconds: 5
      maxStalenessPrefix: 100
    }
    apiProperties: {
      serverVersion: '4.2'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    cors: []
    capabilities: [
      {
        name: 'EnableMongo'
      }
      {
        name: 'DisableRateLimitingResponses'
      }
      {
        name: 'EnableServerless'
      }
    ]
    ipRules: []
    backupPolicy: {
      type: 'Periodic'
      periodicModeProperties: {
        backupIntervalInMinutes: 240
        backupRetentionIntervalInHours: 8
        backupStorageRedundancy: 'Local'
      }
    }
    networkAclBypassResourceIds: []
  }
}

resource workspaces_anbo_pizza_law_name_resource 'Microsoft.OperationalInsights/workspaces@2021-12-01-preview' = {
  name: workspaces_anbo_pizza_law_name
  location: location
  properties: {
    sku: {
      name: 'pergb2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    workspaceCapping: { 
      dailyQuotaGb: -1
    }
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

resource namespaces_anbopizza_name_resource 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: namespaces_anbopizza_name
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  properties: {
    premiumMessagingPartitions: 0
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
    zoneRedundant: false
  }
  resource pizza_orders 'queues' = {
    name: pizza_orders_queue_name
    properties: {

    }
  }
}

resource storageAccounts_anbopizzastore_name_resource 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccounts_anbopizzastore_name
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    dnsEndpointType: 'Standard'
    defaultToOAuthAuthentication: false
    publicNetworkAccess: 'Enabled'
    allowCrossTenantReplication: false
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    networkAcls: {
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
      defaultAction: 'Allow'
    }
    supportsHttpsTrafficOnly: true
    encryption: {
      requireInfrastructureEncryption: false
      services: {
        file: {
          keyType: 'Account'
          enabled: true
        }
        blob: {
          keyType: 'Account'
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    accessTier: 'Hot'
  }
}
resource namespaces_anbopizza_name_ReadAndListenAccessKey 'Microsoft.ServiceBus/namespaces/authorizationrules@2022-10-01-preview' = {
  parent: namespaces_anbopizza_name_resource
  name: 'ReadAndListen'
  properties: {
    rights: [
      'Listen'
      'Send'
    ]
  }
}

resource namespaces_anbopizza_name_RootManageSharedAccessKey 'Microsoft.ServiceBus/namespaces/authorizationrules@2022-10-01-preview' = {
  parent: namespaces_anbopizza_name_resource
  name: 'RootManageSharedAccessKey'
  properties: {
    rights: [
      'Listen'
      'Manage'
      'Send'
    ]
  }
}

resource managedEnvironments_anbo_pizza_app_env_name 'Microsoft.App/managedEnvironments@2023-05-02-preview' = {
  name: managedEnvironments_anbo_pizza_app_env_name_param
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: workspaces_anbo_pizza_law_name_resource.properties.customerId
        sharedKey: workspaces_anbo_pizza_law_name_resource.listKeys().primarySharedKey
      }
    }
    zoneRedundant: false
    kedaConfiguration: {}
    daprConfiguration: {}
    customDomainConfiguration: {}
    peerAuthentication: {
      mtls: {
        enabled: false
      }
    }
  }
}

resource containerapps_anbo_pizza_web_name 'Microsoft.App/containerapps@2023-05-02-preview' = {
  name: containerapps_anbo_pizza_web_name_param
  location: location
  identity: {
    type: 'None'
  }
  properties: {
    managedEnvironmentId: managedEnvironments_anbo_pizza_app_env_name.id
    environmentId: managedEnvironments_anbo_pizza_app_env_name.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 80
        exposedPort: 0
        transport: 'Auto'
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
        allowInsecure: false
      }
    }
    template: {
      containers: [
        {
          image: 'mcr.microsoft.com/k8se/quickstart:latest'
          name: 'simple-hello-world-container'
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 10
      }
    }
  }
}

resource namespaces_anbopizza_name_default 'Microsoft.ServiceBus/namespaces/networkrulesets@2022-10-01-preview' = {
  parent: namespaces_anbopizza_name_resource
  name: 'default'
  properties: {
    publicNetworkAccess: 'Enabled'
    defaultAction: 'Allow'
    virtualNetworkRules: []
    ipRules: []
    trustedServiceAccessEnabled: false
  }
}

resource storageAccounts_anbopizzastore_name_default 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccounts_anbopizzastore_name_resource
  name: 'default'
  properties: {
    changeFeed: {
      enabled: false
    }
    restorePolicy: {
      enabled: false
    }
    containerDeleteRetentionPolicy: {
      enabled: false
    }
    cors: {
      corsRules: []
    }
    deleteRetentionPolicy: {
      allowPermanentDelete: false
      enabled: false
    }
    isVersioningEnabled: false
  }
  resource pizza_container 'containers' = {
    name: 'pizza'
    properties: {
      publicAccess: 'None'
    }
  }
}

resource Microsoft_Storage_storageAccounts_fileServices_storageAccounts_anbopizzastore_name_default 'Microsoft.Storage/storageAccounts/fileServices@2023-01-01' = {
  parent: storageAccounts_anbopizzastore_name_resource
  name: 'default'
  properties: {
    protocolSettings: {
      smb: {}
    }
    cors: {
      corsRules: []
    }
    shareDeleteRetentionPolicy: {
      enabled: false
    }
  }
}

resource Microsoft_Storage_storageAccounts_queueServices_storageAccounts_anbopizzastore_name_default 'Microsoft.Storage/storageAccounts/queueServices@2023-01-01' = {
  parent: storageAccounts_anbopizzastore_name_resource
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
  }
}

resource Microsoft_Storage_storageAccounts_tableServices_storageAccounts_anbopizzastore_name_default 'Microsoft.Storage/storageAccounts/tableServices@2023-01-01' = {
  parent: storageAccounts_anbopizzastore_name_resource
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
  }
}
