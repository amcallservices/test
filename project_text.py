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


_PREFISSI_PREAMBOLO = re.compile(
    r"(?i)^\s*(?:ecco|certamente|certo|sicuramente|ok|okay|here\s+is|here's|sure)\b"
)
_PAROLE_META = re.compile(
    r"(?i)\b(?:sezione|capitolo|sottocapitolo|prefazione|testo|richiest\w*|"
    r"section|chapter|text|requested)\b"
)


def rimuovi_preambolo_ai(testo) -> str:
    """Toglie solo una frase di cortesia iniziale del modello, mai il libro.

    Viene esaminata unicamente la prima riga non vuota. È rimossa se inizia
    con una formula tipica ("Ecco", "Certamente", "Ok"...) e inoltre termina
    con i due punti, è una conferma brevissima ("Certamente!") oppure parla
    del testo stesso ("Ecco la sezione richiesta."). Dialoghi e frasi
    narrative come "Ecco perché nessuno era tornato." restano intatti.
    """
    righe = str(testo or "").split("\n")
    indice = next((i for i, riga in enumerate(righe) if riga.strip()), None)
    if indice is None:
        return ""
    prima = righe[indice].strip()
    if _PREFISSI_PREAMBOLO.match(prima):
        conferma_breve = len(prima.split()) <= 3 and prima[-1:] in "!.:"
        meta = bool(_PAROLE_META.search(prima)) and len(prima.split()) <= 14
        if prima.endswith(":") or conferma_breve or meta:
            del righe[indice]
    return "\n".join(righe).strip()


def estratto_finale(testo, limite: int = 900) -> str:
    """Restituisce la parte conclusiva di un testo, partendo da una frase intera.

    Per continuare una storia serve sapere come finisce la sezione precedente,
    non come comincia.
    """
    pulito = str(testo or "").strip()
    if len(pulito) <= limite:
        return pulito
    coda = pulito[-limite:]
    inizio_frase = re.search(r"(?<=[.!?…»”])\s+", coda)
    if inizio_frase and inizio_frase.end() < len(coda) // 2:
        coda = coda[inizio_frase.end():]
    else:
        spazio = coda.find(" ")
        coda = coda[spazio + 1:] if 0 <= spazio < 40 else coda
    return "…" + coda.strip()
