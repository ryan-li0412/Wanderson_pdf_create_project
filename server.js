const express = require('express');
const path = require('path');
const fs = require('fs');
const { translateFormData } = require('./modules/deepl');
const { generatePDF } = require('./modules/pdf-generator');
const { uploadToDrive } = require('./modules/drive-upload');

const app = express();
const PORT = process.env.PORT || 3000;

// Config
const DEEPL_API_KEY = process.env.DEEPL_API_KEY || '';
const DRIVE_FOLDER_ID = process.env.DRIVE_FOLDER_ID || '';

// Google Drive credentials from env or file
let driveCredentials = null;
const credPath = path.join(__dirname, 'google-credentials.json');
if (fs.existsSync(credPath)) {
  driveCredentials = JSON.parse(fs.readFileSync(credPath, 'utf-8'));
}

// Ensure output directory
const OUTPUT_DIR = path.join(__dirname, 'output');
if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR);

// Middleware
app.use(express.json({ limit: '5mb' }));
app.use(express.static(path.join(__dirname, 'public')));
app.use('/output', express.static(OUTPUT_DIR));

// API endpoint
app.post('/api/generate-pdf', async (req, res) => {
  try {
    const formData = req.body;
    console.log('Received form submission for:', formData.pedido_nome_alvo || 'unknown');

    // Step 1: Translate fields via DeepL
    let processedData;
    if (DEEPL_API_KEY) {
      console.log('Translating fields via DeepL...');
      processedData = await translateFormData(formData, DEEPL_API_KEY);
      console.log('Translation complete');
    } else {
      console.log('No DeepL API key - using original text (no translation)');
      processedData = { ...formData };
      // Copy original values as _pl fields so template works
      const { TRANSLATABLE_FIELDS } = require('./modules/deepl');
      for (const field of TRANSLATABLE_FIELDS) {
        processedData[`${field}_pl`] = formData[field] || '';
      }
    }

    // Step 2: Generate PDF
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const clientName = (formData.pedido_nome_alvo || 'documento').replace(/[^a-zA-Z0-9_-]/g, '_');
    const fileName = `${clientName}_${timestamp}.pdf`;
    const outputPath = path.join(OUTPUT_DIR, fileName);

    console.log('Generating PDF...');
    await generatePDF(processedData, outputPath);
    console.log('PDF generated:', fileName);

    // Step 3: Upload to Google Drive (optional)
    let driveUrl = null;
    if (driveCredentials) {
      console.log('Uploading to Google Drive...');
      const driveResult = await uploadToDrive(outputPath, driveCredentials, DRIVE_FOLDER_ID);
      if (driveResult) {
        driveUrl = driveResult.webViewLink;
        console.log('Uploaded to Drive:', driveUrl);
      }
    }

    res.json({
      success: true,
      downloadUrl: `/output/${fileName}`,
      driveUrl,
      fileName,
    });
  } catch (err) {
    console.error('Error:', err);
    res.status(500).json({ success: false, error: err.message });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`\nPolonia4u server running at http://127.0.0.1:${PORT}`);
  console.log(`DeepL API: ${DEEPL_API_KEY ? 'configured' : 'NOT configured (no translation)'}`);
  console.log(`Google Drive: ${driveCredentials ? 'configured' : 'NOT configured (local only)'}`);
  console.log('');
});
