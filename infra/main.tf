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
    STORAGE_URL    = module.storage.endpoint
  }
}

module "schedule" {
  source               = "./modules/schedule"
  stage                = var.stage
  rg_name              = azurerm_resource_group.rg.name
  rg_location          = azurerm_resource_group.rg.location
  storage_account_name = module.storage.account_name
  storage_access_key   = module.storage.access_key
  app_envs = {
    DB_HOST         = module.database.db_domain
    DB_USER         = module.database.db_user
    DB_NAME         = module.database.db_name
    DB_PASSWORD     = module.database.db_password
    VISION_APIKEY   = module.schedule.vision_access_key
    VISION_ENDPOINT = module.schedule.vision_endpoint
    STORAGE_URL     = module.storage.endpoint
    ACCOUNT_NAME    = module.storage.account_name

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

module "storage" {
  source      = "./modules/storage"
  stage       = var.stage
  rg_name     = azurerm_resource_group.rg.name
  rg_location = azurerm_resource_group.rg.location
}

resource "azurerm_resource_group" "rg" {
  name     = "trustLessonResourceGroup-${var.stage}"
  location = var.region
}

