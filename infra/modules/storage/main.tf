
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
  storage_account_id    = azurerm_storage_account.trust_lesson.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "lesson_spreadsheet" {
  name                  = "lesson-spreadsheet"
  storage_account_id    = azurerm_storage_account.trust_lesson.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "function_fc" {
  name                  = "function-flex-consumption"
  storage_account_id    = azurerm_storage_account.trust_lesson.id
  container_access_type = "private"
}
