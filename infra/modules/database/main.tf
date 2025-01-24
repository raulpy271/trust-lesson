
resource "random_password" "password" {
  length  = 16
  special = true
}

resource "azurerm_postgresql_flexible_server" "pg" {
  name                          = "api-postgresql-${var.stage}"
  resource_group_name           = var.rg_name
  location                      = var.rg_location
  version                       = "16"
  public_network_access_enabled = true
  administrator_login           = var.db_user
  administrator_password        = random_password.password.result
  storage_mb                    = 32768
  sku_name                      = "B_Standard_B1ms"
  tags = {
    "stage" = var.stage
  }
  lifecycle {
    ignore_changes = [
      zone,
    ]
  }
}

resource "azurerm_postgresql_flexible_server_database" "pg_database" {
  name      = var.db_name
  server_id = azurerm_postgresql_flexible_server.pg.id
  collation = "en_US.utf8"
  charset   = "utf8"
  lifecycle {
    #prevent_destroy = true
  }
}

