"""Regole editoriali pure di Scrittore Site.

Questo modulo non contiene interfaccia Streamlit né chiamate AI: raccoglie le
regole riutilizzabili per lunghezza, riconoscimento delle sezioni e controlli
tecnici dei testi. Tenerle qui riduce il rischio che un intervento sul layout
modifichi involontariamente la qualità editoriale.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Callable, Iterable, Mapping
from typing import Any


PROFILI_LUNGHEZZA_STESURA = {
    "Compatto": {
        "parole": "480-560 parole",
        "min_parole": 480,
        "max_parole": 560,
        "max_completion_tokens": 1325,
        "descrizione": "testo essenziale ma completo, pensato per almeno 100 pagine",
        "max_sezioni": 50,
        "pagine_minime": 100,
    },
    "Standard KDP": {
        "parole": "620-700 parole",
        "min_parole": 620,
        "max_parole": 700,
        "max_completion_tokens": 1675,
        "descrizione": "trattazione equilibrata, pensata per almeno 200 pagine",
        "max_sezioni": 80,
        "pagine_minime": 200,
    },
    "Approfondito": {
        "parole": "700-800 parole",
        "min_parole": 700,
        "max_parole": 800,
        "max_completion_tokens": 1900,
        "descrizione": "trattazione ampia e approfondita, pensata per almeno 300 pagine",
        "max_sezioni": 110,
        "pagine_minime": 300,
    },
}


def vincolo_parole_con_tolleranza(profilo_lunghezza: str) -> tuple[int, int]:
    """Restituisce i limiti editoriali con la tolleranza massima del 5%."""
    profilo = PROFILI_LUNGHEZZA_STESURA.get(
        profilo_lunghezza, PROFILI_LUNGHEZZA_STESURA["Standard KDP"]
    )
    return math.ceil(profilo["min_parole"] * 0.95), math.floor(profilo["max_parole"] * 1.05)


def classifica_sezione(sezione: str, is_prefazione: Callable[[str], bool]) -> str:
    """Classifica una voce dell'indice senza dipendere dalla lingua dell'app."""
    pulita = str(sezione or "").strip()
    if is_prefazione(pulita):
        return "prefazione"
    if re.match(r"(?i)^(parte|part|partie|teil|partea|часть|الجزء|部分)\b", pulita):
        return "parte"
    if re.match(r"(?i)^(capitolo|chapter|kapitel|capítulo|chapitre|capitolul|глава|الفصل|章节)\s+\d+", pulita):
        return "capitolo"
    if re.match(r"^\d+\.\d+\s+", pulita):
        return "sottocapitolo"
    return "frontespizio"


def chiave_sezione(sezione: str) -> str:
    """Identificativo stabile: 1.1 e 11 non possono collidere."""
    digest = hashlib.sha256(str(sezione).encode("utf-8")).hexdigest()[:20]
    return f"txt_{digest}"


def chiave_sezione_precedente(sezione: str) -> str:
    """Compatibilità per testi creati prima delle chiavi univoche."""
    return f"txt_{str(sezione).replace(' ', '_').replace('.', '')}"


def minimo_parole_per_sezione_editoriale(
    sezione: str, genere: str, classificatore: Callable[[str], str]
) -> int:
    """Soglia unica usata da tutti i controlli prima dell'esportazione."""
    minimi = {
        "prefazione": 100,
        "parte": 35,
        "capitolo": 90 if genere == "Ricettario" else 120,
        "sottocapitolo": 120,
        "frontespizio": 40,
    }
    return minimi.get(classificatore(sezione), 40)


def motivo_chiusura_tecnica(testo: str) -> str:
    """Restituisce il motivo di un finale palesemente incompleto."""
    parole_sospese = {
        "a", "ad", "al", "alla", "alle", "allo", "che", "con", "da", "dal", "dalla",
        "delle", "dello", "di", "ed", "e", "fra", "gli", "il", "in", "la", "le", "lo",
        "nel", "nella", "nelle", "nello", "o", "per", "sul", "sulla", "sulle", "sullo",
        "tra", "un", "una", "uno", "with", "and", "or", "of", "to", "for", "the",
    }
    finale = str(testo or "").rstrip(" \t\r\n\"'»”)]}")
    ultima_riga = next((r.strip() for r in reversed(str(testo or "").splitlines()) if r.strip()), "")
    ultima_parola = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", finale.lower())
    elenco_sintetico = bool(re.match(r"^(?:[-•*]|\d+[.)])\s*", ultima_riga))
    if finale.endswith((",", ";", ":", "—", "–", "-", "…")):
        return "il testo termina con una punteggiatura sospesa"
    if not elenco_sintetico and (not finale or finale[-1] not in ".!?"):
        return "l'ultima frase non risulta chiusa"
    if ultima_parola and ultima_parola[-1] in parole_sospese:
        return "l'ultima frase sembra terminare con una parola di collegamento"
    return ""


def stati_sezioni_editoriali(
    sezioni: Iterable[str],
    genere: str,
    contenuti: Mapping[str, Any],
    leggi_sezione: Callable[[str], str],
    pulisci_testo: Callable[[str], str],
    classificatore: Callable[[str], str],
) -> list[dict[str, str]]:
    """Distingue sezioni mancanti, deboli e complete usando una fonte stabile."""
    risultati = []
    for sezione in sezioni:
        testo = contenuti.get(sezione) or leggi_sezione(sezione)
        testo = pulisci_testo(testo).strip()
        minimo = minimo_parole_per_sezione_editoriale(sezione, genere, classificatore)
        parole = len(testo.split())
        if not testo:
            stato, motivo = "MANCANTE", "nessun contenuto generato"
        elif testo.startswith("ERRORE:") or parole < minimo:
            stato, motivo = "DEBOLE", f"{parole} parole: servono almeno {minimo} parole"
        elif motivo_chiusura_tecnica(testo):
            stato, motivo = "DEBOLE", motivo_chiusura_tecnica(testo)
        else:
            stato, motivo = "COMPLETA", f"{parole} parole"
        risultati.append({"Sezione": sezione, "Stato": stato, "Dettaglio": motivo})
    return risultati


def controllo_completezza_testi_gratuito(
    sezioni: Iterable[str],
    contenuti: Mapping[str, Any],
    leggi_sezione: Callable[[str], str],
    pulisci_testo: Callable[[str], str],
) -> list[dict[str, str]]:
    """Controllo locale: individua assenze o interruzioni senza chiamare l'AI."""
    risultati = []
    for sezione in sezioni:
        testo = pulisci_testo(contenuti.get(sezione) or leggi_sezione(sezione)).strip()
        if not testo:
            stato, dettaglio = "MANCANTE", "nessun testo presente"
        elif testo.startswith("ERRORE:"):
            stato, dettaglio = "DA RIVEDERE", "la generazione precedente ha restituito un errore"
        elif len(testo.split()) < 12:
            stato, dettaglio = "TROPPO BREVE", "meno di 12 parole: verifica che la sezione sia stata realmente completata"
        elif motivo_chiusura_tecnica(testo):
            stato, dettaglio = "INTERROTTA", motivo_chiusura_tecnica(testo)
        else:
            stato, dettaglio = "COMPLETA", f"{len(testo.split())} parole — nessuna interruzione tecnica rilevata"
        risultati.append({"Sezione": sezione, "Esito": stato, "Dettaglio": dettaglio})
    return risultati
