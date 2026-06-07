// Azure Architecture Reviewer - Test Resources
// Bicep template for deploying test resources

@description('Azure region for resource deployment')
param location string = 'eastus'

@description('Subscription ID')
param subscriptionId string = '1234567890'

@description('Resource group name')
param resourceGroupName string = 'rg1'

// Resource 1: Bad Storage Account
resource badStorageAccount1 'Microsoft.Storage/storageAccounts@2021-06-01' = {
    name: 'badresource1'
    location: location
    kind: 'StorageV2'
    sku: {
        name: 'Standard_LRS'
    }
    properties: {
        publicNetworkAccess: 'Enabled'
        allowBlobPublicAccess: true
        minimumTlsVersion: 'TLS1_0'
        encryption: {
            services: {
                blob: {
                    enabled: false
                }
            }
            keySource: 'Microsoft.Storage'
        }
        accessTier: 'Hot'
    }
}

// Resource 2: Bad SQL Server
resource badSqlServer1 'Microsoft.Sql/servers@2019-06-01' = {
    name: 'badresource2'
    location: location
    properties: {
        publicNetworkAccess: 'Enabled'
        administratorLogin: 'sqladmin'
        administratorLoginPassword: 'P@ssw0rd1234!' // Should use Key Vault reference
        version: '12.0'
        minimalTlsVersion: 'TLS1_0'
    }
}

// Resource 2a: Bad SQL Firewall Rule
resource sqlFirewallRule1 'Microsoft.Sql/servers/firewallRules@2014-04-01' = {
    parent: badSqlServer1
    name: 'AllowAll'
    properties: {
        startIpAddress: '0.0.0.0'
        endIpAddress: '255.255.255.255'
    }
}

// Resource 3: Bad Web App
resource badWebApp 'Microsoft.Web/sites@2021-02-01' = {
    name: 'badresource3'
    location: 'westeurope'
    kind: 'app'
    identity: {
        type: 'SystemAssigned'
    }
    properties: {
        publicNetworkAccess: 'Enabled'
        httpsOnly: false
        serverFarmId: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Web/serverfarms/asp-placeholder'
        siteConfig: {
            minTlsVersion: '1.0'
            ftpsState: 'AllAllowed'
        }
    }
}

// Resource 5: Bad Application Gateway
resource badAppGateway 'Microsoft.Network/applicationGateways@2021-05-01' = {
    name: 'badresource5'
    location: location
    properties: {
        sku: {
            name: 'Standard_v2'
            tier: 'Standard_v2'
            capacity: 2
        }
        gatewayIPConfigurations: [
            {
                name: 'appGatewayIpConfig'
                properties: {
                    subnet: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/virtualNetworks/vnet-placeholder/subnets/subnet-placeholder'
                    }
                }
            }
        ]
        frontendIPConfigurations: [
            {
                name: 'appGatewayFrontendIP'
                properties: {
                    publicIPAddress: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/publicIPAddresses/appgw-ip'
                    }
                }
            }
        ]
        frontendPorts: [
            {
                name: 'appGatewayFrontendPort'
                properties: {
                    port: 80
                }
            }
        ]
        backendAddressPools: [
            {
                name: 'appGatewayBackendPool'
            }
        ]
        backendHttpSettingsCollection: [
            {
                name: 'appGatewayBackendHttpSettings'
                properties: {
                    port: 80
                    protocol: 'Http'
                    cookieBasedAffinity: 'Disabled'
                }
            }
        ]
        httpListeners: [
            {
                name: 'appGatewayHttpListener'
                properties: {
                    frontendIPConfiguration: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/applicationGateways/badresource5/frontendIPConfigurations/appGatewayFrontendIP'
                    }
                    frontendPort: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/applicationGateways/badresource5/frontendPorts/appGatewayFrontendPort'
                    }
                    protocol: 'Http'
                }
            }
        ]
        requestRoutingRules: [
            {
                name: 'rule1'
                properties: {
                    ruleType: 'Basic'
                    httpListener: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/applicationGateways/badresource5/httpListeners/appGatewayHttpListener'
                    }
                    backendAddressPool: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/applicationGateways/badresource5/backendAddressPools/appGatewayBackendPool'
                    }
                    backendHttpSettings: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/applicationGateways/badresource5/backendHttpSettingsCollection/appGatewayBackendHttpSettings'
                    }
                }
            }
        ]
        sslPolicy: {
            minProtocolVersion: 'TLSv1_0'
        }
    }
}

