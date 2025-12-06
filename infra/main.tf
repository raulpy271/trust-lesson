terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.51.0"
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
    FUNCTION_URL   = module.functions.function_url
    FUNCTION_KEY   = module.functions.function_key
  }
}

module "functions" {
  source                       = "./modules/functions"
  stage                        = var.stage
  rg_name                      = azurerm_resource_group.rg.name
  rg_location                  = azurerm_resource_group.rg.location
  storage_account_name         = module.storage.account_name
  storage_endpoint             = module.storage.endpoint
  storage_access_key           = module.storage.access_key
  insights_instrumentation_key = module.logging.insights_instrumentation_key
  app_envs = {
    DB_HOST                        = module.database.db_domain
    DB_USER                        = module.database.db_user
    DB_NAME                        = module.database.db_name
    DB_PASSWORD                    = module.database.db_password
    STORAGE_URL                    = module.storage.endpoint
    ACCOUNT_NAME                   = module.storage.account_name
    VISION_ENDPOINT                = module.cognitive.vision_endpoint
    VISION_APIKEY                  = module.cognitive.vision_apikey
    DOCUMENT_INTELLIGENCE_ENDPOINT = module.cognitive.document_intelligence_endpoint
    DOCUMENT_INTELLIGENCE_APIKEY   = module.cognitive.document_intelligence_apikey

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

module "cognitive" {
  source      = "./modules/cognitive"
  stage       = var.stage
  rg_name     = azurerm_resource_group.rg.name
  rg_location = azurerm_resource_group.rg.location
}

resource "azurerm_resource_group" "rg" {
  name     = "trustLessonResourceGroup-${var.stage}"
  location = var.region
}

