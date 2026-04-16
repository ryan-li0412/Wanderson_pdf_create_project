#!/usr/bin/env python3
"""
make_pt_pages.py
Generates Portuguese-labeled versions of the official Polish form pages.
Whites out Polish text labels and replaces with Portuguese.
Output: public/form_pages_pt/page_N.png
Coordinates derived from actual PDF text positions via fitz.get_text('dict').
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

SRC  = Path(__file__).parent.parent / 'public' / 'form_pages'
DEST = Path(__file__).parent.parent / 'public' / 'form_pages_pt'
DEST.mkdir(parents=True, exist_ok=True)

SCALE = 150 / 72   # pt -> px

def px(v): return round(v * SCALE)

# fonts
try:
    F8   = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',  16)
    F9   = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',  18)
    F10  = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',  20)
    FB10 = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 20)
    FB12 = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 25)
    FB14 = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 29)
except Exception:
    F8 = F9 = F10 = FB10 = FB12 = FB14 = ImageFont.load_default()


def cover(draw, x0, y0, x1, y1, padding=2):
    draw.rectangle([x0-padding, y0-padding, x1+padding, y1+padding], fill='white')


def label(draw, x, y, text, font=None, color='black'):
    if font is None:
        font = F9
    draw.text((x, y), text, fill=color, font=font)


def cover_label(draw, x_pt, y_pt, w_pt, h_pt, text, font=None, pad=2):
    """White out pt-based region then place text."""
    x0, y0 = px(x_pt), px(y_pt)
    x1, y1 = px(x_pt + w_pt), px(y_pt + h_pt)
    cover(draw, x0, y0, x1, y1, pad)
    if text:
        if font is None:
            font = F9
        label(draw, x0 + 2, y0 + 2, text, font)


def cover_label2(draw, x_pt, y_pt, w_pt, h_pt, line1, line2, font=None, pad=2):
    """White out region and add two-line text."""
    x0, y0 = px(x_pt), px(y_pt)
    x1, y1 = px(x_pt + w_pt), px(y_pt + h_pt)
    cover(draw, x0, y0, x1, y1, pad)
    if font is None:
        font = F9
    if line1:
        label(draw, x0 + 2, y0 + 1, line1, font)
    if line2:
        label(draw, x0 + 2, y0 + 19, line2, font)


def date_sublabels(draw, y_pt, x0_pt, sp_pt, suffix=''):
    """
    Cover "rok/miesiąc/dzień" sub-labels and place PT versions.
    y_pt: y of the sub-label text line (below cells)
    x0_pt: x start of year cells
    sp_pt: cell spacing (17.27 or 22.03)
    suffix: unused, kept for compat
    """
    # year group: 4 cells; gap cell (sep); month group: 2 cells; gap; day group: 2 cells
    w_year  = 4 * sp_pt
    x_month = x0_pt + 5 * sp_pt
    w_month = 2 * sp_pt
    x_day   = x0_pt + 8 * sp_pt
    w_day   = 2 * sp_pt
    cover_label(draw, x0_pt,   y_pt - 1, w_year  + 1, 13, 'ano', F8)
    cover_label(draw, x_month, y_pt - 1, w_month + 1, 13, 'mês', F8)
    cover_label(draw, x_day,   y_pt - 1, w_day   + 1, 13, 'dia', F8)


# ── PAGE 0 (page_1.png) ──────────────────────────────────────────────────────
def process_page_0(draw):
    # Stamp text: "(pieczęć organu przyjmującego wniosek)" at y=172.9, x=70
    cover_label(draw, 70, 171, 257, 13, '(carimbo do órgão receptor)', F8)

    # Date sub-labels: "rok  miesiąc  dzień" at y=172.5, x=357
    # Year cells (data_zlozenia g1): x0=325.04, n=4, sp=17.27
    cover_label(draw, 325, 171, 87,  13, 'ano', F8)
    # Month cells (g2): x0=411.38, n=2, sp=17.27
    cover_label(draw, 411, 171, 36,  13, 'mês', F8)
    # Day cells (g3): x0=463.16, n=2, sp=17.27
    cover_label(draw, 463, 171, 36,  13, 'dia', F8)

    # "(miejsce i data złożenia wniosku)" at y=189.0, x=347.2
    cover_label(draw, 325, 188, 180, 12, '(lugar e data de apresentação)', F8)

    # Notice box content at y=215-257
    cover_label(draw, 70, 203, 470, 100,
                'Antes de preencher o pedido, leia as instruções na página 12.\n'
                'O pedido é preenchido em língua polonesa.', F8)

    # "WOJEWODA ..." at y=284.5, x=273.5
    cover_label(draw, 175, 283, 365, 18,
                'VOIVODA ......................................................', F9)
    # "(wskazanie organu...)" at y=295.4, x=285.6
    cover_label(draw, 283, 294, 257, 13,
                '(indicação do órgão ao qual o pedido é submetido)', F8)

    # "WNIOSKODAWCA" at y=320.7-334.7, x=70
    cover_label(draw, 70, 319, 255, 17, 'REQUERENTE', FB14)

    # "Imię i nazwisko/nazwa" at y=345.0; "podmiotu" at y=353.0
    cover_label2(draw, 70, 343, 88, 24, 'Nome e sobrenome /', 'nome da entidade', F9)

    # "ADRES ZAMIESZKANIA/SIEDZIBY" at y=388.7-402.6, x=70
    cover_label(draw, 70, 387, 295, 18, 'ENDEREÇO DE RESIDÊNCIA / SEDE', FB12)

    # Field labels (using actual PDF text y positions)
    # "1 Państwo/województwo" at y=409.1
    cover_label(draw, 70, 407, 95, 13, '1 País / Voivodia', F9)
    # "2 Miejscowość" at y=425.0
    cover_label(draw, 70, 423, 95, 13, '2 Localidade', F9)
    # "3 Ulica" at y=441.0
    cover_label(draw, 70, 439, 95, 13, '3 Rua', F9)
    # "4 Numer domu" at y=457.1
    cover_label(draw, 70, 455, 95, 13, '4 Número da casa', F9)
    # "5 Numer mieszkania" at y=457.1, x=280.4
    cover_label(draw, 278, 455, 105, 13, '5 Número do apartamento', F9)
    # "6 Kod pocztowy" at y=473.1
    cover_label(draw, 70, 471, 95, 13, '6 Código postal', F9)
    # PT label for postal town (no original label exists here)
    cover_label(draw, 258, 471, 35,  13, 'Cidade postal', F8)
    # "7 Telefon kontaktowy" at y=489.0
    cover_label(draw, 70, 487, 95, 13, '7 Telefone de contato', F9)

    # "WNIOSEK" at y=552.9-565.8, x=259.1
    cover_label(draw, 175, 551, 268, 18, 'PEDIDO', FB14)
    # "o potwierdzenie..." at y=563.8-577.7, x=144.3
    cover_label(draw, 70,  561, 475, 19,
                'de confirmação de posse ou perda de cidadania polonesa', F10)
    # "Wnoszę o wydanie decyzji:" at y=587.8-601.7, x=70
    cover_label(draw, 70,  585, 325, 20, 'Solicito a emissão de decisão:', FB10)

    # Checkbox option 1: "potwierdzającej posiadanie..." at y=612.2; "(imię i nazwisko)" at y=623.4
    cover_label2(draw, 82, 609, 462, 28,
                 'confirmando a posse de cidadania polonesa por ......................................',
                 '(nome e sobrenome)', F9)
    # Checkbox option 2: "potwierdzającej utratę..." at y=637.2; "(imię i nazwisko)" at y=648.3
    cover_label2(draw, 82, 634, 462, 28,
                 'confirmando a perda de cidadania polonesa por .......................................',
                 '(nome e sobrenome)', F9)

    # Bottom text: y=673.7 and y=685.2
    cover_label2(draw, 70, 671, 475, 30,
                 'Informações adicionais relativas ao estado de fato ou de direito relacionadas com a confirmação',
                 'de posse ou perda de cidadania polonesa: ..............................', F9)


# ── PAGE 1 (page_2.png) - CZĘŚĆ I ────────────────────────────────────────────
def process_page_1(draw):
    # Top paragraph at y=100.5-124.3
    cover_label2(draw, 70, 98, 470, 50,
                 'Se o pedido não diz respeito ao requerente, mas a terceiro, por que razão o',
                 'requerente busca a decisão de confirmação?', F9)

    # "C Z Ę Ś Ć  I" at y=266.4-280.3, x=70
    cover_label(draw, 70, 264, 95, 19, 'PARTE I', FB14)

    # "A. Dane osoby, której dotyczy wniosek." at y=290.5-303.3, x=70
    cover_label(draw, 70, 288, 375, 18, 'A. Dados da pessoa a quem se refere o pedido.', FB10)

    # "1 Nazwisko" at y=312.8, x=70
    cover_label(draw, 70, 311, 95, 13, '1 Sobrenome', F9)
    # "2 Nazwisko rodowe" at y=344.8, x=70
    cover_label(draw, 70, 343, 120, 13, '2 Sobrenome de solteiro(a)', F9)
    # "3 Imię (imiona)" at y=360.8, x=70
    cover_label(draw, 70, 359, 95, 13, '3 Nome(s)', F9)
    # "4 Imię i nazwisko ojca" at y=376.8, x=70
    cover_label(draw, 70, 375, 130, 13, '4 Nome e sobrenome do pai', F9)
    # "5 Imię i nazwisko rodowe" y=392.8 + "matki" y=400.8
    cover_label2(draw, 70, 391, 95, 22, '5 Nome e sobrenome de', 'solteira da mãe', F9)
    # "6 Używane nazwiska wraz" y=416.8 + "z datą zmiany" y=424.7
    cover_label2(draw, 70, 415, 95, 22, '6 Sobrenomes usados com', 'data de alteração', F9)
    # "7 Data urodzenia" at y=448.8, x=70
    cover_label(draw, 70, 447, 95, 13, '7 Data de nascimento', F9)
    # "8 Płeć" at y=448.8, x=332.6 (same line as field 7)
    cover_label(draw, 330, 447, 65, 13, '8 Sexo', F9)

    # Date sub-labels "rok/miesiąc/dzień" at y=455.3, x=153.6
    # req_nasc cells: sp=22.03; year x0=152.89, month x0=263.04, day x0=329.13
    date_sublabels(draw, 455, 152.89, 22.03)

    # "m – mężczyzna k – kobieta" at y=455.3, x=362.6
    cover_label(draw, 358, 454, 190, 13, 'm – masculino   k – feminino', F8)

    # "9 Miejsce urodzenia" at y=472.8 + "(państwo/miejscowość)" at y=480.8
    cover_label2(draw, 70, 471, 135, 22, '9 Local de nascimento', '(país/localidade)', F9)

    # "10 Posiadane obce" y=496.8 + "obywatelstwa wraz" y=504.8 + "z datą nabycia" y=512.8
    cover_label2(draw, 70, 494, 125, 32, '10 Cidadanias estrangeiras', 'com data de aquisição', F9)

    # "11 Stan cywilny" at y=544.8, x=70
    cover_label(draw, 70, 543, 95, 13, '11 Estado civil', F9)

    # "12 Nr PESEL (jeżeli" y=560.9 + "został nadany" y=568.8
    cover_label2(draw, 70, 558, 95, 24, '12 Nr PESEL', '(se atribuído)', F9)

    # "B. Czy w stosunku..." at y=584.7+
    cover_label2(draw, 70, 582, 475, 52,
                 'B. Em relação à pessoa a quem se refere o pedido, foi emitida decisão de confirmação/',
                 'negação de posse ou perda de cidadania polonesa? Se sim, qual órgão e quando?', F9)


# ── PAGE 2 (page_3.png) - C,D,E + Mother + Father start ──────────────────────
def process_page_2(draw):
    # "C. Czy osoba..." at y=99.8-156.6 (multi-line)
    cover_label2(draw, 70, 97, 475, 62,
                 'C. A pessoa a quem se refere o pedido requereu autorização para mudança de',
                 'cidadania polonesa ou para renúncia? Se sim, qual órgão e quando emitiu decisão?', F9)

    # "D. Miejsca zamieszkania..." at y=222.8, x=85.6
    cover_label(draw, 70, 221, 475, 18,
                'D. Locais de residência da pessoa a quem se refere o pedido, na Polônia e no exterior.', FB10)

    # "E. Dane osobowe rodziców..." at y=291.1, x=85.7
    cover_label(draw, 70, 289, 475, 18,
                'E. Dados pessoais dos pais da pessoa a quem se refere o pedido.', FB10)

    # "I. Dane dotyczące matki." at y=314.0
    cover_label(draw, 70, 312, 215, 16, 'I. Dados referentes à mãe.', FB10)

    # Mother field labels (actual PDF positions from text extraction)
    # "1 Nazwisko" at y=337.3
    cover_label(draw, 70, 335, 95, 13, '1 Sobrenome', F9)
    # "2 Nazwisko rodowe" at y=369.4
    cover_label(draw, 70, 367, 120, 13, '2 Sobrenome de solteira', F9)
    # "3 Imię (imiona)" at y=385.3
    cover_label(draw, 70, 383, 95, 13, '3 Nome(s)', F9)
    # "4 Imię i nazwisko ojca" at y=401.3
    cover_label(draw, 70, 399, 130, 13, '4 Nome e sobrenome do pai', F9)
    # "5 Imię i nazwisko rodowe" y=417.3 + "matki" y=425.3
    cover_label2(draw, 70, 415, 95, 22, '5 Nome e sobrenome de', 'solteira da mãe', F9)
    # "6 Używane nazwiska wraz" y=441.3 + "z datą zmiany" y=449.3
    cover_label2(draw, 70, 439, 95, 22, '6 Sobrenomes usados com', 'data de alteração', F9)
    # "7 Data urodzenia" at y=473.3
    cover_label(draw, 70, 471, 95, 13, '7 Data de nascimento', F9)

    # Date sub-labels for birth at y=479.8, x=153.6; mae_nasc sp=17.27
    date_sublabels(draw, 479, 152.89, 17.27)

    # "8 Miejsce urodzenia" y=497.3 + "(państwo/miejscowość)" y=505.4
    cover_label2(draw, 70, 495, 135, 22, '8 Local de nascimento', '(país/localidade)', F9)
    # "9 Stan cywilny" at y=521.3
    cover_label(draw, 70, 519, 95, 13, '9 Estado civil', F9)
    # "10 Data zawarcia związku" y=537.3 + "małżeńskiego" y=545.3
    cover_label2(draw, 70, 535, 130, 22, '10 Data de casamento', '', F9)

    # Marriage date sub-labels at y=543.8, x=153.6; mae_cas sp=17.27
    date_sublabels(draw, 543, 152.89, 17.27)

    # "11 Miejsce zawarcia" y=561.3 + "związku małżeńskiego" y=569.3 + "(państwo/...)" y=577.4
    cover_label2(draw, 70, 559, 135, 30, '11 Local do casamento', '(país/localidade)', F9)

    # "12 Obywatelstwa posiadane w dacie urodzenia..." y=593.3-617.3 (4 lines)
    cover_label2(draw, 70, 591, 130, 32,
                 '12 Cidadanias na data de nascimento', 'da pessoa do pedido', F9)

    # "13 Nr PESEL (jeżeli" y=633.3 + "został nadany" y=641.4
    cover_label2(draw, 70, 631, 95, 24, '13 Nr PESEL', '(se atribuído)', F9)

    # "II. Dane dotyczące ojca." at y=660.2
    cover_label(draw, 70, 658, 215, 16, 'II. Dados referentes ao pai.', FB10)

    # Father field 1: "1 Nazwisko" at y=683.4
    cover_label(draw, 70, 681, 95, 13, '1 Sobrenome', F9)
    # Father field 2: "2 Nazwisko rodowe" at y=715.4
    cover_label(draw, 70, 713, 120, 13, '2 Sobrenome de solteiro', F9)


# ── PAGE 3 (page_4.png) - Father cont. + Maternal grandparents ───────────────
def process_page_3(draw):
    # Father fields continued (from page 2)
    # "3 Imię (imiona)" at y=107.9, x=70.7
    cover_label(draw, 70, 106, 95, 13, '3 Nome(s)', F9)
    # "4 Imię i nazwisko ojca" at y=124.0
    cover_label(draw, 70, 122, 130, 13, '4 Nome e sobrenome do pai', F9)
    # "5 Imię i nazwisko rodowe" y=140.0 + "matki" y=148.0
    cover_label2(draw, 70, 138, 95, 22, '5 Nome e sobrenome de', 'solteira da mãe', F9)
    # "6 Używane nazwiska wraz" y=164.0 + "z datą zmiany" y=172.0
    cover_label2(draw, 70, 162, 95, 22, '6 Sobrenomes usados com', 'data de alteração', F9)
    # "7 Data urodzenia" at y=196.0
    cover_label(draw, 70, 194, 95, 13, '7 Data de nascimento', F9)

    # Date sub-labels for father birth at y=202.4; pai_nasc sp=17.27
    date_sublabels(draw, 202, 153.60, 17.27)

    # "8 Miejsce urodzenia" y=220.0 + "(państwo/miejscowość)" y=228.0
    cover_label2(draw, 70, 218, 135, 22, '8 Local de nascimento', '(país/localidade)', F9)
    # "9 Stan cywilny" at y=244.0
    cover_label(draw, 70, 242, 95, 13, '9 Estado civil', F9)
    # "10 Data zawarcia związku" y=260.0 + "małżeńskiego" y=268.1
    cover_label2(draw, 70, 258, 130, 22, '10 Data de casamento', '', F9)

    # Marriage date sub-labels at y=266.5; pai_cas sp=17.27
    date_sublabels(draw, 266, 153.60, 17.27)

    # "11 Miejsce zawarcia" y=284.0 + "związku małżeńskiego" y=292.1 + "(państwo/...)" y=300.0
    cover_label2(draw, 70, 282, 135, 30, '11 Local do casamento', '(país/localidade)', F9)

    # "12 Obywatelstwa posiadane..." y=316.1-340.1 (4 lines)
    cover_label2(draw, 70, 314, 130, 32,
                 '12 Cidadanias na data de nascimento', 'da pessoa do pedido', F9)

    # "13 Nr PESEL (jeżeli" y=356.0 + "został nadany" y=364.1
    cover_label2(draw, 70, 354, 95, 24, '13 Nr PESEL', '(se atribuído)', F9)

    # "F. Dane osobowe dalszych wstępnych..." at y=391.9
    cover_label(draw, 70, 389, 475, 18,
                'F. Dados pessoais dos antepassados da pessoa a quem se refere o pedido.', FB10)

    # "I. Dane dotyczące dziadka ze strony matki." at y=410.9
    cover_label(draw, 70, 408, 295, 18, 'I. Dados referentes ao avô materno.', FB10)

    # Maternal grandfather fields
    # "1 Nazwisko" at y=434.1
    cover_label(draw, 70, 432, 95, 13, '1 Sobrenome', F9)
    # "2 Nazwisko rodowe" at y=466.1
    cover_label(draw, 70, 464, 120, 13, '2 Sobrenome de solteiro', F9)
    # "3 Imię (imiona)" at y=482.1
    cover_label(draw, 70, 480, 95, 13, '3 Nome(s)', F9)
    # "4 Imię i nazwisko ojca" at y=498.2
    cover_label(draw, 70, 496, 130, 13, '4 Nome e sobrenome do pai', F9)
    # "5 Imię i nazwisko rodowe" y=514.1 + "matki" y=522.2
    cover_label2(draw, 70, 512, 95, 22, '5 Nome e sobrenome da mãe', '', F9)
    # "6 Data urodzenia" at y=538.1
    cover_label(draw, 70, 536, 95, 13, '6 Data de nascimento', F9)

    # Date sub-labels at y=544.6; avo_mat_nasc sp=17.27
    date_sublabels(draw, 544, 153.60, 17.27)

    # "7 Miejsce urodzenia" y=562.2 + "(państwo/miejscowość)" y=570.2
    cover_label2(draw, 70, 560, 135, 22, '7 Local de nascimento', '(país/localidade)', F9)
    # "8 Nr PESEL (jeżeli" y=586.2 + "został nadany" y=594.2
    cover_label2(draw, 70, 584, 95, 24, '8 Nr PESEL', '(se atribuído)', F9)

    # "II. Dane dotyczące babki ze strony matki." at y=625.0
    cover_label(draw, 70, 623, 295, 18, 'II. Dados referentes à avó materna.', FB10)

    # Maternal grandmother fields
    # "1 Nazwisko" at y=648.2
    cover_label(draw, 70, 646, 95, 13, '1 Sobrenome', F9)
    # "2 Nazwisko rodowe" at y=680.3
    cover_label(draw, 70, 678, 120, 13, '2 Sobrenome de solteira', F9)
    # "3 Imię (imiona)" at y=696.2
    cover_label(draw, 70, 694, 95, 13, '3 Nome(s)', F9)
    # "4 Imię i nazwisko ojca" at y=712.2
    cover_label(draw, 70, 710, 130, 13, '4 Nome e sobrenome do pai', F9)


# ── PAGE 4 (page_5.png) - Maternal grandmother cont. + Paternal grandparents ─
def process_page_4(draw):
    # Maternal grandmother cont.
    # "5 Imię i nazwisko rodowe" y=108.6 + "matki" y=116.7
    cover_label2(draw, 70, 106, 95, 22, '5 Nome e sobrenome da mãe', '', F9)
    # "6 Data urodzenia" at y=132.7
    cover_label(draw, 70, 130, 95, 13, '6 Data de nascimento', F9)

    # Date sub-labels at y=139.1; ava_mat_nasc sp=17.27
    date_sublabels(draw, 139, 153.60, 17.27)

    # "7 Miejsce urodzenia" y=156.7 + "(państwo/miejscowość)" y=164.7
    cover_label2(draw, 70, 154, 135, 22, '7 Local de nascimento', '(país/localidade)', F9)
    # "8 Nr PESEL (jeżeli" y=180.7 + "został nadany" y=188.7
    cover_label2(draw, 70, 178, 95, 24, '8 Nr PESEL', '(se atribuído)', F9)

    # "III. Dane dotyczące dziadka ze strony ojca." at y=208.6
    cover_label(draw, 70, 206, 310, 18, 'III. Dados referentes ao avô paterno.', FB10)

    # Paternal grandfather fields
    # "1 Nazwisko" at y=231.7
    cover_label(draw, 70, 229, 95, 13, '1 Sobrenome', F9)
    # "2 Nazwisko rodowe" at y=263.8
    cover_label(draw, 70, 261, 120, 13, '2 Sobrenome de solteiro', F9)
    # "3 Imię (imiona)" at y=279.7
    cover_label(draw, 70, 277, 95, 13, '3 Nome(s)', F9)
    # "4 Imię i nazwisko ojca" at y=295.7
    cover_label(draw, 70, 293, 130, 13, '4 Nome e sobrenome do pai', F9)
    # "5 Imię i nazwisko rodowe" y=311.8 + "matki" y=319.7
    cover_label2(draw, 70, 309, 95, 22, '5 Nome e sobrenome da mãe', '', F9)
    # "6 Data urodzenia" at y=335.8
    cover_label(draw, 70, 333, 95, 13, '6 Data de nascimento', F9)

    # Date sub-labels at y=342.2; avo_pat_nasc sp=17.26
    date_sublabels(draw, 342, 153.60, 17.26)

    # "7 Miejsce urodzenia" y=359.8 + "(państwo/miejscowość)" y=367.7
    cover_label2(draw, 70, 357, 135, 22, '7 Local de nascimento', '(país/localidade)', F9)
    # "8 Nr PESEL (jeżeli" y=383.8 + "został nadany" y=391.7
    cover_label2(draw, 70, 381, 95, 24, '8 Nr PESEL', '(se atribuído)', F9)

    # "IV. Dane dotyczące babki ze strony ojca." at y=411.6
    cover_label(draw, 70, 409, 310, 18, 'IV. Dados referentes à avó paterna.', FB10)

    # Paternal grandmother fields
    # "1 Nazwisko" at y=434.8
    cover_label(draw, 70, 432, 95, 13, '1 Sobrenome', F9)
    # "2 Nazwisko rodowe" at y=466.8
    cover_label(draw, 70, 464, 120, 13, '2 Sobrenome de solteira', F9)
    # "3 Imię (imiona)" at y=482.8
    cover_label(draw, 70, 480, 95, 13, '3 Nome(s)', F9)
    # "4 Imię i nazwisko ojca" at y=498.9
    cover_label(draw, 70, 496, 130, 13, '4 Nome e sobrenome do pai', F9)
    # "5 Imię i nazwisko rodowe" y=514.9 + "matki" y=522.9
    cover_label2(draw, 70, 512, 95, 22, '5 Nome e sobrenome da mãe', '', F9)
    # "6 Data urodzenia" at y=538.9
    cover_label(draw, 70, 536, 95, 13, '6 Data de nascimento', F9)

    # Date sub-labels at y=545.4; ava_pat_nasc sp=17.27
    date_sublabels(draw, 545, 153.60, 17.27)

    # "7 Miejsce urodzenia" y=562.9 + "(państwo/miejscowość)" y=570.9
    cover_label2(draw, 70, 560, 135, 22, '7 Local de nascimento', '(país/localidade)', F9)
    # "8 Nr PESEL (jeżeli" y=586.9 + "został nadany" y=594.9
    cover_label2(draw, 70, 584, 95, 24, '8 Nr PESEL', '(se atribuído)', F9)

    # Bottom notice: "JEŻELI WNIOSKODAWCA..." at y=614.7
    cover_label(draw, 70, 612, 475, 18,
                'SE O REQUERENTE JUNTAR AO PEDIDO UMA CÓPIA:', FB10)
    cover_label(draw, 70, 629, 475, 18,
                '– do documento de identidade polonês da pessoa a quem se refere o pedido, OU', F9)
    # "LUB" (OR) at y=641.9, x=101.4 — cover and replace with "OU"
    cover_label(draw, 95, 640, 52, 17, 'OU', F9)
    cover_label(draw, 70, 656, 475, 18,
                '– do passaporte polonês da pessoa a quem se refere o pedido, OU', F9)
    cover_label2(draw, 70, 672, 475, 32,
                 '– da decisão do voivoda confirmando a posse de cidadania polonesa pela pessoa',
                 '  a quem se refere o pedido - NÃO É NECESSÁRIO PREENCHER A PARTE II NEM A III.', F9)
    cover_label(draw, 70, 699, 475, 16,
                'NÃO PREENCHE A PARTE II NEM A PARTE III DO PEDIDO.', FB10)


# ── Narrative pages (5-10) ────────────────────────────────────────────────────
def process_page_narrative(draw, page_idx):
    titles = {
        5:  'PARTE II - Biografia do requerente',
        6:  'PARTE II - Biografia da mãe',
        7:  'PARTE II - Biografia do avô e avó maternos',
        8:  'PARTE II - Biografia do avô e avó paternos',
        9:  'PARTE III - Decisões, documentos e informações adicionais',
        10: 'PARTE IV - Lista de anexos',
    }
    title = titles.get(page_idx, f'PARTE - Página {page_idx + 1}')
    cover_label(draw, 70, 95, 460, 22, title, FB12)


# ── main ──────────────────────────────────────────────────────────────────────
PROCESSORS = {
    0: process_page_0,
    1: process_page_1,
    2: process_page_2,
    3: process_page_3,
    4: process_page_4,
}

def process_all():
    for i in range(11):
        src_path  = SRC  / f'page_{i+1}.png'
        dest_path = DEST / f'page_{i+1}.png'

        if not src_path.exists():
            print(f'  [skip] {src_path} not found')
            continue

        img  = Image.open(src_path).convert('RGB')
        draw = ImageDraw.Draw(img)

        if i in PROCESSORS:
            PROCESSORS[i](draw)
        elif 5 <= i <= 10:
            process_page_narrative(draw, i)

        img.save(dest_path, 'PNG')
        print(f'  [ok] page_{i+1}.png')

    print(f'[make_pt_pages] Done -> {DEST}')


if __name__ == '__main__':
    process_all()
