"""Ricerca fonti mirata: domande dalla sidebar, schede per fonte, fonti per capitolo.

Modulo puro: nessuna chiamata AI, nessun accesso alla sessione Streamlit.
L'app usa queste funzioni per:
1. trasformare i campi della sidebar in domande di ricerca precise;
2. chiedere al motore di ricerca schede strutturate (una per fonte);
3. leggere, unire e filtrare le schede ricevute da una o più ricerche;
4. dare a ogni sezione in stesura solo le schede pertinenti, senza costi.
"""

from __future__ import annotations

import json
import re

from book_project import tipo_opera

LIVELLI_RICERCA = ("standard", "approfondita")
MASSIMO_FONTI = {"standard": 12, "approfondita": 15}
# Numero di ricerche lanciate in parallelo: la durata resta vicina a quella di
# una ricerca singola anche nel livello approfondito.
GRUPPI_RICERCA = {"standard": 1, "approfondita": 3}
PERTINENZA_MINIMA = 6
# Sotto questa soglia il livello approfondito fa un secondo giro mirato.
FONTI_MINIME_SECONDO_GIRO = 6


def normalizza_livello(livello: str) -> str:
    livello = str(livello or "").strip().lower()
    return livello if livello in LIVELLI_RICERCA else "standard"


def _breve(testo: str, limite: int = 180) -> str:
    testo = re.sub(r"\s+", " ", str(testo or "")).strip()
    if len(testo) <= limite:
        return testo
    taglio = testo[:limite].rsplit(" ", 1)[0]
    return taglio + "…"


def _righe_approfondimenti(approfondimenti: str, massimo: int = 3) -> list[str]:
    righe = []
    for riga in re.split(r"[\n;]+", str(approfondimenti or "")):
        riga = re.sub(r"^\s*[-*•\d.)]+\s*", "", riga).strip()
        if len(riga) >= 12 and not riga.lower().startswith(("nessun", "none")):
            righe.append(_breve(riga, 160))
        if len(righe) >= massimo:
            break
    return righe


def domande_ricerca(titolo: str, genere: str, trama: str, obiettivo: str,
                    approfondimenti: str = "", pubblico: str = "") -> list[str]:
    """Trasforma i campi della sidebar in 6-10 domande di ricerca mirate."""
    tema = _breve(f"{titolo}: {trama}" if titolo else trama, 200) or _breve(titolo, 120)
    scopo = _breve(obiettivo, 140) or "l'obiettivo del libro"
    lettore = _breve(pubblico, 100) or f"i lettori di {genere or 'questo genere'}"
    if tipo_opera(genere) == "narrativa":
        domande = [
            f"Ambientazione di «{tema}»: luoghi, epoca, contesto storico e sociale verificabili.",
            f"Vita quotidiana nell'ambientazione di «{tema}»: abitudini, oggetti, abbigliamento, modi di parlare.",
            f"Mestieri, competenze e procedure reali dei personaggi di «{tema}» (come lavorano davvero).",
            f"Fatti, eventi o fenomeni reali collegati a «{tema}» utili a rendere la trama credibile.",
            f"Convenzioni del genere {genere or ''} e aspettative attuali dei lettori: cosa funziona e cosa annoia.",
            f"Dettagli tecnici plausibili per «{tema}»: tecnologia, trasporti, tempi, distanze, procedure.",
        ]
    else:
        domande = [
            f"Definizioni, concetti di base e modelli riconosciuti su «{tema}».",
            f"Dati, statistiche e studi recenti (ultimi 3 anni) su «{tema}».",
            f"Casi reali ed esempi pratici verificabili utili per {scopo}.",
            f"Errori comuni, ostacoli e domande frequenti di {lettore} su «{tema}».",
            f"Metodi, strumenti ed esercizi pratici per {scopo}.",
            f"Limiti, controversie e posizioni contrastanti su «{tema}».",
            f"Norme, linee guida o standard ufficiali aggiornati che riguardano «{tema}», se esistono.",
        ]
    for riga in _righe_approfondimenti(approfondimenti):
        domande.append(f"Approfondimento richiesto dall'autore: {riga}")
    return domande


def dividi_domande(domande: list[str], gruppi: int) -> list[list[str]]:
    """Distribuisce le domande in gruppi bilanciati per ricerche parallele."""
    gruppi = max(1, min(int(gruppi or 1), len(domande) or 1))
    divise: list[list[str]] = [[] for _ in range(gruppi)]
    for indice, domanda in enumerate(domande):
        divise[indice % gruppi].append(domanda)
    return [gruppo for gruppo in divise if gruppo]


