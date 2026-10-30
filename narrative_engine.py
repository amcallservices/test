"""Memoria e controlli locali per la continuità narrativa.

Il modulo è deliberatamente privo di Streamlit e di chiamate API. Costruisce
una mappa compatta dai testi già approvati, la riusa nel prompt della sezione
successiva e segnala solo anomalie osservabili. In questo modo il costo della
stesura non cresce con il numero di capitoli.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


GENERI_NARRATIVI = frozenset({
    "Romanzo Rosa", "Thriller / Noir", "Fantasy", "Fantascienza", "Narrativo",
    "Romanzo Classico", "Contemporaneo", "Biografia",
})

FORMULE_DA_MONITORARE = (
    "come se", "sembrava", "non era soltanto", "per la prima volta",
    "rimase in silenzio", "abbassò lo sguardo", "strinse la mandibola",
)

EMOZIONI_RILEVABILI = (
    "paura", "felice", "felicità", "triste", "rabbia", "arrabbi", "ansia",
    "timore", "sollievo", "gelosia", "vergogna", "nostalgia", "amore",
)
OGGETTI_RILEVABILI = (
    "lettera", "chiave", "anello", "fotografia", "diario", "valigia", "telefono",
    "documento", "biglietto", "arma", "libro",
)

PAROLE_NON_PERSONAGGIO = frozenset({
    "Capitolo", "Parte", "Prefazione", "Epilogo", "Pagina", "Page", "Il", "Lo", "La",
    "I", "Gli", "Le", "Un", "Una", "Nel", "Nella", "In", "A", "Da", "Con", "Per",
    "Poi", "Quando", "Mentre", "Dopo", "Prima", "Quella", "Questo", "Questa", "Era",
    "Sono", "Non", "Ma", "Se", "Che", "Anche", "Solo", "Lui", "Lei", "Loro",
})


def genere_narrativo(genere: str) -> bool:
    valore = str(genere or "").strip()
    return valore in GENERI_NARRATIVI or "romanzo" in valore.casefold()


def _pulito(testo: Any) -> str:
    return re.sub(r"\s+", " ", str(testo or "")).strip()


def _frasi(testo: str) -> list[str]:
    return [frase.strip() for frase in re.split(r"(?<=[.!?…])\s+", _pulito(testo)) if frase.strip()]


def _estratto(testo: str, limite: int = 240) -> str:
    testo = _pulito(testo)
    if len(testo) <= limite:
        return testo
    taglio = testo.rfind(" ", 0, limite)
    return (testo[:taglio if taglio > 40 else limite].rstrip(" ,;:") + "…").strip()


def _nomi(testo: str) -> list[str]:
    candidati = re.findall(r"(?<![.!?]\s)\b[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]{2,}\b", testo)
    risultato: list[str] = []
    for nome in candidati:
        if nome not in PAROLE_NON_PERSONAGGIO and nome not in risultato:
            risultato.append(nome)
    return risultato[:12]


def _luoghi(testo: str) -> list[str]:
    # Raccoglie solo luoghi espressamente introdotti da una preposizione: è un
    # indizio, non una dichiarazione certa sulla posizione di un personaggio.
    pattern = r"\b(?:a|in|nel|nella|nei|nelle|verso|da|sul|sulla)\s+([A-ZÀ-ÖØ-Þ][\wÀ-ÖØ-öø-ÿ'’-]{2,}(?:\s+[A-ZÀ-ÖØ-Þ][\wÀ-ÖØ-öø-ÿ'’-]{2,})?)"
    trovati: list[str] = []
    for luogo in re.findall(pattern, testo):
        luogo = _pulito(luogo)
        if luogo not in trovati and luogo not in PAROLE_NON_PERSONAGGIO:
            trovati.append(luogo)
    return trovati[:8]


def _formule(testo: str) -> dict[str, int]:
    minuscolo = _pulito(testo).casefold()
    return {formula: minuscolo.count(formula) for formula in FORMULE_DA_MONITORARE if minuscolo.count(formula)}


def _fatti_osservabili(frasi: Sequence[str], nomi: Sequence[str]) -> tuple[list[str], list[str], list[str]]:
    """Estrae solo segnali testuali: non deduce età, rapporti o retroscena."""
    relazioni, stati, oggetti = [], [], []
    for frase in frasi:
        minuscolo = frase.casefold()
        nomi_nella_frase = [nome for nome in nomi if re.search(rf"\b{re.escape(nome)}\b", frase)]
        if len(nomi_nella_frase) >= 2:
            relazioni.append(_estratto(frase, 180))
        if any(emozione in minuscolo for emozione in EMOZIONI_RILEVABILI):
            stati.append(_estratto(frase, 180))
        for oggetto in OGGETTI_RILEVABILI:
            if re.search(rf"\b{re.escape(oggetto)}\b", minuscolo) and oggetto not in oggetti:
                oggetti.append(oggetto)
    return relazioni[:5], stati[:5], oggetti[:8]


def _firma_evento(testo: str) -> set[str]:
    parole = re.findall(r"[a-zà-öø-ÿ]{4,}", _pulito(testo).casefold())
    stop = {"questa", "quello", "della", "delle", "dello", "degli", "anche", "prima", "dopo", "senza", "quando", "mentre", "come", "sono", "non", "nella", "nelle", "dalla", "dalle", "dentro", "verso", "stato", "stata", "essere"}
    return {parola for parola in parole if parola not in stop}


def _similarita_evento(a: str, b: str) -> float:
    parole_a, parole_b = _firma_evento(a), _firma_evento(b)
    if not parole_a or not parole_b:
        return 0.0
    return len(parole_a & parole_b) / max(1, len(parole_a | parole_b))


def costruisci_memoria_narrativa(
    indice: str,
    contenuti: Mapping[str, Any],
    genere: str,
    precedente: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Costruisce una fotografia narrativa compatta dai contenuti approvati."""
    if not genere_narrativo(genere):
        return {"versione": 1, "attiva": False, "scene": {}, "personaggi": {}, "avvisi": []}

    ordine = [riga.strip() for riga in str(indice or "").splitlines() if riga.strip()]
    if not ordine:
        ordine = [str(sezione) for sezione in contenuti]
    scene: dict[str, dict[str, Any]] = {}
    personaggi: dict[str, dict[str, Any]] = {}
    luoghi_visitati: list[str] = []
    eventi: list[dict[str, str]] = []
    relazioni_confermate: list[dict[str, str]] = []
    stati_emotivi: list[dict[str, str]] = []
    oggetti_rilevanti: list[dict[str, Any]] = []
    for posizione, sezione in enumerate(ordine, 1):
        testo = _pulito(contenuti.get(sezione, ""))
        if not testo:
            continue
        frasi = _frasi(testo)
        nomi = _nomi(testo)
        luoghi = _luoghi(testo)
        relazioni, stati, oggetti = _fatti_osservabili(frasi, nomi)
        apertura = _estratto(" ".join(frasi[:2]), 260)
        chiusura = _estratto(" ".join(frasi[-2:]), 260)
        eventi_scena = [_estratto(frase, 200) for frase in frasi[-3:] if len(frase.split()) >= 6]
        scene[sezione] = {
            "ordine": posizione,
            "stato": "confermata",
            "personaggi_presenti": nomi,
            "luoghi_citati": luoghi,
            "apertura": apertura,
            "chiusura": chiusura,
            "eventi": eventi_scena[:3],
            "relazioni_osservate": relazioni,
            "stati_emotivi_osservati": stati,
            "oggetti_rilevanti": oggetti,
            "formule": _formule(testo),
        }
        for nome in nomi:
            scheda = personaggi.setdefault(nome, {"prima_apparizione": sezione, "ultima_apparizione": sezione, "presenze": 0})
            scheda["ultima_apparizione"] = sezione
            scheda["presenze"] = int(scheda.get("presenze", 0)) + 1
        for luogo in luoghi:
            if luogo not in luoghi_visitati:
                luoghi_visitati.append(luogo)
        if chiusura:
            eventi.append({"sezione": sezione, "esito": chiusura})
        relazioni_confermate.extend({"sezione": sezione, "fatto": relazione} for relazione in relazioni)
        stati_emotivi.extend({"sezione": sezione, "fatto": stato} for stato in stati)
        oggetti_rilevanti.extend({"sezione": sezione, "oggetti": oggetti} for _ in [0] if oggetti)

    # Manteniamo unicamente i fatti più recenti; le scene complete continuano
    # a essere indirizzabili per titolo, ma il prompt non cresce col libro.
    memoria = {
        "versione": 1,
        "attiva": True,
        "scene": scene,
        "personaggi": personaggi,
        "luoghi_visitati": luoghi_visitati[-15:],
        "eventi_confermati": eventi[-18:],
        "relazioni_confermate": relazioni_confermate[-12:],
        "stati_emotivi_confermati": stati_emotivi[-12:],
        "oggetti_rilevanti": oggetti_rilevanti[-12:],
        "cronologia": {"unita_confermate": len(scene), "ultima_sezione": next(reversed(scene), "")},
        "avvisi": [],
    }
    return memoria


