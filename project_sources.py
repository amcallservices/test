"""Utilità pure per fonti caricate e fonti web di Scrittore Site.

Nessuna funzione qui avvia ricerche, chiama l'AI o scrive nella sessione: sono
trasformazioni verificabili dei dati ricevuti dall'interfaccia.
"""

from __future__ import annotations

import hashlib
import re


def firma_fonti_esterne(caricati) -> str:
    """Crea un'impronta dei file caricati senza doverli rileggere."""
    digest = hashlib.sha256()
    for file in caricati or []:
        contenuto = file.getvalue()
        digest.update(file.name.encode("utf-8", "ignore"))
        digest.update(str(len(contenuto)).encode("ascii"))
        digest.update(hashlib.sha256(contenuto).digest())
    return digest.hexdigest()


def crea_scheda_fonti(testo: str, limite: int = 2600) -> str:
    """Crea una breve scheda locale, senza chiamate supplementari."""
    paragrafi = [
        re.sub(r"\s+", " ", paragrafo).strip()
        for paragrafo in re.split(r"\n\s*\n|(?<=\.)\s{2,}", testo or "")
    ]
    paragrafi = [paragrafo for paragrafo in paragrafi if len(paragrafo) > 80]
    scelti: list[str] = []
    usati = 0
    for paragrafo in paragrafi:
        if usati + len(paragrafo) > limite:
            break
        scelti.append(paragrafo)
        usati += len(paragrafo)
    return "\n".join(scelti) or (testo or "")[:limite]


def firma_ricerca_preliminare(
    titolo: str, genere: str, trama: str, obiettivo: str, lingua: str, approfondimenti: str
) -> str:
    """Rende riutilizzabile una ricerca finché il brief resta uguale."""
    base = "\n".join([titolo or "", genere or "", trama or "", obiettivo or "", lingua or "", approfondimenti or ""])
    return hashlib.sha256(base.encode("utf-8", "ignore")).hexdigest()


def separa_mappa_e_registro_fonti_web(testo: str) -> tuple[str, str]:
    """Separa la mappa interna dal registro di collegamenti mostrabile."""
    testo = (testo or "").strip()
    marcatore = re.search(
        r"(?im)^\s*(?:#{1,6}\s*)?REGISTRO\s+(?:DELLE\s+)?FONTI(?:\s+WEB)?\s*:?[ \t]*$",
        testo,
    )
    if marcatore:
        return testo[:marcatore.start()].strip(), testo[marcatore.end():].strip()

    righe = testo.splitlines()
    righe_fonti = [riga for riga in righe if re.search(r"https?://\S+", riga)]
    if righe_fonti:
        mappa = "\n".join(riga for riga in righe if riga not in righe_fonti).strip()
        return mappa or testo, "\n".join(righe_fonti).strip()
    return testo, ""


def conserva_solo_fonti_web_selezionate(registro: str, massimo_fonti: int = 5) -> str:
    """Conserva soltanto le fonti web effettivamente selezionate."""
    righe = [
        riga.strip() for riga in str(registro or "").splitlines()
        if re.search(r"https?://\S+", riga)
    ]
    return "\n".join(righe[:max(1, int(massimo_fonti))])