def prompt_ricerca_fonti(titolo: str, genere: str, trama: str, obiettivo: str, lingua: str,
                         approfondimenti: str, domande: list[str], massimo_schede: int) -> str:
    """Istruzioni per una ricerca web che restituisce mappa + schede strutturate."""
    elenco = "\n".join(f"{n}. {d}" for n, d in enumerate(domande, 1))
    return (
        "Sei un ricercatore editoriale. Usa la ricerca web per rispondere a OGNI domanda qui sotto "
        "con fonti autorevoli e aggiornate (enti ufficiali, università, riviste, editori affidabili, "
        "esperti riconosciuti). Cerca nella lingua del libro e anche in inglese quando le fonti migliori "
        "sono in inglese. Non scrivere il libro.\n\n"
        f"DOMANDE DI RICERCA:\n{elenco}\n\n"
        "FORMATO DELLA RISPOSTA (obbligatorio, in italiano):\n"
        "MAPPA CONCETTUALE INTERNA\n"
        "Una mappa concisa riformulata con parole tue: concetti affidabili, fatti e dati da verificare, "
        "limiti o controversie, progressione consigliata, aspetti concreti da assegnare all'indice. "
        "Niente URL, citazioni o titoli delle fonti nella mappa.\n\n"
        "SCHEDE FONTI\n"
        f"Poi da 1 a {massimo_schede} schede, solo per le fonti davvero pertinenti al brief, "
        "in ordine di utilità. Ogni scheda ha esattamente questo formato:\n"
        "### FONTE\n"
        "Titolo: titolo della pagina o del documento\n"
        "URL: indirizzo completo\n"
        "Pertinenza: voto da 1 a 10 rispetto a titolo, argomento e obiettivo del brief\n"
        "Tema: di cosa parla, in una riga\n"
        "Fatti chiave:\n"
        "- 3-5 fatti, dati o concetti utili, RIFORMULATI con parole tue (mai frasi copiate)\n"
        "Utile per: quali parti o argomenti del libro può sostenere\n\n"
        "Scarta fonti generiche, duplicate, commerciali o deboli. Non inventare URL: inserisci solo "
        "pagine che hai realmente consultato.\n\n"
        f"BRIEF DEL LIBRO\nTitolo: {titolo}\nGenere: {genere}\nLingua del libro: {lingua}\n"
        f"Argomento: {trama}\nObiettivo: {obiettivo}\n"
        f"Approfondimenti: {approfondimenti or 'Nessuno'}"
    )


def prompt_secondo_giro(domande: list[str], fonti_note: list[dict], **brief) -> str:
    """Secondo giro: cerca solo gli aspetti rimasti senza fonti, escludendo quelle già trovate.

    ``brief`` contiene titolo, genere, trama, obiettivo, lingua, approfondimenti, massimo_schede.
    """
    gia = "\n".join(f"- {s.get('url', '')}" for s in fonti_note if s.get("url"))
    base = prompt_ricerca_fonti(domande=domande, **brief)
    return base + (f"\n\nFONTI GIÀ TROVATE (non ripeterle):\n{gia}" if gia else "")


_MARCATORE_SCHEDE = re.compile(r"(?im)^\s*(?:#{1,6}\s*)?\**\s*SCHEDE\s+(?:DELLE\s+)?FONTI\s*\**\s*:?[ \t]*$")
_MARCATORE_REGISTRO = re.compile(
    r"(?im)^\s*(?:#{1,6}\s*)?\**\s*REGISTRO\s+(?:DELLE\s+)?FONTI(?:\s+WEB)?\s*\**\s*:?[ \t]*$"
)
_INIZIO_SCHEDA = re.compile(r"(?im)^\s*(?:#{1,6}\s*)?\**\s*FONTE\b[^\n]*$")
_ETICHETTE = {
    "titolo": "titolo", "title": "titolo",
    "url": "url", "link": "url",
    "pertinenza": "pertinenza", "relevance": "pertinenza",
    "tema": "tema", "topic": "tema",
    "fatti chiave": "fatti", "key facts": "fatti",
    "utile per": "utile_per", "useful for": "utile_per",
}


def _pulisci_url(url: str) -> str:
    url = str(url or "").strip().strip("<>()[]").rstrip(".,;)")
    corrispondenza = re.search(r"https?://[^\s<>\]\)\"']+", url)
    return corrispondenza.group(0).rstrip(".,;") if corrispondenza else ""


