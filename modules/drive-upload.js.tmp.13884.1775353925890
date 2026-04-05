const fs = require('fs');
const path = require('path');
const { google } = require('googleapis');

async function uploadToDrive(filePath, credentials, folderId) {
  if (!credentials) {
    console.log('Google Drive credentials not configured - skipping upload');
    return null;
  }

  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/drive.file'],
  });

  const drive = google.drive({ version: 'v3', auth });
  const fileName = path.basename(filePath);

  const fileMetadata = {
    name: fileName,
    ...(folderId && { parents: [folderId] }),
  };

  const media = {
    mimeType: 'application/pdf',
    body: fs.createReadStream(filePath),
  };

  const res = await drive.files.create({
    requestBody: fileMetadata,
    media,
    fields: 'id, webViewLink',
  });

  return {
    fileId: res.data.id,
    webViewLink: res.data.webViewLink,
  };
}

module.exports = { uploadToDrive };
