
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

