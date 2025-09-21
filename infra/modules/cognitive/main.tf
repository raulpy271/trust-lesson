
resource "azurerm_cognitive_account" "vision" {
  name                          = "vision-${var.stage}"
  resource_group_name           = var.rg_name
  location                      = var.rg_location
  kind                          = "ComputerVision"
  sku_name                      = "F0"
  public_network_access_enabled = true
  tags = {
    "stage"    = var.stage
    Acceptance = "Test"
  }
}

resource "azurerm_cognitive_account" "document_intelligence" {
  name                          = "document-intelligence-${var.stage}"
  resource_group_name           = var.rg_name
  location                      = var.rg_location
  kind                          = "FormRecognizer"
  sku_name                      = "F0"
  public_network_access_enabled = true
  tags = {
    "stage"    = var.stage
    Acceptance = "Test"
  }
}
