@description('Storage account name (must be globally unique)')
param storageAccountName string

@description('Location for the storage account')
param location string = resourceGroup().location

@description('Container name for book downloads')
param containerName string = 'downloads'

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    allowBlobPublicAccess: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
}

resource container 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobServices
  name: containerName
  properties: {
    publicAccess: 'Blob'
  }
}

@description('Blob endpoint URL')
output blobEndpoint string = storageAccount.properties.primaryEndpoints.blob

@description('Download base URL')
output downloadUrl string = '${storageAccount.properties.primaryEndpoints.blob}${containerName}'