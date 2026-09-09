"""Controlli editoriali locali e riutilizzabili di Scrittore Site.

Questo modulo non conosce Streamlit, crediti o provider AI. Contiene soltanto
calcoli deterministici: può quindi essere provato in isolamento e non può
alterare il manoscritto dell'utente.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import re
from collections.abc import Callable, Mapping
from typing import Any


def analizza_qualita_prosa(testo: str) -> str:
    """Restituisce un linter locale su lessico, ritmo e ripetizioni."""
    if not testo or len(testo) < 50:
        return "⚠️ Testo troppo breve per un'analisi sintattica significativa."

    risultati = ["📊 **REPORT LINTER AVANZATO E ANALISI SINTATTICA**\n"]
    parole = re.findall(r"\b\w+\b", testo.lower())
    frasi = [frase.strip() for frase in re.split(r"[.!?]+", testo) if len(frase.strip()) > 5]
    totale_parole = len(parole)
    totale_frasi = len(frasi) or 1

    diversita = (len(set(parole)) / totale_parole) * 100 if totale_parole else 0
    if diversita < 35:
        risultati.append(
            f"⚠️ **Vocabolario Ripetitivo**: Indice di diversità lessicale basso ({diversita:.1f}%). "
            "Valuta di usare più sinonimi."
        )
    else:
        risultati.append(
            f"✅ **Ricchezza Lessicale**: Ottima diversità ({diversita:.1f}%). Il testo risulta stimolante."
        )

    parole_per_frase = totale_parole / totale_frasi
    if parole_per_frase > 30:
        risultati.append(
            f"⚠️ **Sintassi Pesante**: Le frasi sono troppo lunghe (media {parole_per_frase:.1f} parole/frase). "
            "Rischio di affaticamento cognitivo: spezza i periodi."
        )
    elif parole_per_frase < 8:
        risultati.append(
            f"⚠️ **Ritmo Frammentato**: Frasi molto brevi (media {parole_per_frase:.1f} parole/frase). "
            "Il testo potrebbe risultare troppo robotico o telegrafico."
        )
    else:
        risultati.append(
            f"✅ **Ritmo e Leggibilità**: Lunghezza frasi perfettamente bilanciata "
            f"(media {parole_per_frase:.1f} parole/frase)."
        )

    ripetizioni = []
    for indice in range(len(parole) - 15):
        parola = parole[indice]
        if len(parola) > 4 and parola in parole[indice + 1:indice + 15]:
            ripetizioni.append(parola)
    if ripetizioni:
        comuni = [voce[0] for voce in Counter(ripetizioni).most_common(5)]
        risultati.append(
            "🔍 **Allerta Ripetizioni Ravvicinate**: Le seguenti parole si ripetono troppo vicine tra loro: "
            f"*{', '.join(comuni)}*"
        )
    else:
        risultati.append("✅ **Fluidità Testuale**: Nessuna ripetizione fastidiosa o eco ravvicinata rilevata.")
    return "\n\n".join(risultati)


def blocchi_per_audit_manoscritto(
    contenuti: Mapping[str, Any],
    pulisci_testo: Callable[[Any], str],
    limite_caratteri: int = 18_000,
) -> list[str]:
    """Divide un manoscritto in blocchi consecutivi senza perdere parti centrali."""
    blocchi: list[str] = []
    corrente = ""
    for sezione, contenuto in contenuti.items():
        testo = pulisci_testo(contenuto).strip()
        if not testo:
            continue
        unita = f"SEZIONE: {sezione}\nTESTO:\n{testo}\n\n"
        while unita:
            spazio = limite_caratteri - len(corrente)
            if spazio <= 300:
                blocchi.append(corrente)
                corrente, spazio = "", limite_caratteri
            if len(unita) <= spazio:
                corrente += unita
                unita = ""
            else:
                punto_taglio = unita.rfind("\n", 0, spazio)
                if punto_taglio < max(500, spazio // 2):
                    punto_taglio = spazio
                corrente += unita[:punto_taglio]
                blocchi.append(corrente)
                corrente, unita = "", unita[punto_taglio:]
    if corrente.strip():
        blocchi.append(corrente)
    return blocchi


def firma_controllo_conformita_kdp(
    contenuti: Mapping[str, Any], titolo: str, genere: str, argomento: str, lingua: str
) -> str:
    """Identifica con certezza la versione sottoposta al controllo KDP."""
    parti = [titolo, genere, argomento, lingua]
    parti.extend(f"{sezione}\n{contenuto}" for sezione, contenuto in contenuti.items())
    return hashlib.sha256("\n␞\n".join(str(parte or "") for parte in parti).encode("utf-8")).hexdigest()


def mappa_capitoli_e_sottocapitoli(indice: str) -> str:
    """Mappa ogni sottocapitolo al suo capitolo padre, per report azionabili."""
    capitolo_corrente = ""
    righe_mappa = []
    pattern_capitolo = re.compile(
        r"(?i)^(?:capitolo|chapter|kapitel|cap[ií]tulo|chapitre|capitolul|глава|الفصل|章节)\s+\d+.*"
    )
    pattern_sottocapitolo = re.compile(r"^\d+\.\d+(?:\.\d+)?\s+.+")
    for riga in (indice or "").splitlines():
        voce = riga.strip()
        if not voce:
            continue
        if pattern_capitolo.match(voce):
            capitolo_corrente = voce
        elif pattern_sottocapitolo.match(voce) and capitolo_corrente:
            righe_mappa.append(f"{voce}  →  {capitolo_corrente}")
    return "\n".join(righe_mappa) or "Nessun sottocapitolo mappabile nell'indice."