def _chiave_url(url: str) -> str:
    url = re.sub(r"^https?://(www\.)?", "", str(url or "").lower())
    url = re.sub(r"[?#].*$", "", url)
    return url.rstrip("/")


def leggi_schede(testo: str) -> tuple[str, list[dict]]:
    """Separa la mappa dalle schede fonti. Restituisce (mappa, schede)."""
    testo = str(testo or "").strip()
    marcatore = _MARCATORE_SCHEDE.search(testo)
    if marcatore:
        mappa, resto = testo[:marcatore.start()], testo[marcatore.end():]
    else:
        primo = _INIZIO_SCHEDA.search(testo)
        if not primo:
            return testo, []
        mappa, resto = testo[:primo.start()], testo[primo.start():]
    registro = _MARCATORE_REGISTRO.search(resto)
    if registro:
        resto = resto[:registro.start()]
    mappa = re.sub(r"(?im)^\s*(?:#{1,6}\s*)?\**\s*MAPPA\s+CONCETTUALE\s+INTERNA\s*\**\s*:?[ \t]*\n", "", mappa).strip()

    blocchi = [b for b in _INIZIO_SCHEDA.split(resto) if b.strip()]
    schede = []
    for blocco in blocchi:
        scheda = {"titolo": "", "url": "", "pertinenza": 0, "tema": "", "fatti": [], "utile_per": ""}
        campo = ""
        for riga in blocco.splitlines():
            pulita = riga.strip().strip("*").strip()
            if not pulita:
                continue
            etichetta = re.match(r"^[-*•]?\s*\**([A-Za-zÀ-ÿ ]{3,20})\**\s*:\s*(.*)$", pulita)
            nome = _ETICHETTE.get(etichetta.group(1).strip().lower()) if etichetta else None
            if nome:
                campo, valore = nome, etichetta.group(2).strip()
                if nome == "fatti":
                    if valore:
                        scheda["fatti"].append(valore)
                elif nome == "pertinenza":
                    numero = re.search(r"\d+(?:[.,]\d+)?", valore)
                    scheda["pertinenza"] = min(10, round(float(numero.group(0).replace(",", ".")))) if numero else 0
                elif nome == "url":
                    scheda["url"] = _pulisci_url(valore)
                else:
                    scheda[nome] = valore
            elif campo == "fatti" and re.match(r"^[-*•\d.)]+\s*", pulita):
                fatto = re.sub(r"^[-*•\d.)]+\s*", "", pulita).strip()
                if fatto:
                    scheda["fatti"].append(fatto)
        if not scheda["url"]:
            scheda["url"] = _pulisci_url(blocco)
        if scheda["url"]:
            scheda["titolo"] = scheda["titolo"] or scheda["url"]
            scheda["fatti"] = scheda["fatti"][:5]
            schede.append(scheda)
    return mappa, schede


def unisci_schede(*liste: list[dict], massimo: int = 12, minimo_pertinenza: int = PERTINENZA_MINIMA) -> list[dict]:
    """Unisce schede di più ricerche: niente doppioni, solo le più pertinenti."""
    migliori: dict[str, dict] = {}
    ordine: dict[str, int] = {}
    for lista in liste:
        for scheda in lista or []:
            chiave = _chiave_url(scheda.get("url"))
            if not chiave:
                continue
            ordine.setdefault(chiave, len(ordine))
            attuale = migliori.get(chiave)
            if attuale is None or int(scheda.get("pertinenza") or 0) > int(attuale.get("pertinenza") or 0):
                migliori[chiave] = dict(scheda)
    # Una scheda senza voto non viene scartata: il modello potrebbe averlo omesso.
    tenute = [s for s in migliori.values()
              if not s.get("pertinenza") or int(s["pertinenza"]) >= minimo_pertinenza]
    tenute.sort(key=lambda s: (-int(s.get("pertinenza") or 0), ordine[_chiave_url(s["url"])]))
    return tenute[:max(1, int(massimo))]


def registro_da_schede(schede: list[dict]) -> str:
    """Registro compatibile con il vecchio formato: '- Titolo | URL | motivo'."""
    righe = []
    for s in schede:
        motivo = s.get("utile_per") or s.get("tema") or ""
        if s.get("pertinenza"):
            motivo = f"{s['pertinenza']}/10 · {motivo}".strip(" ·")
        righe.append(f"- {s.get('titolo') or s['url']} | {s['url']} | {motivo}".rstrip(" |"))
    return "\n".join(righe)


def schede_in_json(schede: list[dict]) -> str:
    return json.dumps(schede or [], ensure_ascii=False)


