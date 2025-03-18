locals {
  storage_account_prefix = "talkitdoit"
}

# This Terraform block retrieves and exports the current Azure Resource Manager (ARM) client's configuration.
data "azurerm_client_config" "current" {
}

# This Terraform block generates a random lowercase, non-special, non-numeric string of seven characters.
resource "random_string" "prefix" {
  length  = 7
  special = false
  upper   = false
  numeric = false
}

# This Terraform block defines a module for creating a bastion host with a specific name and location, using either a random prefix or a user-defined one for the name.
module "bastion_host" {
  source                       = "./modules/bastion_host"
  name                         = var.name_prefix == null ? "${random_string.prefix.result}${var.bastion_host_name}" : "${var.name_prefix}${var.bastion_host_name}"
  location                     = var.location
# This block sets the parameters for a resource in Azure, namely its group name, subnet ID, and associated tags.
  resource_group_name          = azurerm_resource_group.rg.name
  subnet_id                    = module.virtual_network.subnet_ids["AzureBastionSubnet"]
  tags                         = var.tags
}
