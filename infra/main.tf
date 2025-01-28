terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0.1"
    }
  }
  required_version = ">= 1.1.0"
}

provider "azurerm" {
  features {}
}

module "api" {
  source      = "./modules/api"
  stage       = var.stage
  rg_name     = azurerm_resource_group.rg.name
  rg_location = azurerm_resource_group.rg.location
  app_envs = {
    REDIS_HOST     = module.cache.hostname
    REDIS_PORT     = module.cache.ssl_port
    REDIS_PASSWORD = module.cache.access_key
    REDIS_SSL      = true
    DB_HOST        = module.database.db_domain
    DB_USER        = module.database.db_user
    DB_NAME        = module.database.db_name
    DB_PASSWORD    = module.database.db_password
  }
}

module "database" {
  source      = "./modules/database"
  stage       = var.stage
  rg_name     = azurerm_resource_group.rg.name
  rg_location = azurerm_resource_group.rg.location
}

module "cache" {
  source      = "./modules/cache"
  stage       = var.stage
  rg_name     = azurerm_resource_group.rg.name
  rg_location = azurerm_resource_group.rg.location
}

resource "azurerm_resource_group" "rg" {
  name     = "trustLessonResourceGroup-${var.stage}"
  location = var.region
}

