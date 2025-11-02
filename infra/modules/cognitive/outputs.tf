
output "vision_endpoint" {
  value = azurerm_cognitive_account.vision.endpoint
}

output "vision_apikey" {
  value = azurerm_cognitive_account.vision.primary_access_key
}

output "document_intelligence_endpoint" {
  value = azurerm_cognitive_account.document_intelligence.endpoint
}

output "document_intelligence_apikey" {
  value = azurerm_cognitive_account.document_intelligence.primary_access_key
}
