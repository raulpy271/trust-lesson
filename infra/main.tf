terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.18.0"
    }
  }
  required_version = ">= 1.1.0"
}

provider "azurerm" {
  features {}
}

module "api" {
  source                       = "./modules/api"
  stage                        = var.stage
  rg_name                      = azurerm_resource_group.rg.name
  rg_location                  = azurerm_resource_group.rg.location
  insights_instrumentation_key = module.logging.insights_instrumentation_key
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
    FUNCTION_URL   = module.schedule.function_url
    FUNCTION_KEY   = module.schedule.function_key
  }
}

module "schedule" {
  source                       = "./modules/schedule"
  stage                        = var.stage
  rg_name                      = azurerm_resource_group.rg.name
  rg_location                  = azurerm_resource_group.rg.location
  storage_account_name         = module.storage.account_name
  storage_access_key           = module.storage.access_key
  insights_instrumentation_key = module.logging.insights_instrumentation_key
  app_envs = {
    DB_HOST      = module.database.db_domain
    DB_USER      = module.database.db_user
    DB_NAME      = module.database.db_name
    DB_PASSWORD  = module.database.db_password
    STORAGE_URL  = module.storage.endpoint
    ACCOUNT_NAME = module.storage.account_name

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

module "logging" {
  source      = "./modules/logging"
  stage       = var.stage
  rg_name     = azurerm_resource_group.rg.name
  rg_location = azurerm_resource_group.rg.location
}

resource "azurerm_resource_group" "rg" {
  name     = "trustLessonResourceGroup-${var.stage}"
  location = var.region
}

