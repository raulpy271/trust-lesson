
resource "azurerm_monitor_action_group" "smart_detector" {
  name                = "Application Insights Smart Detection"
  short_name          = "SmartDetect"
  resource_group_name = var.rg_name
}

resource "azurerm_log_analytics_workspace" "workspace" {
  name                = "workspace-${var.stage}"
  location            = var.rg_location
  resource_group_name = var.rg_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_application_insights" "application_insights" {
  name                = "function-application-insights-${var.stage}"
  resource_group_name = var.rg_name
  location            = var.rg_location
  application_type    = "other"
  workspace_id        = azurerm_log_analytics_workspace.workspace.id

  depends_on = [azurerm_monitor_action_group.smart_detector]
}
