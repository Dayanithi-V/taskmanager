# =============================================================================
# locals.tf — computed names and shared tags
# =============================================================================
# Azure naming: many resources must be unique. We build readable names from
# project + environment + suffix. Override with explicit variables when needed.
# =============================================================================

locals {
  # Safe short slug for names (alphanumeric only where required by Azure)
  slug = lower(replace("${var.project_name}${var.environment}", "-", ""))

  log_analytics_name = trimspace(var.log_analytics_name) != "" ? var.log_analytics_name : "${local.slug}${var.log_analytics_name_suffix}"

  app_insights_name = trimspace(var.application_insights_name) != "" ? var.application_insights_name : "${local.slug}${var.application_insights_name_suffix}"

  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.extra_tags,
  )
}
