
output "account_name" {
  value = azurerm_storage_account.trust_lesson.name
}

output "access_key" {
  value = azurerm_storage_account.trust_lesson.primary_access_key
  sensitive = true
}

output "endpoint" {
  value = azurerm_storage_account.trust_lesson.primary_blob_endpoint
}

