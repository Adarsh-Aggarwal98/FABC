# SharePoint Document Storage Setup Guide

This guide explains how to configure SharePoint as the document storage backend for the CRM. Documents will be organized in folders by client name.

## Prerequisites

- Microsoft 365 Business subscription with SharePoint
- Azure Active Directory admin access
- A SharePoint site where documents will be stored

---

## Step 1: Register an Application in Azure AD

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Fill in the details:
   - **Name**: `CRM Document Storage` (or any name you prefer)
   - **Supported account types**: Select "Accounts in this organizational directory only"
   - **Redirect URI**: Leave blank (not needed for this integration)
5. Click **Register**

After registration, note down these values from the **Overview** page:
- **Application (client) ID** → This is your `GRAPH_CLIENT_ID`
- **Directory (tenant) ID** → This is your `GRAPH_TENANT_ID`

---

## Step 2: Create a Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Under **Client secrets**, click **New client secret**
3. Add a description (e.g., "CRM Production")
4. Select an expiration period (recommend 24 months)
5. Click **Add**
6. **IMPORTANT**: Copy the secret **Value** immediately (it won't be shown again)
   - This is your `GRAPH_CLIENT_SECRET`

---

## Step 3: Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Select **Application permissions** (not Delegated)
5. Add these permissions:

| Permission | Description |
|------------|-------------|
| `Sites.ReadWrite.All` | Read and write items in all site collections |
| `Files.ReadWrite.All` | Read and write files in all site collections |

6. Click **Add permissions**
7. Click **Grant admin consent for [Your Organization]**
8. Confirm by clicking **Yes**

The status should show green checkmarks for all permissions.

---

## Step 4: Get Your SharePoint Site ID

### Option A: Using Graph Explorer (Recommended)

1. Go to [Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)
2. Sign in with your Microsoft 365 account
3. Run this query to find your site:

```
GET https://graph.microsoft.com/v1.0/sites?search=*
```

This returns all sites. Find your site and note the `id` field.

### Option B: Get Site ID by URL

If you know your SharePoint site URL (e.g., `https://yourcompany.sharepoint.com/sites/CRMDocuments`), run:

```
GET https://graph.microsoft.com/v1.0/sites/yourcompany.sharepoint.com:/sites/CRMDocuments
```

The response will include:
```json
{
  "id": "yourcompany.sharepoint.com,guid1,guid2",
  "name": "CRMDocuments",
  "webUrl": "https://yourcompany.sharepoint.com/sites/CRMDocuments"
}
```

The `id` value is your `SHAREPOINT_SITE_ID`.

### Option C: Using PowerShell

```powershell
# Install Microsoft Graph PowerShell module
Install-Module Microsoft.Graph -Scope CurrentUser

# Connect to Graph
Connect-MgGraph -Scopes "Sites.Read.All"

# Get all sites
Get-MgSite -Search "*"

# Or get specific site
Get-MgSite -SiteId "yourcompany.sharepoint.com:/sites/YourSiteName"
```

---

## Step 5: Get the Document Library Drive ID

Once you have the Site ID, get the document library (drive) ID:

### Using Graph Explorer

```
GET https://graph.microsoft.com/v1.0/sites/{site-id}/drives
```

Replace `{site-id}` with your actual Site ID.

Response example:
```json
{
  "value": [
    {
      "id": "b!xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "name": "Documents",
      "driveType": "documentLibrary",
      "webUrl": "https://yourcompany.sharepoint.com/sites/CRMDocuments/Shared Documents"
    }
  ]
}
```

The `id` of the "Documents" drive is your `SHAREPOINT_DRIVE_ID`.

**Note**: If you want to use a specific document library (not the default "Documents"), look for its name in the response.

---

## Step 6: Configure Environment Variables

Add these variables to your `.env` file:

```env
# SharePoint Document Storage
SHAREPOINT_ENABLED=true
SHAREPOINT_SITE_ID=yourcompany.sharepoint.com,guid1,guid2
SHAREPOINT_DRIVE_ID=b!xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SHAREPOINT_ROOT_FOLDER=CRM_Documents

# Microsoft Graph API (may already be configured for email)
GRAPH_CLIENT_ID=your-application-client-id
GRAPH_CLIENT_SECRET=your-client-secret-value
GRAPH_TENANT_ID=your-directory-tenant-id
```

---

## Step 7: Run Database Migration

Apply the database migration to add SharePoint columns:

```bash
# Using psql
psql -d accountant_crm -f migrations/add_sharepoint_columns.sql

# Or using Flask-Migrate
flask db upgrade
```

---

## Step 8: Test the Configuration

1. Restart your Flask application
2. Upload a test document through the CRM
3. Check your SharePoint site - you should see:
   ```
   CRM_Documents/
   └── {Client Name}/
       └── {category}/
           └── {uuid}.{ext}
   ```

---

## Folder Structure

Documents are organized by client name:

```
CRM_Documents/
├── John Smith/
│   ├── tax_document/
│   │   ├── abc123.pdf
│   │   └── def456.pdf
│   ├── id_proof/
│   │   └── ghi789.jpg
│   └── supporting_document/
│       └── jkl012.docx
├── Jane Doe/
│   └── financial_statement/
│       └── mno345.xlsx
└── Acme Corporation/
    └── invoice/
        └── pqr678.pdf
```

If a document is linked to a service request, the structure includes the request ID:
```
CRM_Documents/
└── John Smith/
    └── {service_request_id}/
        └── tax_document/
            └── abc123.pdf
```

---

## Troubleshooting

### Error: "Failed to get token"
- Verify `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`, and `GRAPH_TENANT_ID` are correct
- Ensure the client secret hasn't expired
- Check that admin consent was granted for all permissions

### Error: "Failed to create folder"
- Verify `SHAREPOINT_SITE_ID` and `SHAREPOINT_DRIVE_ID` are correct
- Ensure the app has `Sites.ReadWrite.All` permission
- Check that admin consent was granted

### Error: "Upload failed: 403"
- The app lacks permissions to write to the document library
- Ensure `Files.ReadWrite.All` permission is granted with admin consent

### Error: "Site not found"
- Double-check the Site ID format (should be like `contoso.sharepoint.com,guid,guid`)
- Ensure the site exists and is accessible

### Documents not appearing in SharePoint
- Check the `SHAREPOINT_ROOT_FOLDER` setting
- Verify the drive ID points to the correct document library
- Look in the root of the document library for the `CRM_Documents` folder

---

## Security Considerations

1. **Client Secret Rotation**: Set a reminder to rotate the client secret before it expires
2. **Principle of Least Privilege**: Only grant the minimum required permissions
3. **Audit Logging**: Enable audit logging in SharePoint to track document access
4. **Conditional Access**: Consider adding conditional access policies for the app

---

## Quick Reference: Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SHAREPOINT_ENABLED` | Enable SharePoint storage | `true` |
| `SHAREPOINT_SITE_ID` | SharePoint site identifier | `contoso.sharepoint.com,abc123,def456` |
| `SHAREPOINT_DRIVE_ID` | Document library drive ID | `b!xxxxxxxxxxxxxx` |
| `SHAREPOINT_ROOT_FOLDER` | Root folder for CRM documents | `CRM_Documents` |
| `GRAPH_CLIENT_ID` | Azure AD app client ID | `12345678-1234-...` |
| `GRAPH_CLIENT_SECRET` | Azure AD app client secret | `abc123~xxxxx` |
| `GRAPH_TENANT_ID` | Azure AD tenant ID | `87654321-4321-...` |

---

## Additional Resources

- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/overview)
- [SharePoint Sites API](https://docs.microsoft.com/en-us/graph/api/resources/site)
- [DriveItem API](https://docs.microsoft.com/en-us/graph/api/resources/driveitem)
- [Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)
- [Azure AD App Registration](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
