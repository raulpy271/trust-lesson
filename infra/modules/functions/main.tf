
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
  }
  app_settings = merge(local.local_app_settings, var.app_envs)
}

resource "azurerm_service_plan" "functions_sp" {
  name                = "functions-sp-${var.stage}"
  resource_group_name = var.rg_name
  location            = var.rg_location
  os_type             = "Linux"
  sku_name            = "B2"
  tags = {
    "stage" = var.stage
  }
}

resource "terraform_data" "requirements" {
  triggers_replace = {
    always = uuid()
  }
  provisioner "local-exec" {
    command     = <<EOT
      poetry export -n --without-hashes --format=requirements.txt > requirements.txt
      sed -i '/api\s*@\s*file:/d' requirements.txt # Remove local package from requirements
    EOT
    working_dir = "../functions"
  }
}

resource "terraform_data" "functions_pkg" {
  triggers_replace = {
    always = uuid()
  }
  provisioner "local-exec" {
    command     = "./create-zip.sh"
    working_dir = "../functions"
  }
  depends_on = [
    terraform_data.requirements
  ]
}

data "archive_file" "api_zip" {
  type        = "zip"
  output_path = "../functions/dist/functions-${uuid()}.zip"
  source_dir  = "../functions/dist"
  excludes    = ["Dockerfile*", "*.env", "tests", "dist", "**/__pycache__", ".pytest_cache", ".poetry", "functions-*.zip"]
  depends_on = [
    terraform_data.functions_pkg
  ]
}

resource "azurerm_linux_function_app" "functions" {
  name                       = "trust-lesson-functions-${var.stage}"
  resource_group_name        = var.rg_name
  location                   = var.rg_location
  service_plan_id            = azurerm_service_plan.functions_sp.id
  storage_account_name       = var.storage_account_name
  storage_account_access_key = var.storage_access_key
  zip_deploy_file            = data.archive_file.api_zip.output_path
  app_settings               = local.app_settings
  builtin_logging_enabled    = true
  identity {
    type = "SystemAssigned"
  }
  site_config {
    health_check_path                 = "/api/health"
    health_check_eviction_time_in_min = 5
    application_insights_key          = var.insights_instrumentation_key
    always_on                         = true
    application_stack {
      python_version = "3.12"
    }
    app_service_logs {
      disk_quota_mb         = 25
      retention_period_days = 60
    }
  }
  tags = {
    "stage" = var.stage
  }
  provisioner "local-exec" {
    command = "rm -r ../functions/dist/*"
    when    = destroy
  }
}

data "azurerm_function_app_host_keys" "functions" {
  name                = azurerm_linux_function_app.functions.name
  resource_group_name = var.rg_name
}

data "azurerm_subscription" "primary" {
}

resource "azurerm_role_assignment" "blob_delegator_role" {
  scope                = data.azurerm_subscription.primary.id
  role_definition_name = "Storage Blob Delegator"
  principal_id         = azurerm_linux_function_app.functions.identity[0].principal_id
}

resource "azurerm_role_assignment" "storage_role" {
  scope                = data.azurerm_subscription.primary.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_linux_function_app.functions.identity[0].principal_id
}

