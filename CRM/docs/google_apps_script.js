/**
 * Google Apps Script - CRM Document Storage
 * ==========================================
 *
 * SETUP INSTRUCTIONS:
 * 1. Go to https://script.google.com/
 * 2. Create a new project
 * 3. Copy this entire code into Code.gs
 * 4. Click Deploy > New deployment
 * 5. Select "Web app"
 * 6. Set "Execute as" = "Me"
 * 7. Set "Who has access" = "Anyone"
 * 8. Click Deploy and copy the Web App URL
 * 9. Add the URL to your .env: GOOGLE_APPS_SCRIPT_URL=<your-url>
 *
 * OPTIONAL: Set a root folder ID in the code below (ROOT_FOLDER_ID)
 */

// Configuration - Set your root folder ID here (optional)
const ROOT_FOLDER_ID = ''; // Leave empty to use root of My Drive

/**
 * Handle POST requests from the CRM backend
 */
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const action = data.action;

    switch (action) {
      case 'upload':
        return handleUpload(data);
      case 'getDownloadUrl':
        return handleGetDownloadUrl(data);
      case 'delete':
        return handleDelete(data);
      case 'listFiles':
        return handleListFiles(data);
      case 'test':
        return handleTest();
      default:
        return jsonResponse({ success: false, error: 'Unknown action: ' + action });
    }
  } catch (error) {
    return jsonResponse({ success: false, error: error.toString() });
  }
}

/**
 * Handle GET requests (for testing)
 */
function doGet(e) {
  return handleTest();
}

/**
 * Upload a file to Google Drive
 */
function handleUpload(data) {
  try {
    const filename = data.filename;
    const contentBase64 = data.content;
    const folderPath = data.folderPath || '';
    const rootFolderId = data.rootFolderId || ROOT_FOLDER_ID;
    const metadata = data.metadata || {};

    // Decode base64 content
    const decodedContent = Utilities.base64Decode(contentBase64);
    const blob = Utilities.newBlob(decodedContent, getMimeType(filename), filename);

    // Get or create the target folder
    let targetFolder;
    if (rootFolderId) {
      targetFolder = DriveApp.getFolderById(rootFolderId);
    } else {
      targetFolder = DriveApp.getRootFolder();
    }

    // Navigate/create folder path
    if (folderPath) {
      const pathParts = folderPath.split('/').filter(p => p.trim());
      for (const part of pathParts) {
        targetFolder = getOrCreateFolder(targetFolder, part);
      }
    }

    // Create the file
    const file = targetFolder.createFile(blob);

    // Set description with metadata
    if (metadata.service_request_id) {
      file.setDescription(JSON.stringify(metadata));
    }

    return jsonResponse({
      success: true,
      fileId: file.getId(),
      fileName: file.getName(),
      webViewLink: file.getUrl(),
      webContentLink: 'https://drive.google.com/uc?export=download&id=' + file.getId(),
      size: file.getSize(),
      mimeType: file.getMimeType(),
      folderId: targetFolder.getId(),
      folderName: targetFolder.getName()
    });

  } catch (error) {
    return jsonResponse({ success: false, error: error.toString() });
  }
}

/**
 * Get download URL for a file
 */
function handleGetDownloadUrl(data) {
  try {
    const fileId = data.fileId;
    const file = DriveApp.getFileById(fileId);

    return jsonResponse({
      success: true,
      fileId: file.getId(),
      fileName: file.getName(),
      webViewLink: file.getUrl(),
      downloadUrl: 'https://drive.google.com/uc?export=download&id=' + file.getId(),
      mimeType: file.getMimeType(),
      size: file.getSize()
    });

  } catch (error) {
    return jsonResponse({ success: false, error: error.toString() });
  }
}

/**
 * Delete a file
 */
function handleDelete(data) {
  try {
    const fileId = data.fileId;
    const file = DriveApp.getFileById(fileId);
    file.setTrashed(true);

    return jsonResponse({ success: true });

  } catch (error) {
    return jsonResponse({ success: false, error: error.toString() });
  }
}

/**
 * List files in a folder
 */
function handleListFiles(data) {
  try {
    const folderId = data.folderId || ROOT_FOLDER_ID;
    const pageSize = data.pageSize || 100;

    let folder;
    if (folderId) {
      folder = DriveApp.getFolderById(folderId);
    } else {
      folder = DriveApp.getRootFolder();
    }

    const files = [];
    const fileIterator = folder.getFiles();
    let count = 0;

    while (fileIterator.hasNext() && count < pageSize) {
      const file = fileIterator.next();
      files.push({
        id: file.getId(),
        name: file.getName(),
        mimeType: file.getMimeType(),
        size: file.getSize(),
        createdTime: file.getDateCreated().toISOString(),
        modifiedTime: file.getLastUpdated().toISOString(),
        webViewLink: file.getUrl()
      });
      count++;
    }

    return jsonResponse({ success: true, files: files });

  } catch (error) {
    return jsonResponse({ success: false, error: error.toString(), files: [] });
  }
}

/**
 * Test connection
 */
function handleTest() {
  try {
    const email = Session.getActiveUser().getEmail();
    const quota = DriveApp.getStorageUsed();
    const limit = DriveApp.getStorageLimit();

    return jsonResponse({
      success: true,
      message: 'Google Apps Script is working!',
      email: email,
      storageUsed: quota,
      storageLimit: limit,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    return jsonResponse({
      success: true,
      message: 'Google Apps Script is working!',
      timestamp: new Date().toISOString()
    });
  }
}

/**
 * Get or create a folder within a parent folder
 */
function getOrCreateFolder(parentFolder, folderName) {
  const folders = parentFolder.getFoldersByName(folderName);
  if (folders.hasNext()) {
    return folders.next();
  }
  return parentFolder.createFolder(folderName);
}

/**
 * Get MIME type from filename
 */
function getMimeType(filename) {
  const extension = filename.split('.').pop().toLowerCase();
  const mimeTypes = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'csv': 'text/csv',
    'txt': 'text/plain',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'zip': 'application/zip'
  };
  return mimeTypes[extension] || 'application/octet-stream';
}

/**
 * Create JSON response
 */
function jsonResponse(data) {
  return ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
