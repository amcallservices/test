"""Pulizia e suddivisione del testo, indipendenti dall'interfaccia.

Queste trasformazioni non scrivono nel progetto e non cambiano il contenuto
editoriale: rimuovono solo segnali tecnici non destinati al manoscritto.
"""

from __future__ import annotations

import re


def pulisci_testo_editoriale(testo) -> str:
    """Rimuove Markdown, URL e riferimenti tecnici da anteprima ed export."""
    if not testo:
        return ""
    testo = str(testo)
    testo = re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", testo)
    testo = testo.replace("**", "").replace("__", "")
    testo = re.sub(r"(?m)^\s*>\s?", "", testo)
    testo = re.sub(
        r"(?is)(?:^|\n)\s{0,3}(?:#+\s*)?(?:fonti verificate|fonti consultate|riferimenti bibliografici|sources|references)\s*:?.*$",
        "",
        testo,
    )
    testo = re.sub(r"\[([^\]]+)\]\(https?://[^)]+\)", r"\1", testo)
    testo = re.sub(r"https?://[^\s)\]>]+", "", testo)
    testo = re.sub(
        r"\s*\([^\n()]{0,180}(?:\b[a-z0-9-]+\.)+(?:com|org|net|gov|edu|io|co\.uk|it|fr|de|es|ai|info|biz|co)[^\n()]*\)",
        "",
        testo,
        flags=re.I,
    )
    testo = re.sub(
        r"(?im)^\s*\[?(?:informazione|fatto|esempio|fonte)[^\n]{0,120}(?:da verificare|verificato|ipotetico|di carattere generale)[^\n]*\]?\s*$",
        "",
        testo,
    )
    testo = re.sub(r"(?m)^\s*[-_*]{3,}\s*$", "", testo)
    return re.sub(r"\n{3,}", "\n\n", testo).strip()


def dividi_blocchi_lettura(testo, limite: int = 480) -> list[str]:
    """Divide il testo per il lettore browser, senza spezzare frasi inutilmente."""
    normalizzato = re.sub(r"\s+", " ", str(testo or "")).strip()
    if not normalizzato:
        return []
    frasi = re.findall(r"[^.!?…]+[.!?…]+|[^.!?…]+$", normalizzato) or [normalizzato]
    blocchi: list[str] = []
    corrente = ""
    for frase in frasi:
        candidata = (corrente + " " + frase).strip()
        if len(candidata) > limite and corrente:
            blocchi.append(corrente)
            corrente = frase.strip()
        else:
            corrente = candidata
    if corrente:
        blocchi.append(corrente)
    return blocchi
