"""Genera le due guide PDF dell'area riservata di Scrittore Site (italiano e inglese).

Uso (dalla cartella del progetto):
    python tools/guide/genera_guide.py

I testi sono in tools/guide/contenuti.py; i PDF vengono scritti in assets/ con
gli stessi nomi offerti dalla home. Richiede reportlab e i font Liberation Sans.

Stile ripreso dalle guide originali: copertina con logo, titoli blu notte,
sottotitoli azzurri, tabelle con intestazione scura e righe alterne azzurre,
piè di pagina con numero.
"""
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

CARTELLA = Path(__file__).resolve().parent
RADICE = CARTELLA.parents[1]
sys.path.insert(0, str(CARTELLA))
from contenuti import GUIDE  # noqa: E402

LOGO = RADICE / "assets" / "scrittore-site-logo.png"
USCITE = {
    "Italiano": RADICE / "assets" / "scrittore-site-guida-area-riservata-italiano.pdf",
    "English": RADICE / "assets" / "scrittore-site-private-area-guide-english.pdf",
}

pdfmetrics.registerFont(TTFont("Sans", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Italic", "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Sans-BoldItalic", "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-Bold", italic="Sans-Italic", boldItalic="Sans-BoldItalic")

NAVY = colors.HexColor("#08233b")
TESTO = colors.HexColor("#203448")
AZZURRO = colors.HexColor("#147fc0")
VERDE = colors.HexColor("#057b78")
GRIGIO = colors.HexColor("#567086")
CHIARO = colors.HexColor("#eaf6fd")
BORDO = colors.HexColor("#c9dfec")

S = {
    "titolo": ParagraphStyle("titolo", fontName="Sans-Bold", fontSize=26, leading=31, textColor=NAVY, alignment=TA_CENTER),
    "sottotitolo": ParagraphStyle("sottotitolo", fontName="Sans", fontSize=11.5, leading=15, textColor=GRIGIO, alignment=TA_CENTER),
    "nota": ParagraphStyle("nota", fontName="Sans", fontSize=10, leading=15, textColor=TESTO, alignment=TA_CENTER),
    "marchio": ParagraphStyle("marchio", fontName="Sans-Bold", fontSize=15, leading=19, textColor=VERDE, alignment=TA_CENTER),
    "marchio2": ParagraphStyle("marchio2", fontName="Sans", fontSize=9.5, leading=12, textColor=GRIGIO, alignment=TA_CENTER),
    "h1": ParagraphStyle("h1", fontName="Sans-Bold", fontSize=20, leading=25, textColor=NAVY, spaceAfter=8),
    "intro": ParagraphStyle("intro", fontName="Sans", fontSize=10, leading=14.5, textColor=TESTO, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName="Sans-Bold", fontSize=13, leading=17, textColor=AZZURRO, spaceBefore=8, spaceAfter=6),
    "punto": ParagraphStyle("punto", fontName="Sans", fontSize=9.8, leading=14, textColor=TESTO, spaceAfter=5),
    "cella": ParagraphStyle("cella", fontName="Sans", fontSize=8.6, leading=11.2, textColor=TESTO),
    "cella_testa": ParagraphStyle("cella_testa", fontName="Sans-Bold", fontSize=8.6, leading=11.2, textColor=colors.white),
    "novita": ParagraphStyle("novita", fontName="Sans", fontSize=9.6, leading=13.5, textColor=TESTO),
}

LARGHEZZA = A4[0] - 2 * 18 * mm


def tabella(intestazioni, righe, proporzioni):
    dati = [[Paragraph(t, S["cella_testa"]) for t in intestazioni]]
    dati += [[Paragraph(c, S["cella"]) for c in riga] for riga in righe]
    larghezze = [LARGHEZZA * p for p in proporzioni]
    t = Table(dati, colWidths=larghezze, repeatRows=1)
    stile = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, BORDO),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDO),
    ]
    for i in range(1, len(dati)):
        if i % 2 == 0:
            stile.append(("BACKGROUND", (0, i), (-1, i), CHIARO))
    t.setStyle(TableStyle(stile))
    return t


def riquadro(testo, stile="nota"):
    t = Table([[Paragraph(testo, S[stile])]], colWidths=[LARGHEZZA * 0.92])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CHIARO),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDO),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))
    return t


def genera(lingua, percorso):
    g = GUIDE[lingua]

    def piede(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(BORDO)
        canvas.setLineWidth(0.6)
        canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
        canvas.setFont("Sans", 8)
        canvas.setFillColor(GRIGIO)
        canvas.drawString(18 * mm, 10 * mm, f"Scrittore Site · {g['versione']}")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(percorso), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=22 * mm,
        title=g["titolo"], author="Scrittore Site", subject=g["sottotitolo"],
    )
    storia = [Spacer(1, 30 * mm), Image(str(LOGO), width=46 * mm, height=46 * mm * 1232 / 1277),
              Spacer(1, 10 * mm), Paragraph(g["titolo"], S["titolo"]), Spacer(1, 4 * mm),
              Paragraph(g["sottotitolo"], S["sottotitolo"]), Spacer(1, 10 * mm), riquadro(g["nota_copertina"]),
              Spacer(1, 8 * mm), riquadro(g["novita"], "novita"), Spacer(1, 10 * mm),
              Paragraph("Scrittore Site", S["marchio"]), Paragraph(g["area"], S["marchio2"]), PageBreak()]
    for numero, capitolo in enumerate(g["capitoli"], 1):
        blocco = [Paragraph(f"{numero} {capitolo['titolo']}", S["h1"]), Paragraph(capitolo["intro"], S["intro"])]
        for elemento in capitolo["blocchi"]:
            tipo = elemento[0]
            if tipo == "h2":
                blocco.append(Paragraph(elemento[1], S["h2"]))
            elif tipo == "punti":
                blocco.extend(Paragraph(f"• {p}", S["punto"]) for p in elemento[1])
            elif tipo == "tabella":
                blocco.append(tabella(elemento[1], elemento[2], elemento[3]))
                blocco.append(Spacer(1, 4 * mm))
        storia.append(KeepTogether(blocco[:2]))
        storia.extend(blocco[2:])
        storia.append(PageBreak())
    storia.pop()
    doc.build(storia, onFirstPage=piede, onLaterPages=piede)


if __name__ == "__main__":
    for lingua, percorso in USCITE.items():
        genera(lingua, percorso)
        print(f"{lingua}: {percorso}")
