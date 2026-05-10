# =============================================================================
# outputs.tf — values to copy into App Service, GitHub Secrets, or your notes
# =============================================================================

output "resource_group_name" {
  description = "Existing resource group that owns the new resources."
  value       = data.azurerm_resource_group.main.name
}

output "location" {
  description = "Region where new resources were placed."
  value       = var.location
}

# --- Log Analytics ---

output "log_analytics_workspace_id" {
  description = "Resource ID of the Log Analytics workspace."
  value       = azurerm_log_analytics_workspace.main.id
}

output "log_analytics_workspace_name" {
  description = "Name of the Log Analytics workspace."
  value       = azurerm_log_analytics_workspace.main.name
}

# --- Application Insights ---

output "application_insights_name" {
  description = "Application Insights resource name."
  value       = azurerm_application_insights.main.name
}

output "application_insights_instrumentation_key" {
  description = "Legacy instrumentation key (some SDKs still use it)."
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "Connection string for OpenTelemetry / APPLICATIONINSIGHTS_CONNECTION_STRING."
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

# --- Key Vault ---

output "key_vault_id" {
  description = "Key Vault resource ID."
  value       = azurerm_key_vault.main.id
}

output "key_vault_name" {
  description = "Key Vault name (DNS prefix)."
  value       = azurerm_key_vault.main.name
}

output "key_vault_uri" {
  description = "Key Vault URI (e.g. https://myvault.vault.azure.net/)."
  value       = azurerm_key_vault.main.vault_uri
}

# --- Storage ---

output "storage_account_id" {
  description = "Storage account resource ID."
  value       = azurerm_storage_account.main.id
}

output "storage_account_name" {
  description = "Storage account name."
  value       = azurerm_storage_account.main.name
}

output "storage_container_name" {
  description = "Private blob container created for app data."
  value       = azurerm_storage_container.app.name
}

output "storage_primary_blob_endpoint" {
  description = "Primary blob service endpoint."
  value       = azurerm_storage_account.main.primary_blob_endpoint
}

output "storage_primary_connection_string" {
  description = "Primary connection string (treat as secret)."
  value       = azurerm_storage_account.main.primary_connection_string
  sensitive   = true
}