def piano_scena(
    sezione: str,
    ordine: Sequence[str],
    memoria: Mapping[str, Any],
) -> dict[str, Any]:
    """Deriva un piano minimo dalla struttura e dagli eventi già confermati."""
    elenco = [str(voce) for voce in ordine if str(voce).strip()]
    posizione = elenco.index(sezione) if sezione in elenco else len(elenco)
    precedente = elenco[posizione - 1] if posizione else ""
    successiva = elenco[posizione + 1] if posizione + 1 < len(elenco) else ""
    scene = dict(memoria.get("scene", {}) or {})
    scena_precedente = dict(scene.get(precedente, {}) or {})
    presenti = _nomi(sezione) or list(scena_precedente.get("personaggi_presenti", []) or [])[:3]
    luogo = _luoghi(sezione) or list(scena_precedente.get("luoghi_citati", []) or [])[:1]
    return {
        "sezione": sezione,
        "obiettivo": f"sviluppare esclusivamente la promessa narrativa di «{sezione}»",
        "personaggi": presenti,
        "ambientazione": luogo,
        "punto_temporale": f"dopo «{precedente}»" if precedente else "apertura del manoscritto",
        "situazione_iniziale": scena_precedente.get("chiusura", "continuità con l'ultima scena confermata"),
        "conflitto": "inserire un ostacolo, una scelta, una conseguenza o una rivelazione nuova coerente con il titolo",
        "azioni": "mostrare azioni, percezioni o dialoghi che facciano avanzare la storia",
        "nuove_informazioni": "aggiungere solo informazioni nuove e necessarie alla voce dell'indice",
        "cambiamento": "la scena deve lasciare una condizione diversa da quella iniziale",
        "situazione_finale": "chiudere con una conseguenza concreta, senza risolvere le scene successive",
        "prossimo_collegamento": successiva,
    }


