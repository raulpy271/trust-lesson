
resource "azurerm_storage_account" "trust_lesson" {
  name                     = "${var.storage_account_prefix}${var.stage}"
  resource_group_name      = var.rg_name
  location                 = var.rg_location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    "stage" = var.stage
  }
}

resource "azurerm_storage_container" "lesson_image" {
  name                  = "lesson-image"
  storage_account_name  = azurerm_storage_account.trust_lesson.name
  container_access_type = "private"
}

