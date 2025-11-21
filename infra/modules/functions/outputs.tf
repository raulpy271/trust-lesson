
output "function_url" {
  value = "https://${azurerm_function_app_flex_consumption.functions.default_hostname}"
}

output "function_key" {
  value     = data.azurerm_function_app_host_keys.functions.default_function_key
  sensitive = true
}
