terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 2.0"
    }
  }
}

provider "azurerm" {
  features {}
}
variable "location" {
  type = string
  default = "westeurope"
}

variable "namespaces_anbopizza_name" {
  type = string
  default = "anbopizza"
}

variable "pizza_orders_queue_name" {
  type = string
  default = "pizza-orders"
}

resource "azurerm_servicebus_namespace" "anbopizza" {
  name                = var.namespaces_anbopizza_name
  location            = var.location
  sku                 = "Basic"
  resource_group_name = "anbopizza"
  default_primary_key = ""
  default_secondary_key = ""
}

resource "azurerm_servicebus_queue" "pizza_orders" {
    namespace_id = azurerm_servicebus_namespace.anbopizza.id
    name                = var.pizza_orders_queue_name
}

resource "azurerm_application_insights" "anbo_pizza_appi" {
  name                = var.components_anbo_pizza_appi_name_param
  location            = var.location
  application_type    = "web"
  flow_type           = "Redfield"
  request_source      = "IbizaAIExtension"
  retention_in_days   = 30
  workspace_resource_id = azurerm_log_analytics_workspace.anbo_pizza_law.id
  ingestion_mode      = "LogAnalytics"
  public_network_access_for_ingestion = true
  public_network_access_for_query     = true
}

resource "azurerm_cosmosdb_account" "anbo_pizza_mongodb" {
  name                = var.databaseAccounts_anbo_pizza_mongodb_name
  location            = var.location
  offer_type          = "Standard"
  kind                = "MongoDB"
  consistency_policy {
    consistency_level = "Session"
    max_interval_in_seconds = 5
    max_staleness_prefix = 100
  }
  capabilities {
    name = "EnableMongo"
  }
  capabilities {
    name = "DisableRateLimitingResponses"
  }
  capabilities {
    name = "EnableServerless"
  }
  enable_free_tier = true
  enable_analytical_storage = false
  enable_automatic_failover = false
  enable_multiple_write_locations = false
  is_virtual_network_filter_enabled = false
  enable_free_tier = true
  enable_analytical_storage = false
  analytical_storage_configuration {
    schema_type = "FullFidelity"
  }
  locations {
    location_name = var.location
    failover_priority = 0
    is_zone_redundant = false
  }
}

resource "azurerm_log_analytics_workspace" "anbo_pizza_law" {
  name                = var.workspaces_anbo_pizza_law_name
  location            = var.location
  sku                 = "pergb2018"
  retention_in_days   = 30
  features {
    enable_log_access_using_only_resource_permissions = true
  }
  workspace_capping {
    daily_quota_gb = -1
  }
  public_network_access_for_ingestion = true
  public_network_access_for_query     = true
}

resource "azurerm_storage_account" "anbopizzastore" {
  name                = var.storageAccounts_anbopizzastore_name
  location            = var.location
  resource_group_name = azurerm_resource_group.example.name
  account_tier        = "Standard"
  account_replication_type = "LRS"
  enable_https_traffic_only = true
  allow_blob_public_access = false
  network_rules {
    default_action = "Allow"
    bypass         = "AzureServices"
  }
  encryption {
    services {
      file {
        enabled = true
        key_type = "Account"
      }
      blob {
        enabled = true
        key_type = "Account"
      }
    }
    key_source = "Microsoft.Storage"
  }
}

resource "azurerm_servicebus_namespace_authorization_rule" "anbopizza_read_and_listen" {
  name                = "ReadAndListen"
  namespace_name      = azurerm_servicebus_namespace.anbopizza.name
  listen              = true
  send                = true
}

resource "azurerm_servicebus_namespace_authorization_rule" "anbopizza_root_manage_shared_access_key" {
  name                = "RootManageSharedAccessKey"
  namespace_name      = azurerm_servicebus_namespace.anbopizza.name
  listen              = true
  manage              = true
  send                = true
}

resource "azurerm_app_service_environment" "anbo_pizza_app_env" {
  name                = var.managedEnvironments_anbo_pizza_app_env_name_param
  location            = var.location
  app_logs_configuration {
    destination = "log-analytics"
    log_analytics_configuration {
      customer_id = azurerm_log_analytics_workspace.anbo_pizza_law.customer_id
      shared_key  = azurerm_log_analytics_workspace.anbo_pizza_law.primary_shared_key
    }
  }
  peer_authentication {
    mtls {
      enabled = false
    }
  }
}

resource "azurerm_app_service" "anbo_pizza_nginx" {
  name                = var.containerapps_anbo_pizza_nginx_name_param
  location            = var.location
  app_service_environment_id = azurerm_app_service_environment.anbo_pizza_app_env.id
  app_service_plan_id = azurerm_app_service_plan.example.id
  site_config {
    always_on = true
    linux_fx_version = "DOCKER|nginx"
  }
}

resource "azurerm_app_service" "anbo_pizza_web" {
  name                = var.containerapps_anbo_pizza_web_name_param
  location            = var.location
  app_service_environment_id = azurerm_app_service_environment.anbo_pizza_app_env.id
  app_service_plan_id = azurerm_app_service_plan.example.id
  site_config {
    always_on = true
    linux_fx_version = "DOCKER|mcr.microsoft.com/k8se/quickstart:latest"
  }
}

resource "azurerm_servicebus_namespace_network_rule_set" "anbopizza_default" {
  name                = "default"
  namespace_name      = azurerm_servicebus_namespace.anbopizza.name
  public_network_access = "Enabled"
  default_action = "Allow"
}

resource "azurerm_storage_account_blob_service_properties" "anbopizzastore_default" {
  name                = "${azurerm_storage_account.anbopizzastore.name}/default"
  storage_account_name = azurerm_storage_account.anbopizzastore.name
  is_versioning_enabled = false
}

resource "azurerm_storage_account_file_service_properties" "anbopizzastore_default" {
  name                = "${azurerm_storage_account.anbopizzastore.name}/default"
  storage_account_name = azurerm_storage_account.anbopizzastore.name
}

resource "azurerm_storage_account_queue_service_properties" "anbopizzastore_default" {
  name                = "${azurerm_storage_account.anbopizzastore.name}/default"
  storage_account_name = azurerm_storage_account.anbopizzastore.name
}

resource "azurerm_storage_account_table_service_properties" "anbopizzastore_default" {
  name                = "${azurerm_storage_account.anbopizzastore.name}/default"
  storage_account_name = azurerm_storage_account.anbopizzastore.name
}