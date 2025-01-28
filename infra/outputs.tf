
output "resource_group_id" {
  value = azurerm_resource_group.rg.id
}

output "db_domain" {
  value = module.database.db_domain
}

output "db_user" {
  value = module.database.db_user
}

output "db_password" {
  value     = module.database.db_password
  sensitive = true
}

output "cache_hostname" {
  value = module.cache.hostname
}

output "cache_ssl_port" {
  value = module.cache.ssl_port
}

output "cache_access_key" {
  value     = module.cache.access_key
  sensitive = true
}

output "api_hostname" {
  value = module.api.hostname
}

