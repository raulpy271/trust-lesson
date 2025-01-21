terraform {
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "3.6.3"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0.1"
    }
  }

  required_version = ">= 1.1.0"
}

provider "random" {
}

provider "azurerm" {
  features {}
}


resource "azurerm_resource_group" "rg" {
  name     = "trustLessonResourceGroup-${var.stage}"
  location = var.region
}

resource "random_password" "password" {
  length  = 16
  special = true
}

resource "azurerm_postgresql_flexible_server" "pg" {
  name                          = "api-postgresql-${var.stage}"
  resource_group_name           = azurerm_resource_group.rg.name
  location                      = azurerm_resource_group.rg.location
  version                       = "16"
  public_network_access_enabled = true
  administrator_login           = var.db_user
  administrator_password        = random_password.password.result
  storage_mb                    = 32768
  sku_name                      = "B_Standard_B1ms"
  tags = {
    "stage" = var.stage
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

