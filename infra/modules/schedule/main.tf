
terraform {
  required_providers {
    archive = {
      source = "hashicorp/archive"
      version = "2.7.0"
    }
  }
}

locals {
  zip_file = "../api/dist/api-0.1.0-py3-none-any.whl"
  local_app_settings = {
    SCM_DO_BUILD_DURING_DEPLOYMENT = true
    APPINSIGHTS_INSTRUMENTATIONKEY = azurerm_application_insights.application_insights.instrumentation_key
    ZIP_HASH                       = data.archive_file.api_zip.output_md5
  }
  app_settings = merge(local.local_app_settings, var.app_envs)
}
resource "azurerm_service_plan" "functions_sp" {
  name                = "functions-sp-${var.stage}"
  resource_group_name = var.rg_name
  location            = var.rg_location
  os_type             = "Linux"
  sku_name            = "Y1"
  tags = {
    "stage" = var.stage
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
  output_path = local.zip_file
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

resource "azurerm_linux_function_app" "update_status_lesson" {
  name                       = "update-status-lesson-${var.stage}"
  resource_group_name        = var.rg_name
  location                   = var.rg_location
  service_plan_id            = azurerm_service_plan.functions_sp.id
  storage_account_name       = var.storage_account_name
  storage_account_access_key = var.storage_access_key
  zip_deploy_file            = local.zip_file
  app_settings               = local.app_settings
  site_config {
    always_on = false
    application_stack {
      python_version = "3.12"
    }
  }
  tags = {
    "stage" = var.stage
  }
  depends_on = [
    data.archive_file.api_zip
  ]
}