def schede_da_json(valore) -> list[dict]:
    if isinstance(valore, list):
        return [s for s in valore if isinstance(s, dict) and s.get("url")]
    try:
        dati = json.loads(str(valore or "[]"))
    except (TypeError, ValueError):
        return []
    return [s for s in dati if isinstance(s, dict) and s.get("url")] if isinstance(dati, list) else []


def sintesi_schede(schede: list[dict], limite: int = 3000) -> str:
    """Testo compatto delle schede, per l'indice (niente URL)."""
    parti, usati = [], 0
    for s in schede:
        fatti = "; ".join(s.get("fatti") or [])
        riga = f"- {s.get('tema') or s.get('titolo')}: {fatti}".strip()
        if s.get("utile_per"):
            riga += f" (utile per: {s['utile_per']})"
        if usati + len(riga) > limite:
            break
        parti.append(riga)
        usati += len(riga) + 1
    return "\n".join(parti)


_STOP = {
    "della", "delle", "dello", "degli", "dalla", "dalle", "nella", "nelle", "sulla", "sulle",
    "come", "cosa", "sono", "essere", "questo", "questa", "quello", "quella", "anche", "perché",
    "capitolo", "parte", "sezione", "introduzione", "conclusione", "with", "from", "that", "this",
    "chapter", "part", "what", "your", "their", "about", "capítulo", "chapitre", "kapitel", "capitolul",
}


def _parole(testo: str) -> set[str]:
    testo = str(testo or "").lower()
    parole = {p for p in re.findall(r"\w{4,}", testo) if not p.isdigit() and p not in _STOP}
    # Cinese/giapponese: senza spazi, si usano coppie di ideogrammi.
    for blocco in re.findall(r"[一-鿿]{2,}", testo):
        parole.update(blocco[i:i + 2] for i in range(len(blocco) - 1))
    # Radice semplice: "abitudini" e "abitudine" si incontrano.
    return parole | {p[:6] for p in parole if len(p) >= 7}


def _testo_scheda(scheda: dict) -> str:
    return " ".join([scheda.get("titolo", ""), scheda.get("tema", ""), scheda.get("utile_per", ""),
                     " ".join(scheda.get("fatti") or [])])


def punteggio_scheda(scheda: dict, testo_sezione: str) -> int:
    return len(_parole(_testo_scheda(scheda)) & _parole(testo_sezione))


def abbina_schede_ai_capitoli(schede: list[dict], capitoli: list[str], massimo_per_fonte: int = 3) -> dict[str, list[str]]:
    """URL -> capitoli a cui la fonte serve di più (calcolo locale, gratuito)."""
    abbinamenti: dict[str, list[str]] = {}
    for s in schede:
        punteggi = [(punteggio_scheda(s, c), i, c) for i, c in enumerate(capitoli or [])]
        punteggi = [p for p in punteggi if p[0] > 0]
        punteggi.sort(key=lambda p: (-p[0], p[1]))
        abbinamenti[s["url"]] = [c for _, _, c in punteggi[:massimo_per_fonte]]
    return abbinamenti


def schede_per_sezione(schede: list[dict], sezione: str, argomento: str = "",
                       limite: int = 2400, massimo: int = 4) -> str:
    """Solo le schede utili a questa sezione, riformulate, senza URL."""
    if not schede:
        return ""
    testo = f"{sezione} {argomento}"
    valutate = [(punteggio_scheda(s, testo), int(s.get("pertinenza") or 0), i, s) for i, s in enumerate(schede)]
    valutate.sort(key=lambda v: (-v[0], -v[1], v[2]))
    pertinenti = [v for v in valutate if v[0] > 0][:massimo]
    if not pertinenti:
        # Nessuna corrispondenza diretta: le due fonti più autorevoli del libro.
        pertinenti = sorted(valutate, key=lambda v: (-v[1], v[2]))[:2]
    blocchi, usati = [], 0
    for _, _, _, s in pertinenti:
        fatti = "\n".join(f"  · {f}" for f in (s.get("fatti") or []))
        blocco = f"- {s.get('tema') or s.get('titolo')}\n{fatti}".rstrip()
        if usati + len(blocco) > limite:
            continue
        blocchi.append(blocco)
        usati += len(blocco)
    return "\n".join(blocchi)


def domande_scoperte(domande: list[str], schede: list[dict]) -> list[str]:
    """Domande che nessuna scheda trovata copre: servono al secondo giro."""
    return [d for d in domande if not any(punteggio_scheda(s, d) >= 2 for s in schede)]
