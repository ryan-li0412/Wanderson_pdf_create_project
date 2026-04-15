const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');
const os = require('os');

const INJECTOR_SCRIPT = path.join(__dirname, 'pdf-injector.py');

/**
 * Generate PDF by injecting form data into the official Polish government PDF
 * using the Python PyMuPDF coordinate-based injector.
 */
async function generatePDF(formData, outputPath) {
  // Write form data to a temp JSON file
  const tmpJson = path.join(os.tmpdir(), `pdf_form_${Date.now()}.json`);
  fs.writeFileSync(tmpJson, JSON.stringify(formData, null, 2), 'utf-8');

  return new Promise((resolve, reject) => {
    // Windows: use 'python', Linux (Railway): use venv python
    const pythonCmd = process.platform === 'win32' ? 'python' : '/app/.venv/bin/python3';

    execFile(
      pythonCmd,
      [INJECTOR_SCRIPT, tmpJson, outputPath],
      { timeout: 60000, encoding: 'utf-8' },
      (err, stdout, stderr) => {
        // Clean up temp file
        try { fs.unlinkSync(tmpJson); } catch (_) {}

        if (err) {
          console.error('[pdf-generator] Python error:', stderr || err.message);
          reject(new Error(`PDF injection failed: ${stderr || err.message}`));
          return;
        }

        if (stderr) console.log('[pdf-generator]', stderr.trim());
        resolve(outputPath);
      }
    );
  });
}

module.exports = { generatePDF };
