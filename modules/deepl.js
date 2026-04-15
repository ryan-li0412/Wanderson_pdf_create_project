const DEEPL_API_URL = 'https://api-free.deepl.com/v2/translate';

async function translateText(text, apiKey) {
  if (!text || !text.trim()) return '';

  const res = await fetch(DEEPL_API_URL, {
    method: 'POST',
    headers: {
      'Authorization': `DeepL-Auth-Key ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: [text],
      source_lang: 'PT',
      target_lang: 'PL',
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`DeepL API error ${res.status}: ${err}`);
  }

  const data = await res.json();
  return data.translations[0].text;
}

// Fields that need DeepL translation (PT → PL)
const TRANSLATABLE_FIELDS = [
  'pedido_info_adicional',
  'objetivo_pedido',
  'hist_decisao_anterior',
  'hist_mudanca_cidadania',
  'hist_residencia',
  'bio_requerente',
  'bio_mae',
  'bio_pai',
  'bio_avo_mat',
  'bio_ava_mat',
  'bio_avo_pat',
  'bio_ava_pat',
  'bio_bisavos',
  'info_decisoes_irmaos',
  'info_docs_poloneses',
  'info_renuncia',
  'info_adicional',
];

async function translateFormData(formData, apiKey) {
  const translated = { ...formData };

  for (const field of TRANSLATABLE_FIELDS) {
    const value = formData[field];
    if (value && value.trim()) {
      translated[`${field}_pl`] = await translateText(value, apiKey);
    } else {
      translated[`${field}_pl`] = '';
    }
  }

  return translated;
}

module.exports = { translateText, translateFormData, TRANSLATABLE_FIELDS };