// Resource 6: Good Key Vault
resource goodKeyVault 'Microsoft.KeyVault/vaults@2021-06-01-preview' = {
    name: 'goodresource1'
    location: location
    properties: {
        tenantId: subscription().tenantId
        sku: {
            family: 'A'
            name: 'standard'
        }
        accessPolicies: []
        publicNetworkAccess: 'Disabled'
        enableSoftDelete: true
        enablePurgeProtection: true
        softDeleteRetentionInDays: 90
        networkAcls: {
            bypass: 'AzureServices'
            defaultAction: 'Deny'
            ipRules: []
            virtualNetworkRules: []
        }
    }
}

// Resource 7: Good Storage Account
resource goodStorageAccount 'Microsoft.Storage/storageAccounts@2021-06-01' = {
    name: 'goodresource2'
    location: 'northeurope'
    kind: 'StorageV2'
    sku: {
        name: 'Standard_GRS'
    }
    properties: {
        publicNetworkAccess: 'Disabled'
        allowBlobPublicAccess: false
        minimumTlsVersion: 'TLS1_2'
        accessTier: 'Hot'
        encryption: {
            services: {
                blob: {
                    enabled: true
                    keyType: 'Account'
                }
                file: {
                    enabled: true
                    keyType: 'Account'
                }
            }
            keySource: 'Microsoft.Keyvault'
        }
    }
}

// Resource 8: Bad SQL Server 2
resource badSqlServer2 'Microsoft.Sql/servers@2019-06-01' = {
    name: 'badresource6'
    location: location
    properties: {
        publicNetworkAccess: 'Enabled'
        administratorLogin: 'sqladmin'
        administratorLoginPassword: 'P@ssw0rd1234!'
        version: '12.0'
        minimalTlsVersion: '1.0'
    }
}

// Resource 8a: Bad SQL Firewall Rule 2
resource sqlFirewallRule2 'Microsoft.Sql/servers/firewallRules@2014-04-01' = {
    parent: badSqlServer2
    name: 'AllowAzureIps'
    properties: {
        startIpAddress: '0.0.0.0'
        endIpAddress: '0.0.0.0'
    }
}

// Resource 9: Good Application Gateway with WAF
resource goodAppGateway 'Microsoft.Network/applicationGateways@2021-05-01' = {
    name: 'goodresource3'
    location: 'westeurope'
    properties: {
        sku: {
            name: 'WAF_v2'
            tier: 'WAF_v2'
            capacity: 2
        }
        gatewayIPConfigurations: [
            {
                name: 'appGatewayIpConfig'
                properties: {
                    subnet: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/virtualNetworks/vnet-placeholder/subnets/subnet-placeholder'
                    }
                }
            }
        ]
        frontendIPConfigurations: [
            {
                name: 'appGatewayFrontendIP'
                properties: {
                    publicIPAddress: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/publicIPAddresses/waf-pip'
                    }
                }
            }
        ]
        frontendPorts: [
            {
                name: 'appGatewayFrontendPort'
                properties: {
                    port: 443
                }
            }
        ]
        backendAddressPools: [
            {
                name: 'appGatewayBackendPool'
            }
        ]
        backendHttpSettingsCollection: [
            {
                name: 'appGatewayBackendHttpSettings'
                properties: {
                    port: 443
                    protocol: 'Https'
                    cookieBasedAffinity: 'Disabled'
                }
            }
        ]
        httpListeners: [
            {
                name: 'appGatewayHttpListener'
                properties: {
                    frontendIPConfiguration: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/applicationGateways/goodresource3/frontendIPConfigurations/appGatewayFrontendIP'
                    }
                    frontendPort: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/applicationGateways/goodresource3/frontendPorts/appGatewayFrontendPort'
                    }
                    protocol: 'Https'
                    requireServerNameIndication: true
                }
            }
        ]
        requestRoutingRules: [
            {
                name: 'rule1'
                properties: {
                    ruleType: 'Basic'
                    httpListener: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/applicationGateways/goodresource3/httpListeners/appGatewayHttpListener'
                    }
                    backendAddressPool: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/applicationGateways/goodresource3/backendAddressPools/appGatewayBackendPool'
                    }
                    backendHttpSettings: {
                        id: '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.Network/applicationGateways/goodresource3/backendHttpSettingsCollection/appGatewayBackendHttpSettings'
                    }
                }
            }
        ]
        webApplicationFirewallConfiguration: {
            enabled: true
            firewallMode: 'Prevention'
            ruleSetType: 'OWASP'
            ruleSetVersion: '3.2'
        }
        sslPolicy: {
            minProtocolVersion: 'TLSv1_2'
            policyType: 'Custom'
        }
    }
}
