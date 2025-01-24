
locals {
  zip_file = abspath("api-build-${formatdate("YYYYMMDDHHmm", timestamp())}-${var.stage}.zip")
  local_app_settings = {
    SCM_DO_BUILD_DURING_DEPLOYMENT = true
  }
  app_settings = merge(local.local_app_settings, var.app_envs)
}

resource "terraform_data" "api_pkg" {
  triggers_replace = local.zip_file
  provisioner "local-exec" {
    command     = "./build-pkg.sh"
    working_dir = "../api"
    environment = {
      ZIP_FILE = local.zip_file
    }
  }
}

resource "azurerm_service_plan" "api_sp" {
  name                = "api-sp-${var.stage}"
  resource_group_name = var.rg_name
  location            = var.rg_location
  os_type             = "Linux"
  sku_name            = "F1"
  tags = {
    "stage" = var.stage
  }
}

resource "azurerm_linux_web_app" "api_webapp" {
  name                = "api-webapp-${var.stage}"
  resource_group_name = var.rg_name
  location            = var.rg_location
  service_plan_id     = azurerm_service_plan.api_sp.id
  zip_deploy_file     = local.zip_file
  app_settings        = local.app_settings
  site_config {
    always_on        = false
    app_command_line = "fastapi run api/app.py --host 0.0.0.0"
    application_stack {
      python_version = "3.12"
    }
  }
  tags = {
    "stage" = var.stage
  }
  depends_on = [
    terraform_data.api_pkg,
  ]
}
