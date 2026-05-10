output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "postgresql_fqdn" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}

output "linux_web_app_default_hostname" {
  value = azurerm_linux_web_app.api.default_hostname
}

output "application_insights_connection_string" {
  value     = azurerm_application_insights.main.connection_string
  sensitive = true
}

output "application_insights_instrumentation_key" {
  value     = azurerm_application_insights.main.instrumentation_key
  sensitive = true
}
