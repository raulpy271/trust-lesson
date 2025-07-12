
terraform {
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "3.6.3"
    }
  }
}

locals {
  domain        = azurerm_postgresql_flexible_server.pg.fqdn
  user_password = "${var.db_user}:${random_password.password.result}"
  db_url        = "postgresql+psycopg://${local.user_password}@${local.domain}/${var.db_name}"
  myip          = trimspace(data.http.myip.response_body)
}

resource "random_password" "password" {
  length  = 20
  special = false
}

data "http" "myip" {
  url = "https://ipv4.icanhazip.com"
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

resource "azurerm_postgresql_flexible_server_firewall_rule" "azure_ip_fw" {
  name             = "azure-ips-rule-${var.stage}"
  server_id        = azurerm_postgresql_flexible_server.pg.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "deploy_ip_fw" {
  name             = "deploy-ip-rule-${var.stage}"
  server_id        = azurerm_postgresql_flexible_server.pg.id
  start_ip_address = local.myip
  end_ip_address   = local.myip
}

resource "azurerm_postgresql_flexible_server_database" "pg_database" {
  name      = var.db_name
  server_id = azurerm_postgresql_flexible_server.pg.id
  collation = "en_US.utf8"
  charset   = "utf8"
  lifecycle {
    #prevent_destroy = true
  }
  provisioner "local-exec" {
    command     = "poetry -P api run alembic -x sqlalchemy.url=${local.db_url} upgrade head"
    working_dir = ".."
  }
  depends_on = [
    azurerm_postgresql_flexible_server_firewall_rule.deploy_ip_fw
  ]
}

