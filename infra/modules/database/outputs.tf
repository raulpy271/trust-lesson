
output "db_id" {
  value = azurerm_postgresql_flexible_server.pg.id
}

output "db_domain" {
  value = local.domain
}

output "db_user" {
  value = azurerm_postgresql_flexible_server.pg.administrator_login
}

output "db_name" {
  value = azurerm_postgresql_flexible_server_database.pg_database.name
}

output "db_password" {
  value     = azurerm_postgresql_flexible_server.pg.administrator_password
  sensitive = true
}

