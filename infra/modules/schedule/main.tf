
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

resource "terraform_data" "api_zip" {
  provisioner "local-exec" {
    command = "./create_zip.sh"
    working_dir =  "../api"
  }
}

resource "azurerm_linux_function_app" "update_status_lesson" {
  name                = "update-status-lesson-${var.stage}"
  resource_group_name = var.rg_name
  location            = var.rg_location
  service_plan_id     = azurerm_service_plan.functions_sp.id
  storage_account_name       = var.storage_account_name
  storage_account_access_key = var.storage_access_key
  zip_deploy_file            = "../api/dist/api-0.1.0-py3-none-any.whl"
  site_config {
    always_on = false
    app_command_line = "python api/jobs/update_status_lesson.py"
    application_stack {
      python_version = "3.12"
    }
  }
  tags = {
    "stage" = var.stage
  }
  app_settings = {
    SCM_DO_BUILD_DURING_DEPLOYMENT = true
    ZIP_HASH = filemd5("../api/dist/api-0.1.0-py3-none-any.whl")
    
  }
  depends_on = [
    terraform_data.api_zip
  ]
}

