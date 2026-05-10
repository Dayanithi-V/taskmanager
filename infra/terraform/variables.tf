variable "location" {
  type        = string
  description = "Azure region for resources."
  default     = "eastasia"
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name."
}

variable "postgres_server_name" {
  type        = string
  description = "PostgreSQL Flexible Server name (globally unique DNS prefix)."
}

variable "postgres_database_name" {
  type        = string
  description = "Database name for the application."
  default     = "taskmanager"
}

variable "postgres_admin_username" {
  type        = string
  description = "PostgreSQL admin username."
}

variable "postgres_admin_password" {
  type        = string
  description = "PostgreSQL admin password."
  sensitive   = true
}

variable "postgres_version" {
  type        = string
  description = "PostgreSQL major version."
  default     = "16"
}

variable "postgres_storage_mb" {
  type        = number
  description = "PostgreSQL storage size (MB)."
  default     = 32768
}

variable "postgres_sku_name" {
  type        = string
  description = "PostgreSQL SKU (Flexible Server)."
  default     = "B_Standard_B1ms"
}

variable "log_analytics_workspace_name" {
  type        = string
  description = "Log Analytics workspace name."
}

variable "log_analytics_retention_days" {
  type        = number
  default     = 30
}

variable "application_insights_name" {
  type        = string
  description = "Application Insights component name."
}

variable "app_service_plan_name" {
  type        = string
  description = "App Service Plan name."
}

variable "app_service_plan_sku" {
  type        = string
  description = "App Service Plan SKU for Linux apps."
  default     = "B1"
}

variable "linux_web_app_name" {
  type        = string
  description = "Linux Web App name (globally unique)."
}

variable "linux_web_app_python_version" {
  type        = string
  description = "Python runtime version string for Linux Web App."
  default     = "3.12"
}

variable "app_service_always_on" {
  type        = bool
  description = "Enable Always On (recommended for paid SKUs)."
  default     = false
}

variable "api_secret_key" {
  type        = string
  description = "JWT signing secret for access tokens."
  sensitive   = true
}

variable "api_refresh_secret_key" {
  type        = string
  description = "JWT signing secret for refresh tokens (falls back to api_secret_key when blank)."
  default     = ""
  sensitive   = true
}

variable "admin_emails_csv" {
  type        = string
  description = "Comma-separated admin emails for role assignment on registration."
  default     = ""
}

variable "cors_origins_csv" {
  type        = string
  description = "Comma-separated CORS origins."
}

variable "access_token_expire_minutes" {
  type        = number
  default     = 1440
}

variable "refresh_token_expire_days" {
  type        = number
  default     = 7
}

variable "rate_limit_default" {
  type        = string
  default     = "120/minute"
}

variable "rate_limit_auth" {
  type        = string
  default     = "20/minute"
}

variable "use_ml_prioritization" {
  type        = string
  description = "true/false string for ML toggle."
  default     = "false"
}

variable "ml_model_path" {
  type        = string
  default     = "backend/ml/model/priority_model.joblib"
}