def contesto_narrativo(sezione: str, ordine: Sequence[str], memoria: Mapping[str, Any]) -> str:
    """Rende il piano e i vincoli narrativi pronti per il prompt, senza testo superfluo."""
    if not memoria.get("attiva"):
        return ""
    piano = piano_scena(sezione, ordine, memoria)
    eventi = list(memoria.get("eventi_confermati", []) or [])[-5:]
    relazioni = list(memoria.get("relazioni_confermate", []) or [])[-3:]
    stati = list(memoria.get("stati_emotivi_confermati", []) or [])[-3:]
    righe = ["=== BUSSOLA NARRATIVA STRUTTURATA ==="]
    if piano["personaggi"]:
        righe.append("Personaggi già presenti di recente: " + ", ".join(piano["personaggi"]))
    if piano["ambientazione"]:
        righe.append("Ambientazione recente/confermata: " + ", ".join(piano["ambientazione"]))
    righe.extend([
        "Situazione di partenza: " + str(piano["situazione_iniziale"]),
        "Obiettivo della scena corrente: " + str(piano["obiettivo"]),
        "Conflitto o svolta: " + str(piano["conflitto"]),
        "Azioni da privilegiare: " + str(piano["azioni"]),
        "Nuove informazioni: " + str(piano["nuove_informazioni"]),
        "Cambiamento obbligatorio: " + str(piano["cambiamento"]),
        "Esito atteso: " + str(piano["situazione_finale"]),
    ])
    if piano["prossimo_collegamento"]:
        righe.append("Prepara senza svolgerla la sezione successiva: " + str(piano["prossimo_collegamento"]))
    if eventi:
        righe.append("Eventi già confermati - non ripeterli come inediti:")
        righe.extend(f"- {evento.get('sezione', '')}: {evento.get('esito', '')}" for evento in eventi)
    if relazioni:
        righe.append("Dinamiche tra personaggi già osservate:")
        righe.extend(f"- {dato.get('fatto', '')}" for dato in relazioni)
    if stati:
        righe.append("Stati emotivi già osservati:")
        righe.extend(f"- {dato.get('fatto', '')}" for dato in stati)
    righe.append("Usa questi dati come canone: non inventare spostamenti, presenze o rivelazioni incompatibili. Se un cambiamento intenzionale è necessario, mostrane la causa nella scena.")
    return "\n".join(righe)[:4200]


def controlla_unita_narrativa(
    sezione: str,
    testo: str,
    memoria_precedente: Mapping[str, Any],
) -> list[str]:
    """Segnala solo problemi locali ad alta evidenza, senza bloccare la scrittura."""
    avvisi: list[str] = []
    testo = _pulito(testo)
    if not testo:
        return avvisi
    for formula, occorrenze in _formule(testo).items():
        if occorrenze >= 4:
            avvisi.append(f"formula ricorrente nella sezione: «{formula}» ({occorrenze} volte)")
    scene = dict(memoria_precedente.get("scene", {}) or {})
    for titolo, scena in list(scene.items())[-4:]:
        chiusura = str(scena.get("chiusura", "") or "")
        if len(chiusura.split()) >= 8 and _similarita_evento(testo, chiusura) >= 0.82:
            avvisi.append(f"possibile ripresa della scena già chiusa in «{titolo}»")
            break
    return avvisi


def rapporto_narrativo_locale(indice: str, contenuti: Mapping[str, Any], memoria: Mapping[str, Any]) -> list[str]:
    """Aggiunge all'audit generale indicatori locali, ripetibili e senza API."""
    if not memoria.get("attiva"):
        return []
    righe = ["CONTROLLI NARRATIVI LOCALI"]
    scene = dict(memoria.get("scene", {}) or {})
    righe.append(f"Scene confermate nella memoria: {len(scene)}")
    formule = Counter()
    for scena in scene.values():
        formule.update(dict(scena.get("formule", {}) or {}))
    ricorrenti = [f"{formula} ({conteggio})" for formula, conteggio in formule.items() if conteggio >= max(5, len(scene))]
    if ricorrenti:
        righe.append("Formule da rivedere per frequenza: " + ", ".join(ricorrenti[:5]))
    else:
        righe.append("Nessuna formula monitorata supera la soglia locale.")
    return righe
