# =============================================================================
# variables.tf — all inputs for this Terraform stack (beginner-friendly)
# =============================================================================
# You set real values in *terraform.tfvars* (see terraform.tfvars.example).
# Do NOT commit terraform.tfvars if it contains secrets — it is gitignored.
# =============================================================================

variable "resource_group_name" {
  type        = string
  description = "Name of the EXISTING Resource Group (e.g. CLOUD_PROJECT)."
}

variable "location" {
  type        = string
  description = "Azure region for NEW resources. Use East Asia to match your project."
  default     = "East Asia"
}

variable "environment" {
  type        = string
  description = "Short environment label used in resource names and tags (e.g. dev, prod)."
  default     = "dev"
}

variable "project_name" {
  type        = string
  description = "Short project name used in naming and tags (e.g. taskmanager)."
  default     = "taskmanager"
}

# --- Log Analytics naming (constructed if you leave components empty) ---

variable "log_analytics_name" {
  type        = string
  description = "If non-empty, use this exact Log Analytics workspace name (must be unique in RG)."
  default     = ""
}

variable "log_analytics_name_suffix" {
  type        = string
  description = "Suffix for auto-generated Log Analytics name if log_analytics_name is empty."
  default     = "law"
}

variable "log_analytics_retention_days" {
  type        = number
  description = "How many days to retain logs in Log Analytics."
  default     = 30
}

# --- Application Insights naming & options ---

variable "application_insights_name" {
  type        = string
  description = "If non-empty, use this exact Application Insights name (must be unique in RG)."
  default     = ""
}

variable "application_insights_name_suffix" {
  type        = string
  description = "Suffix for auto-generated Application Insights name if application_insights_name is empty."
  default     = "insights"
}

variable "application_insights_sampling_percentage" {
  type        = number
  description = "Percentage of telemetry to sample (100 = full sampling)."
  default     = 100
}

# --- Key Vault ---

variable "key_vault_name" {
  type        = string
  description = "Globally unique Key Vault name: 3–24 chars, letters and digits only (e.g. kvtaskmgrdev01)."
}

variable "key_vault_soft_delete_retention_days" {
  type        = number
  description = "Soft-delete retention for Key Vault (7–90)."
  default     = 7
}

variable "key_vault_purge_protection_enabled" {
  type        = bool
  description = "If true, vault cannot be purged immediately — safer for production, harder for learning."
  default     = false
}

# --- Storage Account ---

variable "storage_account_name" {
  type        = string
  description = "Globally unique storage account name: 3–24 chars, lowercase letters and numbers only."
}

variable "storage_account_tier" {
  type        = string
  description = "Storage tier: Standard or Premium (GPv2 usually uses Standard)."
  default     = "Standard"
}

variable "storage_replication_type" {
  type        = string
  description = "Replication: LRS cheapest; GRS/RA-GRS for higher durability."
  default     = "LRS"
}

variable "storage_container_name" {
  type        = string
  description = "Blob container name for private app data (lowercase, 3–63 chars)."
  default     = "appdata"
}

variable "extra_tags" {
  type        = map(string)
  description = "Optional extra tags merged into all resources."
  default     = {}
}
