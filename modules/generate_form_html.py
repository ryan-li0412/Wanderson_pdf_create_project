#!/usr/bin/env python3
"""
generate_form_html.py
Generates public/form_viewer.html — the PDF form rendered as PNG pages
with absolutely-positioned HTML inputs. Uppercase enforced via CSS.
"""
from pathlib import Path

SCALE = 150 / 72  # PDF pt → pixel (150 DPI)
BOX_H = 8.0
NARR_LINE_H = 13.0
NARR_X1 = 525.0
PAGE_W_PX = round(595 * SCALE)   # 1240
PAGE_H_PX = round(842 * SCALE)   # 1753

FIELD_MAP = {
    'wnioskodawca_nome': [
        {'page': 0, 'y': 345, 'x0': 152.37, 'n': 20, 'sp': 17.27},
        {'page': 0, 'y': 361, 'x0': 152.37, 'n': 20, 'sp': 17.27},
    ],
    'endereco_pais':   [{'page': 0, 'y': 409, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'endereco_cidade': [{'page': 0, 'y': 425, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'endereco_rua':    [{'page': 0, 'y': 441, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'endereco_casa':   [{'page': 0, 'y': 456, 'x0': 152.89, 'n': 7,  'sp': 17.27}],
    'endereco_apto':   [{'page': 0, 'y': 456, 'x0': 376.83, 'n': 6, 'sp': 17.27}],
    'endereco_cep':    [{'page': 0, 'y': 474, 'x0': 152.37, 'n': 8,  'sp': 17.27}],
    'endereco_tel':    [{'page': 0, 'y': 489, 'x0': 152.37, 'n': 20, 'sp': 17.27}],

    'req_sobrenome':          [{'page': 1, 'y': 312, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'req_sobrenome_solteiro': [
        {'page': 1, 'y': 329, 'x0': 152.37, 'n': 20, 'sp': 17.27},
        {'page': 1, 'y': 345, 'x0': 152.37, 'n': 20, 'sp': 17.27},
    ],
    'req_nomes':        [{'page': 1, 'y': 361, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'req_pai':          [{'page': 1, 'y': 377, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'req_mae':          [
        {'page': 1, 'y': 393, 'x0': 152.37, 'n': 20, 'sp': 17.27},
        {'page': 1, 'y': 417, 'x0': 152.37, 'n': 20, 'sp': 17.27},
    ],
    'req_sobrenomes_usados': [{'page': 1, 'y': 433, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'req_nasc_ano': [{'page': 1, 'y': 448, 'x0': 152.89,               'n': 4, 'sp': 22.03}],
    'req_nasc_mes': [{'page': 1, 'y': 448, 'x0': 152.89 + 5*22.03,    'n': 2, 'sp': 22.03}],
    'req_nasc_dia': [{'page': 1, 'y': 448, 'x0': 152.89 + 8*22.03,    'n': 2, 'sp': 22.03}],
    'req_sexo':         [{'page': 1, 'y': 473, 'x0': 152.37, 'n': 1,  'sp': 17.27}],
    'req_local_nasc':   [{'page': 1, 'y': 497, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'req_cidadanias':   [
        {'page': 1, 'y': 513, 'x0': 152.37, 'n': 20, 'sp': 17.27},
        {'page': 1, 'y': 529, 'x0': 152.37, 'n': 20, 'sp': 17.27},
    ],
    'req_estado_civil': [{'page': 1, 'y': 545, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'req_pesel':        [{'page': 1, 'y': 561, 'x0': 152.89, 'n': 11, 'sp': 17.26}],

    'mae_sobrenome':         [{'page': 2, 'y': 337, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_sobrenome_solteira':[{'page': 2, 'y': 353, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_nomes':             [{'page': 2, 'y': 369, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_pai':               [{'page': 2, 'y': 385, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_mae':               [{'page': 2, 'y': 401, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_sobrenomes_usados': [{'page': 2, 'y': 417, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_nasc_ano': [{'page': 2, 'y': 472, 'x0': 152.89,               'n': 4, 'sp': 17.27}],
    'mae_nasc_mes': [{'page': 2, 'y': 472, 'x0': 152.89 + 5*17.27,    'n': 2, 'sp': 17.27}],
    'mae_nasc_dia': [{'page': 2, 'y': 472, 'x0': 152.89 + 8*17.27,    'n': 2, 'sp': 17.27}],
    'mae_local_nasc':  [{'page': 2, 'y': 497, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_estado_civil':[{'page': 2, 'y': 521, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_cas_ano': [{'page': 2, 'y': 536, 'x0': 152.89,               'n': 4, 'sp': 17.27}],
    'mae_cas_mes': [{'page': 2, 'y': 536, 'x0': 152.89 + 5*17.27,    'n': 2, 'sp': 17.27}],
    'mae_cas_dia': [{'page': 2, 'y': 536, 'x0': 152.89 + 8*17.27,    'n': 2, 'sp': 17.27}],
    'mae_local_cas': [
        {'page': 2, 'y': 561, 'x0': 152.37, 'n': 20, 'sp': 17.27},
        {'page': 2, 'y': 593, 'x0': 152.37, 'n': 20, 'sp': 17.27},
    ],
    'mae_cidadanias': [{'page': 2, 'y': 613, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_pesel':      [{'page': 2, 'y': 636, 'x0': 152.89, 'n': 11, 'sp': 17.26}],
    'pai_sobrenome':         [{'page': 2, 'y': 683, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'pai_sobrenome_solteiro':[{'page': 2, 'y': 699, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'pai_nomes':             [{'page': 2, 'y': 715, 'x0': 152.37, 'n': 20, 'sp': 17.27}],

    'pai_pai':              [{'page': 3, 'y': 108, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'pai_mae':              [{'page': 3, 'y': 124, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'pai_sobrenomes_usados':[{'page': 3, 'y': 140, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'pai_nasc_ano': [{'page': 3, 'y': 195, 'x0': 153.60,               'n': 4, 'sp': 17.27}],
    'pai_nasc_mes': [{'page': 3, 'y': 195, 'x0': 153.60 + 5*17.27,    'n': 2, 'sp': 17.27}],
    'pai_nasc_dia': [{'page': 3, 'y': 195, 'x0': 153.60 + 8*17.27,    'n': 2, 'sp': 17.27}],
    'pai_local_nasc':  [{'page': 3, 'y': 220, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'pai_pesel':       [{'page': 3, 'y': 244, 'x0': 153.60, 'n': 11, 'sp': 17.26}],
    'pai_cas_ano': [{'page': 3, 'y': 259, 'x0': 153.60,               'n': 4, 'sp': 17.27}],
    'pai_cas_mes': [{'page': 3, 'y': 259, 'x0': 153.60 + 5*17.27,    'n': 2, 'sp': 17.27}],
    'pai_cas_dia': [{'page': 3, 'y': 259, 'x0': 153.60 + 8*17.27,    'n': 2, 'sp': 17.27}],
    'pai_estado_civil':[{'page': 3, 'y': 284, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'pai_local_cas':   [{'page': 3, 'y': 316, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'pai_cidadanias':  [{'page': 3, 'y': 335, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_mat_sobrenome':         [{'page': 3, 'y': 434, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_mat_sobrenome_solteiro':[{'page': 3, 'y': 450, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_mat_nomes':             [{'page': 3, 'y': 466, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_mat_pai':               [{'page': 3, 'y': 482, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_mat_mae':               [{'page': 3, 'y': 498, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_mat_nasc_ano': [{'page': 3, 'y': 537, 'x0': 153.60,               'n': 4, 'sp': 17.27}],
    'avo_mat_nasc_mes': [{'page': 3, 'y': 537, 'x0': 153.60 + 5*17.27,    'n': 2, 'sp': 17.27}],
    'avo_mat_nasc_dia': [{'page': 3, 'y': 537, 'x0': 153.60 + 8*17.27,    'n': 2, 'sp': 17.27}],
    'avo_mat_local_nasc':[{'page': 3, 'y': 562, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_mat_pesel':     [{'page': 3, 'y': 586, 'x0': 153.60, 'n': 11, 'sp': 17.26}],
    'ava_mat_sobrenome':         [{'page': 3, 'y': 648, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_mat_sobrenome_solteira':[{'page': 3, 'y': 664, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_mat_nomes':             [{'page': 3, 'y': 680, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_mat_pai':               [{'page': 3, 'y': 696, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_mat_mae':               [{'page': 3, 'y': 712, 'x0': 153.07, 'n': 20, 'sp': 17.27}],

    'avo_pat_sobrenome':         [{'page': 4, 'y': 108, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_pat_sobrenome_solteiro':[{'page': 4, 'y': 131, 'x0': 153.60, 'n': 10, 'sp': 17.27}],
    'avo_pat_nomes':             [{'page': 4, 'y': 156, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_pat_nasc_ano': [{'page': 4, 'y': 180, 'x0': 153.60,               'n': 4, 'sp': 17.26}],
    'avo_pat_nasc_mes': [{'page': 4, 'y': 180, 'x0': 153.60 + 5*17.26,    'n': 2, 'sp': 17.26}],
    'avo_pat_nasc_dia': [{'page': 4, 'y': 180, 'x0': 153.60 + 8*17.26,    'n': 2, 'sp': 17.26}],
    'avo_pat_pai':      [{'page': 4, 'y': 231, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_pat_mae':      [{'page': 4, 'y': 247, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_pat_local_nasc':[{'page': 4, 'y': 360, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_pat_cas_ano':  [{'page': 4, 'y': 335, 'x0': 153.60,               'n': 4, 'sp': 17.27}],
    'avo_pat_cas_mes':  [{'page': 4, 'y': 335, 'x0': 153.60 + 5*17.27,    'n': 2, 'sp': 17.27}],
    'avo_pat_cas_dia':  [{'page': 4, 'y': 335, 'x0': 153.60 + 8*17.27,    'n': 2, 'sp': 17.27}],
    'avo_pat_pesel':    [{'page': 4, 'y': 384, 'x0': 153.60, 'n': 11, 'sp': 17.26}],
    'ava_pat_sobrenome':         [{'page': 4, 'y': 435, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_pat_sobrenome_solteira':[{'page': 4, 'y': 451, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_pat_nomes':             [{'page': 4, 'y': 467, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_pat_pai':               [{'page': 4, 'y': 483, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_pat_mae':               [{'page': 4, 'y': 499, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_pat_nasc_ano': [{'page': 4, 'y': 538, 'x0': 153.60,               'n': 4, 'sp': 17.27}],
    'ava_pat_nasc_mes': [{'page': 4, 'y': 538, 'x0': 153.60 + 5*17.27,    'n': 2, 'sp': 17.27}],
    'ava_pat_nasc_dia': [{'page': 4, 'y': 538, 'x0': 153.60 + 8*17.27,    'n': 2, 'sp': 17.27}],
    'ava_pat_local_nasc':[{'page': 4, 'y': 563, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_pat_pesel':     [{'page': 4, 'y': 587, 'x0': 153.60, 'n': 11, 'sp': 17.26}],
}

NARRATIVE_MAP = {
    'bio_requerente': {'page': 5,  'lines': [182,422], 'x0': 70.7},
    'bio_mae':        {'page': 6,  'lines': [179,347], 'x0': 70.0},
    'bio_pai':        {'page': 6,  'lines': [417,585], 'x0': 70.0},
    'bio_avo_mat_1':  {'page': 6,  'lines': [675,711], 'x0': 70.0},
    'bio_avo_mat_2':  {'page': 7,  'lines': [100,220], 'x0': 70.0},
    'bio_ava_mat':    {'page': 7,  'lines': [288,456], 'x0': 70.0},
    'bio_avo_pat':    {'page': 7,  'lines': [536,704], 'x0': 70.0},
    'bio_ava_pat':    {'page': 8,  'lines': [156,324], 'x0': 70.7},
    'bio_bisavos':    {'page': 8,  'lines': [426,618], 'x0': 70.7},
    'info_decisoes_irmaos': {'page': 9, 'lines': [127,175], 'x0': 69.3},
    'info_docs_poloneses':  {'page': 9, 'lines': [236,284], 'x0': 69.3},
    'info_renuncia':        {'page': 9, 'lines': [368,416], 'x0': 69.3},
    'info_adicional':       {'page': 9, 'lines': [473,701], 'x0': 69.3},
    'anexos_lista':         {'page': 10,'lines': [102,210], 'x0': 70.0},
}

def pt(v):
    return round(v * SCALE, 2)


def build_inputs_for_page(page_idx):
    inputs = []

    # Letter-box fields — visible input ABOVE the boxes, spans IN the boxes
    for field_name, rows in FIELD_MAP.items():
        page_rows = [r for r in rows if r['page'] == page_idx]
        if not page_rows:
            continue

        total_chars = sum(r['n'] for r in page_rows)
        first_row = page_rows[0]
        last_row  = page_rows[-1]

        # Input overlaid directly on the box area (covers all rows)
        ix = pt(first_row['x0'])
        iw = pt(first_row['n'] * first_row['sp'])
        iy = pt(first_row['y'])
        ih = pt(last_row['y']) + pt(BOX_H) - iy  # full height of all rows
        inputs.append(
            f'<input type="text" maxlength="{total_chars}" '
            f'data-field="{field_name}" '
            f'style="left:{ix}px;top:{iy}px;width:{iw}px;height:{ih}px;" '
            f'class="row-input" autocomplete="off">'
        )

        # One <span> per character cell inside each box
        char_idx = 0
        for row in page_rows:
            ch_w = pt(row['sp'])
            ch_h = pt(BOX_H)
            cy   = pt(row['y'])
            for col in range(row['n']):
                cx = pt(row['x0'] + col * row['sp'])
                inputs.append(
                    f'<span data-field="{field_name}" data-idx="{char_idx}" '
                    f'style="left:{cx}px;top:{cy}px;width:{ch_w}px;height:{ch_h}px;" '
                    f'class="char-cell"></span>'
                )
                char_idx += 1

    # Narrative fields
    for field_name, spec in NARRATIVE_MAP.items():
        if spec['page'] != page_idx:
            continue
        y0 = pt(spec['lines'][0] - 3)
        y1 = pt(spec['lines'][1] + NARR_LINE_H)
        x  = pt(spec['x0'])
        w  = pt(NARR_X1 - spec['x0'])
        h  = y1 - y0
        inputs.append(
            f'<textarea name="{field_name}" '
            f'style="left:{x}px;top:{y0}px;width:{w}px;height:{h}px;" '
            f'class="narr-field"></textarea>'
        )

    return '\n'.join(inputs)


def generate():
    pages_html = ''
    for i in range(11):
        inputs = build_inputs_for_page(i)
        pages_html += f'''
  <div class="page-wrap">
    <div class="page" style="width:{PAGE_W_PX}px;height:{PAGE_H_PX}px;">
      <img src="form_pages/page_{i+1}.png" width="{PAGE_W_PX}" height="{PAGE_H_PX}">
      {inputs}
    </div>
  </div>'''

    html = f'''<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Formulário de Cidadania Polonesa</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #888; font-family: Arial, sans-serif; }}
  .page-wrap {{ display: flex; justify-content: center; margin: 16px 0; }}
  .page {{
    position: relative;
    box-shadow: 0 2px 12px rgba(0,0,0,0.4);
    background: #fff;
    overflow: hidden;
  }}
  .page img {{ display: block; }}
  .row-input {{
    position: absolute;
    background: rgba(255, 255, 180, 0.5);
    border: none;
    outline: none;
    color: transparent;
    caret-color: transparent;
    z-index: 10;
    cursor: text;
    font-size: 11px;
    padding: 0 3px;
    text-transform: uppercase;
    transition: background 0.1s, border 0.1s, color 0.1s;
  }}
  .row-input:focus {{
    background: #fff;
    border: 1px solid #c00;
    color: #000;
    caret-color: #000;
    box-shadow: 0 0 0 1px #c00;
  }}
  .char-cell {{
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: Arial, sans-serif;
    font-size: 9px;
    color: #000;
    text-transform: uppercase;
    pointer-events: none;
    z-index: 5;
  }}
  .narr-field {{
    position: absolute;
    background: transparent;
    border: none;
    outline: none;
    padding: 0 2px;
    text-transform: uppercase;
    font-family: Arial, sans-serif;
    font-size: 9px;
    line-height: 12px;
    color: #000;
    resize: none;
    z-index: 10;
  }}
  .submit-bar {{
    display: flex;
    justify-content: center;
    padding: 24px;
  }}
  .submit-btn {{
    background: #1a5fb4;
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 14px 48px;
    font-size: 16px;
    cursor: pointer;
    font-weight: bold;
  }}
  .submit-btn:hover {{ background: #1345a0; }}
</style>
</head>
<body>
<form method="POST" action="/generate-pdf" id="mainForm">
{pages_html}
  <div class="submit-bar">
    <button type="submit" class="submit-btn">Gerar PDF</button>
  </div>
</form>
<script>
  // Uppercase while typing, distribute to boxes on blur
  document.querySelectorAll('.row-input').forEach(inp => {{
    inp.addEventListener('input', function() {{
      this.value = this.value.toUpperCase();
    }});
    inp.addEventListener('blur', function() {{
      const val = this.value;
      const field = this.dataset.field;
      document.querySelectorAll(`.char-cell[data-field="${{field}}"]`).forEach(span => {{
        const i = parseInt(span.dataset.idx);
        span.textContent = val[i] || '';
      }});
    }});
  }});

  // Submit
  document.getElementById('mainForm').addEventListener('submit', function(e) {{
    e.preventDefault();
    const data = {{}};

    document.querySelectorAll('.row-input').forEach(inp => {{
      const f = inp.dataset.field;
      data[f] = (data[f] || '') + inp.value;
    }});

    document.querySelectorAll('.narr-field').forEach(ta => {{
      data[ta.name] = ta.value.toUpperCase();
    }});

    fetch('/generate-pdf', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify(data)
    }})
    .then(r => r.blob())
    .then(blob => {{
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'formulario_cidadania.pdf';
      a.click();
    }});
  }});
</script>
</body>
</html>'''

    out = Path(__file__).parent.parent / 'public' / 'form_viewer.html'
    out.write_text(html, encoding='utf-8')
    print(f'[generate_form_html] Saved: {out}')


if __name__ == '__main__':
    generate()
