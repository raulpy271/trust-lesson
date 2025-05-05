
terraform {
  required_providers {
    archive = {
      source  = "hashicorp/archive"
      version = "2.7.0"
    }
  }
}

locals {
  local_app_settings = {
    SCM_DO_BUILD_DURING_DEPLOYMENT = true
    APPINSIGHTS_INSTRUMENTATIONKEY = azurerm_application_insights.application_insights.instrumentation_key
    VISION_APIKEY                  = azurerm_cognitive_account.vision.primary_access_key
    VISION_ENDPOINT                = azurerm_cognitive_account.vision.endpoint
  }
  app_settings = merge(local.local_app_settings, var.app_envs)
}

resource "azurerm_service_plan" "functions_sp" {
  name                = "functions-sp-${var.stage}"
  resource_group_name = var.rg_name
  location            = var.rg_location
  os_type             = "Linux"
  sku_name            = "B1"
  tags = {
    "stage" = var.stage
  }
}

resource "azurerm_cognitive_account" "vision" {
  name                          = "vision-${var.stage}"
  resource_group_name           = var.rg_name
  location                      = var.rg_location
  kind                          = "ComputerVision"
  sku_name                      = "F0"
  public_network_access_enabled = true
  tags = {
    "stage"    = var.stage
    Acceptance = "Test"
  }
}

resource "terraform_data" "requirements" {
  triggers_replace = {
    always = uuid()
  }
  provisioner "local-exec" {
    command     = "poetry export -n --without-hashes --format=requirements.txt > requirements.txt && cat function-requirements.txt >> requirements.txt"
    working_dir = "../api"
  }
}

data "archive_file" "api_zip" {
  type        = "zip"
  output_path = "../api/dist/functions-${uuid()}.zip"
  source_dir  = "../api"
  excludes    = ["Dockerfile*", "*.env", "tests", "dist", "**/__pycache__", ".pytest_cache"]
  depends_on = [
    terraform_data.requirements
  ]
}

resource "azurerm_monitor_action_group" "smart_detector" {
  name                = "Application Insights Smart Detection"
  short_name          = "SmartDetect"
  resource_group_name = var.rg_name
}

resource "azurerm_application_insights" "application_insights" {
  name                = "function-application-insights-${var.stage}"
  resource_group_name = var.rg_name
  location            = var.rg_location
  application_type    = "other"
  depends_on          = [azurerm_monitor_action_group.smart_detector]
}

resource "azurerm_linux_function_app" "schedule_functions" {
  name                       = "schedule-functions-${var.stage}"
  resource_group_name        = var.rg_name
  location                   = var.rg_location
  service_plan_id            = azurerm_service_plan.functions_sp.id
  storage_account_name       = var.storage_account_name
  storage_account_access_key = var.storage_access_key
  zip_deploy_file            = data.archive_file.api_zip.output_path
  app_settings               = local.app_settings
  identity {
    type = "SystemAssigned"
  }
  site_config {
    health_check_path = "/api/health"
    health_check_eviction_time_in_min = 5
    always_on = true
    application_stack {
      python_version = "3.12"
    }
  }
  tags = {
    "stage" = var.stage
  }
  provisioner "local-exec" {
    command = "rm ../api/dist/functions-*.zip"
    when    = destroy
  }
}

data "azurerm_subscription" "primary" {
}

resource "azurerm_role_assignment" "blob_delegator_role" {
  scope                = data.azurerm_subscription.primary.id
  role_definition_name = "Storage Blob Delegator"
  principal_id         = azurerm_linux_function_app.schedule_functions.identity[0].principal_id
}

resource "azurerm_role_assignment" "storage_role" {
  scope                = data.azurerm_subscription.primary.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_linux_function_app.schedule_functions.identity[0].principal_id
}

