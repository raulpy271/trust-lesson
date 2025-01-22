
output "hostname" {
  value = azurerm_redis_cache.cache.hostname
}

output "ssl_port" {
  value = azurerm_redis_cache.cache.ssl_port
}

output "access_key" {
  value     = azurerm_redis_cache.cache.primary_access_key
  sensitive = true
}

