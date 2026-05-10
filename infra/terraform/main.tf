terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.114"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_postgresql_flexible_server" "main" {
  name                   = var.postgres_server_name
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = var.postgres_version
  administrator_login    = var.postgres_admin_username
  administrator_password = var.postgres_admin_password
  storage_mb             = var.postgres_storage_mb
  sku_name               = var.postgres_sku_name

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  lifecycle {
    prevent_destroy = false
  }
}

# Allows Azure platform services (including App Service outbound) to reach the server.
resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure" {
  name             = "allow-azure-services"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

resource "azurerm_postgresql_flexible_server_database" "app" {
  name      = var.postgres_database_name
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = var.log_analytics_workspace_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_analytics_retention_days
}

resource "azurerm_application_insights" "main" {
  name                = var.application_insights_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
}

resource "azurerm_service_plan" "api" {
  name                = var.app_service_plan_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = var.app_service_plan_sku
}

locals {
  database_url = format(
    "postgresql+psycopg://%s:%s@%s:5432/%s?sslmode=require",
    var.postgres_admin_username,
    var.postgres_admin_password,
    azurerm_postgresql_flexible_server.main.fqdn,
    var.postgres_database_name
  )

  refresh_secret = trimspace(var.api_refresh_secret_key) != "" ? var.api_refresh_secret_key : var.api_secret_key
}

resource "azurerm_linux_web_app" "api" {
  name                = var.linux_web_app_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.api.id

  https_only = true

  site_config {
    always_on = var.app_service_always_on

    application_stack {
      python_version = var.linux_web_app_python_version
    }

    # Azure injects PORT at runtime; fall back to 8000 for local parity.
    app_command_line = "sh -c 'gunicorn backend.main:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$${PORT:-8000}'"

    health_check_path                 = "/health"
    health_check_eviction_time_in_min = 2
  }

  app_settings = {
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.main.connection_string
    APPINSIGHTS_INSTRUMENTATION_KEY       = azurerm_application_insights.main.instrumentation_key

    DATABASE_URL                        = local.database_url
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "false"

    SCM_DO_BUILD_DURING_DEPLOYMENT = "true"

    # Prefer Key Vault references for secrets in production environments.
    SECRET_KEY                  = var.api_secret_key
    REFRESH_SECRET_KEY          = local.refresh_secret
    ADMIN_EMAILS                = var.admin_emails_csv
    CORS_ORIGINS                = var.cors_origins_csv
    ACCESS_TOKEN_EXPIRE_MINUTES = tostring(var.access_token_expire_minutes)
    REFRESH_TOKEN_EXPIRE_DAYS   = tostring(var.refresh_token_expire_days)
    RATE_LIMIT_DEFAULT          = var.rate_limit_default
    RATE_LIMIT_AUTH             = var.rate_limit_auth
    USE_ML_PRIORITIZATION       = var.use_ml_prioritization
    ML_MODEL_PATH               = var.ml_model_path
  }
}
