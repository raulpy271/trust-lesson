
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
resource "azurerm_linux_function_app" "update_status_lesson" {
  name                = "update-status-lesson-${var.stage}"
  resource_group_name = var.rg_name
  location            = var.rg_location
  service_plan_id     = azurerm_service_plan.functions_sp.id
  storage_account_name       = var.storage_account_name
  storage_account_access_key = var.storage_access_key
  site_config {}
  tags = {
    "stage" = var.stage
  }
}
