#!/usr/bin/env python3
"""
pdf-injector.py - Inject form data into official Polish government PDF
Usage: python pdf-injector.py <input_json_path> <output_pdf_path>
"""

import sys
import json
import fitz  # PyMuPDF
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Paths
OFFICIAL_PDF = str(Path(__file__).parent.parent / 'templates' / 'official_form.pdf')

def _find_font():
    candidates = [
        Path(__file__).parent.parent / 'fonts' / 'arial.ttf',        # bundled (all platforms)
        Path('C:/Windows/Fonts/arial.ttf'),                           # Windows system
        Path('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'),  # Debian/Ubuntu
        Path('/usr/share/fonts/liberation/LiberationSans-Regular.ttf'),           # RHEL/CentOS
        Path('/nix/var/nix/profiles/default/share/fonts/truetype/LiberationSans-Regular.ttf'),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None

FONT_PATH = _find_font()
# TextWriter font — full Unicode support (handles Polish Ą Ć Ę Ł Ń Ó Ś Ź Ż etc.)
_FITZ_FONT = fitz.Font(fontfile=FONT_PATH) if FONT_PATH else fitz.Font("helv")


def _tw_insert(page, x, y, text, fontsize):
    """Insert text at (x, y) using TextWriter for full Unicode glyph support."""
    tw = fitz.TextWriter(page.rect)
    tw.append(fitz.Point(x, y), text, font=_FITZ_FONT, fontsize=fontsize)
    tw.write_text(page, color=(0, 0, 0))

BOX_FONT_SIZE = 7.5
BOX_CHAR_OFFSET = 3.5   # pts from separator left edge to char baseline x
BOX_Y_OFFSET = 6.5      # pts below box top y to text baseline (box height ~8pt, font 7.5pt)

NARR_FONT_SIZE = 8.5
NARR_X0 = 70.0
NARR_X1 = 525.0  # right margin for narrative text (A4 width 595 - ~70pt right margin)

# ============================================================
# FIELD MAP  — letter boxes (pages 1-5)
# Each entry: list of row specs {page, y, x0, n, sp}
#   page  = 0-indexed page number
#   y     = y-coordinate of the TOP of the separator lines
#   x0    = x of first separator
#   n     = number of character BOXES in this row (for this field slice)
#   sp    = separator spacing (pts)
# ============================================================
FIELD_MAP = {

    # ---- PAGE 1 (top stamp area) ----
    'miejsce_zlozenia':  [{'page': 0, 'y': 137, 'x0': 325.04, 'n': 10, 'sp': 17.27}],
    'data_zlozenia_ano': [{'page': 0, 'y': 161, 'x0': 325.04, 'n': 4,  'sp': 17.27}],
    'data_zlozenia_mes': [{'page': 0, 'y': 161, 'x0': 411.38, 'n': 2,  'sp': 17.27}],
    'data_zlozenia_dia': [{'page': 0, 'y': 161, 'x0': 463.16, 'n': 2,  'sp': 17.27}],

    # ---- PAGE 1 ----
    'wnioskodawca_nome': [
        {'page': 0, 'y': 345, 'x0': 152.37, 'n': 20, 'sp': 17.27},
        {'page': 0, 'y': 361, 'x0': 152.37, 'n': 20, 'sp': 17.27},
    ],
    'endereco_pais':    [{'page': 0, 'y': 409, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'endereco_cidade':  [{'page': 0, 'y': 425, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'endereco_rua':     [{'page': 0, 'y': 441, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    # y=456: 16 wider boxes — first 7 = house nr, last 7 = apt nr (gap in middle)
    'endereco_casa':    [{'page': 0, 'y': 456, 'x0': 152.89, 'n': 7,  'sp': 22.99}],
    'endereco_apto':    [{'page': 0, 'y': 456, 'x0': 152.89 + 9 * 22.99, 'n': 6, 'sp': 22.99}],
    # y=474: postal code (first 8 boxes) + city after code
    'endereco_cep':     [{'page': 0, 'y': 474, 'x0': 152.37, 'n': 8,  'sp': 18.18}],
    'endereco_poczta':  [{'page': 0, 'y': 474, 'x0': 290.49, 'n': 12, 'sp': 17.27}],
    # y=489: telephone
    'endereco_tel':     [{'page': 0, 'y': 489, 'x0': 152.37, 'n': 20, 'sp': 17.27}],

    # ---- PAGE 2 — Requester (Część I) ----
    'req_sobrenome':          [{'page': 1, 'y': 312, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'req_sobrenome_solteiro': [
        {'page': 1, 'y': 329, 'x0': 152.37, 'n': 20, 'sp': 17.27},
        {'page': 1, 'y': 345, 'x0': 152.37, 'n': 20, 'sp': 17.27},
    ],
    'req_nomes': [{'page': 1, 'y': 361, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'req_pai':   [{'page': 1, 'y': 377, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'req_mae':   [
        {'page': 1, 'y': 393, 'x0': 152.37, 'n': 20, 'sp': 17.27},
        {'page': 1, 'y': 417, 'x0': 152.37, 'n': 20, 'sp': 17.27},
    ],
    'req_sobrenomes_usados': [{'page': 1, 'y': 433, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    # Date of birth: y=448 (n=13 wider boxes) — rok[0-3] / mes[5-6] / dia[8-9]
    'req_nasc_ano': [{'page': 1, 'y': 448, 'x0': 152.89,              'n': 4, 'sp': 22.03}],
    'req_nasc_mes': [{'page': 1, 'y': 448, 'x0': 152.89 + 5 * 22.03, 'n': 2, 'sp': 22.03}],
    'req_nasc_dia': [{'page': 1, 'y': 448, 'x0': 152.89 + 8 * 22.03, 'n': 2, 'sp': 22.03}],
    # y=473: sex (M or K — single char)
    'req_sexo':      [{'page': 1, 'y': 473, 'x0': 152.37, 'n': 1, 'sp': 17.27}],
    'req_local_nasc':[{'page': 1, 'y': 497, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'req_cidadanias':[
        {'page': 1, 'y': 513, 'x0': 152.37, 'n': 20, 'sp': 17.27},
        {'page': 1, 'y': 529, 'x0': 152.37, 'n': 20, 'sp': 17.27},
    ],
    'req_estado_civil': [{'page': 1, 'y': 545, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'req_pesel':        [{'page': 1, 'y': 561, 'x0': 152.89, 'n': 11, 'sp': 17.26}],

    # ---- PAGE 3 — Mother (D.I) + start of Father (D.II) ----
    'mae_sobrenome':         [{'page': 2, 'y': 337, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_sobrenome_solteira':[{'page': 2, 'y': 353, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_nomes':             [{'page': 2, 'y': 369, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_pai':               [{'page': 2, 'y': 385, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_mae':               [{'page': 2, 'y': 401, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_sobrenomes_usados': [{'page': 2, 'y': 417, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    # y=441, 457: skipped (form fields not in HTML)
    # y=472 (n=11): date of birth
    'mae_nasc_ano': [{'page': 2, 'y': 472, 'x0': 152.89,              'n': 4, 'sp': 17.27}],
    'mae_nasc_mes': [{'page': 2, 'y': 472, 'x0': 152.89 + 5 * 17.27, 'n': 2, 'sp': 17.27}],
    'mae_nasc_dia': [{'page': 2, 'y': 472, 'x0': 152.89 + 8 * 17.27, 'n': 2, 'sp': 17.27}],
    'mae_local_nasc':  [{'page': 2, 'y': 497, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_estado_civil':[{'page': 2, 'y': 521, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    # y=536 (n=11): marriage date
    'mae_cas_ano': [{'page': 2, 'y': 536, 'x0': 152.89,              'n': 4, 'sp': 17.27}],
    'mae_cas_mes': [{'page': 2, 'y': 536, 'x0': 152.89 + 5 * 17.27, 'n': 2, 'sp': 17.27}],
    'mae_cas_dia': [{'page': 2, 'y': 536, 'x0': 152.89 + 8 * 17.27, 'n': 2, 'sp': 17.27}],
    'mae_local_cas': [
        {'page': 2, 'y': 561, 'x0': 152.37, 'n': 20, 'sp': 17.27},
        {'page': 2, 'y': 593, 'x0': 152.37, 'n': 20, 'sp': 17.27},
    ],
    'mae_cidadanias': [{'page': 2, 'y': 613, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'mae_pesel':      [{'page': 2, 'y': 636, 'x0': 152.89, 'n': 11, 'sp': 17.26}],
    # Father starts at bottom of page 3
    'pai_sobrenome':        [{'page': 2, 'y': 683, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'pai_sobrenome_solteiro':[{'page': 2, 'y': 699, 'x0': 152.37, 'n': 20, 'sp': 17.27}],
    'pai_nomes':            [{'page': 2, 'y': 715, 'x0': 152.37, 'n': 20, 'sp': 17.27}],

    # ---- PAGE 4 — Father (cont.) + Maternal grandparents ----
    'pai_pai':              [{'page': 3, 'y': 108, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'pai_mae':              [{'page': 3, 'y': 124, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'pai_sobrenomes_usados':[{'page': 3, 'y': 140, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    # y=164, 180: skipped (additional form fields not in HTML)
    # y=195 (n=11): father date of birth
    'pai_nasc_ano': [{'page': 3, 'y': 195, 'x0': 153.60,              'n': 4, 'sp': 17.27}],
    'pai_nasc_mes': [{'page': 3, 'y': 195, 'x0': 153.60 + 5 * 17.27, 'n': 2, 'sp': 17.27}],
    'pai_nasc_dia': [{'page': 3, 'y': 195, 'x0': 153.60 + 8 * 17.27, 'n': 2, 'sp': 17.27}],
    'pai_local_nasc':  [{'page': 3, 'y': 220, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    # y=244 (n=12): PESEL
    'pai_pesel':       [{'page': 3, 'y': 244, 'x0': 153.60, 'n': 11, 'sp': 17.26}],
    # y=259 (n=11): marriage date
    'pai_cas_ano': [{'page': 3, 'y': 259, 'x0': 153.60,              'n': 4, 'sp': 17.27}],
    'pai_cas_mes': [{'page': 3, 'y': 259, 'x0': 153.60 + 5 * 17.27, 'n': 2, 'sp': 17.27}],
    'pai_cas_dia': [{'page': 3, 'y': 259, 'x0': 153.60 + 8 * 17.27, 'n': 2, 'sp': 17.27}],
    'pai_estado_civil':[{'page': 3, 'y': 284, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'pai_local_cas':   [{'page': 3, 'y': 316, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'pai_cidadanias':  [{'page': 3, 'y': 335, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    # Maternal grandfather (avo_mat_*) — y=434+
    'avo_mat_sobrenome':        [{'page': 3, 'y': 434, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_mat_sobrenome_solteiro':[{'page': 3, 'y': 450, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_mat_nomes':            [{'page': 3, 'y': 466, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_mat_pai':              [{'page': 3, 'y': 482, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_mat_mae':              [{'page': 3, 'y': 498, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    # y=514: skipped
    # y=537 (n=11): date of birth
    'avo_mat_nasc_ano': [{'page': 3, 'y': 537, 'x0': 153.60,              'n': 4, 'sp': 17.27}],
    'avo_mat_nasc_mes': [{'page': 3, 'y': 537, 'x0': 153.60 + 5 * 17.27, 'n': 2, 'sp': 17.27}],
    'avo_mat_nasc_dia': [{'page': 3, 'y': 537, 'x0': 153.60 + 8 * 17.27, 'n': 2, 'sp': 17.27}],
    'avo_mat_local_nasc':[{'page': 3, 'y': 562, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_mat_pesel':     [{'page': 3, 'y': 586, 'x0': 153.60, 'n': 11, 'sp': 17.26}],
    # Maternal grandmother (ava_mat_*) — y=648+
    'ava_mat_sobrenome':        [{'page': 3, 'y': 648, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_mat_sobrenome_solteira':[{'page': 3, 'y': 664, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_mat_nomes':            [{'page': 3, 'y': 680, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_mat_pai':              [{'page': 3, 'y': 696, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_mat_mae':              [{'page': 3, 'y': 712, 'x0': 153.07, 'n': 20, 'sp': 17.27}],

    # ---- PAGE 5 — Paternal grandparents ----
    'avo_pat_sobrenome':         [{'page': 4, 'y': 108, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    # y=131 (n=11): short row (birth name or date)
    'avo_pat_sobrenome_solteiro':[{'page': 4, 'y': 131, 'x0': 153.60, 'n': 10, 'sp': 17.27}],
    'avo_pat_nomes':             [{'page': 4, 'y': 156, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    # y=180 (n=12): PESEL or date
    'avo_pat_nasc_ano': [{'page': 4, 'y': 180, 'x0': 153.60,              'n': 4, 'sp': 17.26}],
    'avo_pat_nasc_mes': [{'page': 4, 'y': 180, 'x0': 153.60 + 5 * 17.26, 'n': 2, 'sp': 17.26}],
    'avo_pat_nasc_dia': [{'page': 4, 'y': 180, 'x0': 153.60 + 8 * 17.26, 'n': 2, 'sp': 17.26}],
    'avo_pat_pai':      [{'page': 4, 'y': 231, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_pat_mae':      [{'page': 4, 'y': 247, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'avo_pat_local_nasc':[{'page': 4, 'y': 360, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    # y=335 (n=11): date
    'avo_pat_cas_ano':  [{'page': 4, 'y': 335, 'x0': 153.60,              'n': 4, 'sp': 17.27}],
    'avo_pat_cas_mes':  [{'page': 4, 'y': 335, 'x0': 153.60 + 5 * 17.27, 'n': 2, 'sp': 17.27}],
    'avo_pat_cas_dia':  [{'page': 4, 'y': 335, 'x0': 153.60 + 8 * 17.27, 'n': 2, 'sp': 17.27}],
    'avo_pat_pesel':    [{'page': 4, 'y': 384, 'x0': 153.60, 'n': 11, 'sp': 17.26}],
    # Paternal grandmother (ava_pat_*) — y=435+
    'ava_pat_sobrenome':         [{'page': 4, 'y': 435, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_pat_sobrenome_solteira':[{'page': 4, 'y': 451, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_pat_nomes':             [{'page': 4, 'y': 467, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_pat_pai':               [{'page': 4, 'y': 483, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_pat_mae':               [{'page': 4, 'y': 499, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    # y=538 (n=11): date
    'ava_pat_nasc_ano': [{'page': 4, 'y': 538, 'x0': 153.60,              'n': 4, 'sp': 17.27}],
    'ava_pat_nasc_mes': [{'page': 4, 'y': 538, 'x0': 153.60 + 5 * 17.27, 'n': 2, 'sp': 17.27}],
    'ava_pat_nasc_dia': [{'page': 4, 'y': 538, 'x0': 153.60 + 8 * 17.27, 'n': 2, 'sp': 17.27}],
    'ava_pat_local_nasc':[{'page': 4, 'y': 563, 'x0': 153.07, 'n': 20, 'sp': 17.27}],
    'ava_pat_pesel':     [{'page': 4, 'y': 587, 'x0': 153.60, 'n': 11, 'sp': 17.26}],
}

# ============================================================
# NARRATIVE MAP — free-text on dotted lines (pages 6-11)
# Each entry: {page, lines: [y_baselines...], x0}
# ============================================================
NARRATIVE_MAP = {
    'bio_requerente': {
        'page': 5,
        'lines': [182,194,206,218,230,242,254,266,278,290,302,314,326,338,350,362,374,386,398,410,422],
        'x0': 70.7,
    },
    'bio_mae': {
        'page': 6,
        'lines': [179,191,203,215,227,239,251,263,275,287,299,311,323,335,347],
        'x0': 70.0,
    },
    'bio_pai': {
        'page': 6,
        'lines': [417,429,441,453,465,477,489,501,513,525,537,549,561,573,585],
        'x0': 70.0,
    },
    'bio_avo_mat': [
        {'page': 6, 'lines': [675,687,699,711], 'x0': 70.0},
        {'page': 7, 'lines': [100,112,124,136,148,160,172,184,196,208,220], 'x0': 70.0},
    ],
    'bio_ava_mat': {
        'page': 7,
        'lines': [288,300,312,324,336,348,360,372,384,396,408,420,432,444,456],
        'x0': 70.0,
    },
    'bio_avo_pat': {
        'page': 7,
        'lines': [536,548,560,572,584,596,608,620,632,644,656,668,680,692,704],
        'x0': 70.0,
    },
    'bio_ava_pat': {
        'page': 8,
        'lines': [156,168,180,192,204,216,228,240,252,264,276,288,300,312,324],
        'x0': 70.7,
    },
    'bio_bisavos': {
        'page': 8,
        'lines': [426,438,450,462,474,486,498,510,522,534,546,558,570,582,594,606,618],
        'x0': 70.7,
    },
    'info_decisoes_irmaos': {
        'page': 9,
        'lines': [127,139,151,163,175],
        'x0': 69.3,
    },
    'info_docs_poloneses': {
        'page': 9,
        'lines': [236,248,260,272,284],
        'x0': 69.3,
    },
    'info_renuncia': {
        'page': 9,
        'lines': [368,380,392,404,416],
        'x0': 69.3,
    },
    'info_adicional': {
        'page': 9,
        'lines': [473,485,497,509,521,533,545,557,569,581,593,605,617,629,641,653,665,677,689,701],
        'x0': 69.3,
    },
    'anexos_lista': {
        'page': 10,
        'lines': [102,114,126,138,150,162,174,186,198,210],
        'x0': 70.0,
    },
}


def inject_letterbox(page, rows, text):
    """Inject text character-by-character into letter boxes across rows."""
    if not text:
        return
    chars = list(text)
    char_idx = 0

    for row in rows:
        if char_idx >= len(chars):
            break
        y     = row['y']
        x0    = row['x0']
        n     = row['n']
        sp    = row['sp']

        for box_i in range(n):
            if char_idx >= len(chars):
                break
            ch = chars[char_idx]
            char_idx += 1
            x = x0 + box_i * sp + BOX_CHAR_OFFSET
            baseline_y = y + BOX_Y_OFFSET
            _tw_insert(page, x, baseline_y, ch, BOX_FONT_SIZE)


def inject_narrative(page, lines, x0, text):
    """Inject narrative text as justified, filling the dotted-line area."""
    if not text or not lines:
        return 0
    y_top = lines[0] - 3
    y_bottom = lines[-1] + NARR_FONT_SIZE + 4
    rect = fitz.Rect(x0, y_top, NARR_X1, y_bottom)
    kwargs = dict(fontsize=NARR_FONT_SIZE, align=fitz.TEXT_ALIGN_JUSTIFY, color=(0, 0, 0))
    if FONT_PATH:
        kwargs['fontfile'] = FONT_PATH
        kwargs['fontname'] = 'custom'
    else:
        kwargs['fontname'] = 'helv'
    page.insert_textbox(rect, text, **kwargs)
    return len(lines)


def build_req_sexo_value(raw):
    """Normalize sex field: M/K from select option."""
    v = str(raw).upper().strip()
    if v.startswith('M'):
        return 'M'
    if v.startswith('K') or v.startswith('F') or v.startswith('W'):
        return 'K'
    return v[:1]


def inject_form(form_data, output_path):
    doc = fitz.open(OFFICIAL_PDF)
    pages = [doc[i] for i in range(len(doc))]

    # --- Letter box fields (character-by-character, auto-compress if text exceeds boxes) ---
    for field_name, rows in FIELD_MAP.items():
        value = form_data.get(field_name, '')
        if not value:
            continue
        if field_name == 'req_sexo':
            value = build_req_sexo_value(value)
        value = str(value).upper().strip()

        chars = list(value)
        total_boxes = sum(row['n'] for row in rows)

        if len(chars) <= total_boxes:
            # Normal: one char per box
            char_idx = 0
            for row in rows:
                if char_idx >= len(chars):
                    break
                page_obj = pages[row['page']]
                for box_i in range(row['n']):
                    if char_idx >= len(chars):
                        break
                    x = row['x0'] + box_i * row['sp'] + BOX_CHAR_OFFSET
                    baseline_y = row['y'] + BOX_Y_OFFSET
                    _tw_insert(page_obj, x, baseline_y, chars[char_idx], BOX_FONT_SIZE)
                    char_idx += 1
        else:
            # Auto-fit: compress spacing so all chars fit on available rows
            total_width = sum(row['n'] * row['sp'] for row in rows)
            char_spacing = total_width / len(chars)
            scale = char_spacing / rows[0]['sp']
            effective_fontsize = max(4.5, BOX_FONT_SIZE * scale)
            char_idx = 0
            for row in rows:
                if char_idx >= len(chars):
                    break
                page_obj = pages[row['page']]
                row_width = row['n'] * row['sp']
                chars_this_row = min(len(chars) - char_idx, round(row_width / char_spacing))
                if chars_this_row <= 0:
                    continue
                actual_sp = row_width / chars_this_row
                for i in range(chars_this_row):
                    if char_idx >= len(chars):
                        break
                    x = row['x0'] + i * actual_sp + BOX_CHAR_OFFSET
                    baseline_y = row['y'] + BOX_Y_OFFSET
                    _tw_insert(page_obj, x, baseline_y, chars[char_idx], effective_fontsize)
                    char_idx += 1

    # --- Narrative fields ---
    for field_name, spec in NARRATIVE_MAP.items():
        value = form_data.get(field_name, '')
        # Narrative fields may come with _pl translated version
        pl_value = form_data.get(f'{field_name}_pl', '')
        text = pl_value if pl_value else value
        if not text:
            continue
        # Support single spec (dict) or multi-page spec (list of dicts)
        specs = spec if isinstance(spec, list) else [spec]
        for s in specs:
            inject_narrative(pages[s['page']], s['lines'], s['x0'], text)

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    print(f'[pdf-injector] Saved: {output_path}', file=sys.stderr)


def main():
    if len(sys.argv) < 3:
        print('Usage: pdf-injector.py <input_json> <output_pdf>', file=sys.stderr)
        sys.exit(1)

    input_json = sys.argv[1]
    output_pdf = sys.argv[2]

    with open(input_json, 'r', encoding='utf-8') as f:
        form_data = json.load(f)

    inject_form(form_data, output_pdf)


if __name__ == '__main__':
    main()
