# =============================================================================
# Azure Task Manager — add-on resources (Terraform)
# =============================================================================
# This stack does NOT recreate your existing App Service, PostgreSQL, ACR, or
# Static Web App. It only provisions:
#   • Log Analytics Workspace
#   • Application Insights (workspace-based; recommended by Microsoft)
#   • Key Vault
#   • Storage Account
#
# Your existing Resource Group is referenced with a *data source* so Terraform
# attaches new resources to CLOUD_PROJECT (or whatever name you set in tfvars).
#
# -----------------------------------------------------------------------------
# BEGINNER: Commands to run (from THIS folder in a terminal)
# -----------------------------------------------------------------------------
#   cd infra/terraform/azure-taskmanager-addons
#
#   # 1) Log in to Azure (opens browser) — skip if already logged in
#   az login
#
#   # 2) Pick subscription (if you have more than one)
#   az account set --subscription "YOUR-SUBSCRIPTION-ID-OR-NAME"
#
#   # 3) Copy the example variables file and edit values (names must be GLOBALLY unique)
#   #    Windows PowerShell:
#   Copy-Item terraform.tfvars.example terraform.tfvars
#
#   # 4) Initialize Terraform (downloads the Azure provider, creates .terraform/)
#   terraform init
#
#   # 5) Preview changes (no changes applied yet)
#   terraform plan
#
#   # 6) Apply changes (type *yes* when prompted, or use -auto-approve carefully)
#   terraform apply
#
# After apply: copy outputs (e.g. Application Insights connection string) into
# your App Service *Configuration* → *Application settings*.
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.114"
    }
  }
}

# Authenticate with Azure CLI (`az login`). For CI, use a service principal instead.
provider "azurerm" {
  features {
    key_vault {
      # Beginner-friendly: allow purge after delete during learning (turn ON in prod if policy requires)
      purge_soft_delete_on_destroy = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Who is running Terraform? Used to grant *you* access to Key Vault secrets.
data "azurerm_client_config" "current" {}

# Existing Resource Group — created manually in the Azure Portal
data "azurerm_resource_group" "main" {
  name = var.resource_group_name
}

# -----------------------------------------------------------------------------
# Log Analytics Workspace — required "back end" for modern Application Insights
# -----------------------------------------------------------------------------
resource "azurerm_log_analytics_workspace" "main" {
  name                = local.log_analytics_name
  location            = var.location
  resource_group_name = data.azurerm_resource_group.main.name

  # Pay-as-you-go SKU is typical for learning and small projects
  sku               = "PerGB2018"
  retention_in_days = var.log_analytics_retention_days

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Application Insights — telemetry for your API (connect string → App Service)
# -----------------------------------------------------------------------------
resource "azurerm_application_insights" "main" {
  name                = local.app_insights_name
  location            = var.location
  resource_group_name = data.azurerm_resource_group.main.name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.main.id
  sampling_percentage = var.application_insights_sampling_percentage
  # Retention for workspace-based Insights is primarily governed by Log Analytics
  # (see log_analytics_retention_days). Omitting retention_in_days avoids provider quirks.

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Key Vault — store secrets (DB passwords, JWT keys) instead of plain app settings
# Name rules: 3–24 characters, letters and digits ONLY (no hyphens).
# -----------------------------------------------------------------------------
resource "azurerm_key_vault" "main" {
  name                = var.key_vault_name
  location            = var.location
  resource_group_name = data.azurerm_resource_group.main.name

  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  enable_rbac_authorization  = false
  enabled_for_disk_encryption = false

  # "Soft delete" protects against accidental deletion; recovery window in days
  soft_delete_retention_days = var.key_vault_soft_delete_retention_days

  # Beginners: leave false unless your org requires purge protection (harder to delete)
  purge_protection_enabled = var.key_vault_purge_protection_enabled

  # Grant the Terraform runner permission to manage secrets in this vault
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get",
      "List",
      "Set",
      "Delete",
      "Recover",
      "Purge",
    ]
  }

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Storage Account — general purpose (logs export, artifacts, Terraform state later)
# Name rules: 3–24 chars, lowercase letters and numbers ONLY.
# -----------------------------------------------------------------------------
resource "azurerm_storage_account" "main" {
  name                     = var.storage_account_name
  resource_group_name      = data.azurerm_resource_group.main.name
  location                 = var.location
  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_replication_type

  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  https_traffic_only_enabled      = true

  tags = local.common_tags
}

# Optional: a private blob container for app-related files (not public)
resource "azurerm_storage_container" "app" {
  name                  = var.storage_container_name
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}
