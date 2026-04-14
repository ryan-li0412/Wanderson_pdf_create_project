const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const TEMPLATE_PATH = path.join(__dirname, '..', 'templates', 'pdf-template.html');

function buildCheckboxClasses(formData) {
  // Request type: posse vs perda
  formData.check_posse = formData.tipo_pedido === 'posse' ? 'checked' : '';
  formData.check_perda = formData.tipo_pedido === 'perda' ? 'checked' : '';

  // Art. 6 checkboxes
  const art6 = formData.art6 || 'NIE';
  formData.check_tak = art6 === 'TAK' ? 'checked' : '';
  formData.check_nie = art6 === 'NIE' ? 'checked' : '';
  formData.check_nie_wiem = art6 === 'NIE WIEM' ? 'checked' : '';
  formData.check_nie_dotyczy = art6 === 'NIE DOTYCZY' ? 'checked' : '';

  return formData;
}

function fillTemplate(formData) {
  let html = fs.readFileSync(TEMPLATE_PATH, 'utf-8');

  const data = buildCheckboxClasses(formData);

  // Replace all {{placeholder}} with form data
  html = html.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    const val = data[key];
    if (val === undefined || val === null) return '';
    // Escape HTML
    return String(val)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n/g, '<br>');
  });

  return html;
}

async function generatePDF(formData, outputPath) {
  const html = fillTemplate(formData);
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: 'networkidle0', timeout: 60000 });
  await page.evaluateHandle('document.fonts.ready');

  await page.pdf({
    path: outputPath,
    format: 'A4',
    printBackground: true,
    margin: { top: '20mm', right: '15mm', bottom: '20mm', left: '15mm' },
  });

  await browser.close();
  return outputPath;
}

module.exports = { generatePDF, fillTemplate };
