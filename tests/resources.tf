################################################################################
# Azure Architecture Reviewer - Test Resources
# All resources defined in a single Terraform file
################################################################################

#########################################
# Terraform Configuration
#########################################

terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
}

# Data source for current Azure context
data "azurerm_client_config" "current" {}

#########################################
# Variables
#########################################

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
  default     = "1234567890"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg1"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "sql_password" {
  description = "SQL Server administrator password"
  type        = string
  sensitive   = true
  default     = "P@ssw0rd1234!"
}

variable "service_principal_id" {
  description = "Service principal object ID"
  type        = string
  default     = "00000000-0000-0000-0000-000000000000"
}

variable "aad_admin_object_id" {
  description = "Azure AD admin object ID for SQL Server"
  type        = string
  default     = "00000000-0000-0000-0000-000000000000"
}

variable "dev_team_group_object_id" {
  description = "Development team group object ID"
  type        = string
  default     = "00000000-0000-0000-0000-000000000000"
}

#########################################
# Base Infrastructure
#########################################

# Resource Group
resource "azurerm_resource_group" "example" {
  name     = var.resource_group_name
  location = var.location
}

# App Service Plan
resource "azurerm_service_plan" "example" {
  name                = "asp-${var.resource_group_name}"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  os_type             = "Linux"
  sku_name            = "B1"
}

#########################################
# Storage Account - badresource1
#########################################

resource "azurerm_storage_account" "badresource1" {
  name                     = "badresource1"
  location                 = "eastus"
  resource_group_name      = azurerm_resource_group.example.name
  account_tier             = "Standard"
  account_replication_type = "LRS"

  public_network_access_enabled = true
  allow_nested_items_to_be_public = true
  min_tls_version = "TLS1_0"
}

#########################################
# SQL Server - badresource2
#########################################

resource "azurerm_mssql_server" "badresource2" {
  name                         = "badresource2"
  location                     = "eastus"
  resource_group_name          = azurerm_resource_group.example.name
  version                      = "12.0"
  public_network_access_enabled = true

  administrator_login          = "sqladmin"
  administrator_login_password = var.sql_password
}

resource "azurerm_mssql_firewall_rule" "badresource2_allowall" {
  name             = "AllowAll"
  server_id        = azurerm_mssql_server.badresource2.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "255.255.255.255"
}

#########################################
# App Service - badresource3
#########################################

resource "azurerm_linux_web_app" "badresource3" {
  name                = "badresource3"
  location            = "westeurope"
  resource_group_name = azurerm_resource_group.example.name
  service_plan_id     = azurerm_service_plan.example.id

  https_only = false

  site_config {
    minimum_tls_version = "1.0"
    ftps_state          = "AllAllowed"
  }

  public_network_access_enabled = true
}

#########################################
# Role Assignment - badresource4
#########################################

resource "azurerm_role_assignment" "badresource4" {
  scope                = "/subscriptions/1234567890"
  role_definition_name = "Owner"
  principal_id         = var.service_principal_id
}

#########################################
# Application Gateway - badresource5
#########################################

resource "azurerm_application_gateway" "badresource5" {
  name                = "badresource5"
  location            = "eastus"
  resource_group_name = azurerm_resource_group.example.name

  sku {
    name = "Standard_v2"
    tier = "Standard_v2"
  }

  ssl_policy {
    min_protocol_version = "TLSv1_0"
  }
}

#########################################
# Key Vault - goodresource1
#########################################

resource "azurerm_key_vault" "goodresource1" {
  name                = "goodresource1"
  location            = "eastus"
  resource_group_name = azurerm_resource_group.example.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  public_network_access_enabled = false
  soft_delete_retention_days    = 90
  purge_protection_enabled      = true

  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny"
  }
}

#########################################
# Storage Account - goodresource2
#########################################

resource "azurerm_storage_account" "goodresource2" {
  name                     = "goodresource2"
  location                 = "northeurope"
  resource_group_name      = azurerm_resource_group.example.name
  account_tier             = "Standard"
  account_replication_type = "LRS"

  public_network_access_enabled = false
  allow_nested_items_to_be_public = false
  min_tls_version = "TLS1_2"

  infrastructure_encryption_enabled = true
}

#########################################
# SQL Server - badresource6
#########################################

resource "azurerm_mssql_server" "badresource6" {
  name                         = "badresource6"
  location                     = "eastus"
  resource_group_name          = azurerm_resource_group.example.name
  version                      = "12.0"
  public_network_access_enabled = true

  azuread_administrator {
    login_username = "sqladmin@contoso.com"
    object_id      = var.aad_admin_object_id
  }
}

resource "azurerm_mssql_firewall_rule" "badresource6_azureips" {
  name             = "AllowAzureIps"
  server_id        = azurerm_mssql_server.badresource6.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

#########################################
# Application Gateway - goodresource3
#########################################

resource "azurerm_application_gateway" "goodresource3" {
  name                = "goodresource3"
  location            = "westeurope"
  resource_group_name = azurerm_resource_group.example.name

  sku {
    name = "WAF_v2"
    tier = "WAF_v2"
  }

  waf_configuration {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
  }

  ssl_policy {
    min_protocol_version = "TLSv1_2"
  }
}

#########################################
# Role Assignment - badresource7
#########################################

resource "azurerm_role_assignment" "badresource7" {
  scope                = "/subscriptions/1234567890/resourceGroups/rg1"
  role_definition_name = "Owner"
  principal_id         = var.dev_team_group_object_id
}

#########################################
# Outputs
#########################################

output "resource_group_id" {
  description = "ID of the resource group"
  value       = azurerm_resource_group.example.id
}

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.example.name
}

output "subscription_id" {
  description = "Azure subscription ID"
  value       = data.azurerm_client_config.current.subscription_id
}

output "tenant_id" {
  description = "Azure tenant ID"
  value       = data.azurerm_client_config.current.tenant_id
}