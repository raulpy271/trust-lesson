
resource "azurerm_redis_cache" "cache" {
  name                               = "cache-trust-lesson-${var.stage}"
  location                           = var.rg_location
  resource_group_name                = var.rg_name
  family                             = "C"
  capacity                           = 1
  sku_name                           = "Basic"
  non_ssl_port_enabled               = false
  minimum_tls_version                = "1.2"
  public_network_access_enabled      = true
  access_keys_authentication_enabled = true
  redis_version                      = 6

  redis_configuration {
  }
  tags = {
    "stage" = var.stage
  }
}

