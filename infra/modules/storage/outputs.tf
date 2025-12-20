
output "account_name" {
  value = azurerm_storage_account.trust_lesson.name
}

output "access_key" {
  value     = azurerm_storage_account.trust_lesson.primary_access_key
  sensitive = true
}

output "endpoint" {
  value = azurerm_storage_account.trust_lesson.primary_blob_endpoint
}

output "storage_account_id" {
  value = azurerm_storage_account.trust_lesson.id
}

output "storage_lesson_image_id" {
  value = azurerm_storage_container.lesson_image.id
}

output "storage_lesson_spreadsheet_id" {
  value = azurerm_storage_container.lesson_spreadsheet.id
}
