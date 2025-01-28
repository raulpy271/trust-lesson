
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
  }
}

provider "docker" {
  registry_auth {
    address  = azurerm_container_registry.acr.login_server
    username = azurerm_container_registry.acr.admin_username
    password = azurerm_container_registry.acr.admin_password
  }
}

locals {
  local_app_settings = {
    # This environment is not actually used in the application. It is setted to force the app service to be deployed when there's a change in the image
    APP_IMAGE_ID = docker_image.api_img.id
  }
  app_settings = merge(local.local_app_settings, var.app_envs)
  image_name = "trust-lesson/api-img-${var.stage}"
  image_fullname = "${azurerm_container_registry.acr.login_server}/${local.image_name}"
}

resource "azurerm_container_registry" "acr" {
  name                = "trustLessonRegistry"
  resource_group_name = var.rg_name
  location            = var.rg_location
  sku                 = "Basic"
  admin_enabled       = true
  tags = {
    "stage" = var.stage
  }
}

resource "docker_image" "api_img" {
  name = local.image_name
  force_remove = true
  build {
    context    = "../api/"
    dockerfile = "Dockerfile-infra"
    tag = [local.image_fullname]
  }
  triggers = {
    # Always build the image locally. TODO: Build only when the code changes
    "random_uuid": uuid()
  }
}

resource "docker_registry_image" "api_img_registry" {
  name = local.image_fullname
  triggers = {
    "image_id" = docker_image.api_img.image_id
  }
}

resource "azurerm_service_plan" "api_sp" {
  name                = "api-sp-${var.stage}"
  resource_group_name = var.rg_name
  location            = var.rg_location
  os_type             = "Linux"
  sku_name            = "F1"
  tags = {
    "stage" = var.stage
  }
}

resource "azurerm_linux_web_app" "api_webapp" {
  name                = "api-webapp-${var.stage}"
  resource_group_name = var.rg_name
  location            = var.rg_location
  service_plan_id     = azurerm_service_plan.api_sp.id
  app_settings        = local.app_settings
  https_only = true
  site_config {
    always_on = false
    application_stack {
      docker_image_name        = docker_image.api_img.name
      docker_registry_url      = "https://${azurerm_container_registry.acr.login_server}"
      docker_registry_username = azurerm_container_registry.acr.admin_username
      docker_registry_password = azurerm_container_registry.acr.admin_password
    }
  }
  tags = {
    "stage" = var.stage
  }
  depends_on = [
    docker_registry_image.api_img_registry
  ]
}
