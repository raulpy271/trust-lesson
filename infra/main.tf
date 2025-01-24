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

module "api" {
  source      = "./modules/api"
  stage       = var.stage
  rg_name     = azurerm_resource_group.rg.name
  rg_location = azurerm_resource_group.rg.location
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

