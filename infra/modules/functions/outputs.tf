
output "vision_endpoint" {
  value = azurerm_cognitive_account.vision.endpoint
}

output "vision_access_key" {
  value = azurerm_cognitive_account.vision.primary_access_key
}

output "function_url" {
  value = "https://${azurerm_linux_function_app.functions.default_hostname}"
}

output "function_key" {
  value     = data.azurerm_function_app_host_keys.functions.default_function_key
  sensitive = true
}
