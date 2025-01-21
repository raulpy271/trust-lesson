
output "resource_group_id" {
  value = azurerm_resource_group.rg.id
}

output "db_id" {
  value = azurerm_postgresql_flexible_server.pg.id
}

output "db_domain" {
  value = azurerm_postgresql_flexible_server.pg.fqdn
}

output "db_user" {
  value = azurerm_postgresql_flexible_server.pg.administrator_login
}

output "db_password" {
  value     = azurerm_postgresql_flexible_server.pg.administrator_password
  sensitive = true
}

