"""Progetto del libro: pianificazione, coerenza e controlli per ogni genere.

Il modulo non usa Streamlit e non chiama provider AI. Contiene:
- la classificazione dell'opera (narrativa, saggistica, manuale);
- i campi del progetto per ciascun tipo (verità nascosta, mappa dei semi,
  tesi centrale, obiettivi e prerequisiti) e la loro lettura;
- le direttive di struttura di apertura e chiusura dei capitoli;
- i marcatori [DA VERIFICARE] per i dati incerti;
- i controlli locali e gratuiti su ripetizioni, frasi fatte e dialoghi;
- i prompt per proporre il progetto, aggiornare la scheda di coerenza e
  rivedere un capitolo.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence

from narrative_engine import genere_narrativo


# ---------------------------------------------------------------------------
# Tipo di opera
# ---------------------------------------------------------------------------

GENERI_MANUALE = frozenset({
    "Manuale Tecnico", "Manuale Pratico", "Manuale Psicologico", "Ricettario",
    "Test Prep (Preparazione Esami)", "Quiz Scientifico", "Meditazione / Mindfulness",
})


def tipo_opera(genere: str) -> str:
    """'narrativa', 'manuale' oppure 'saggistica'."""
    if genere_narrativo(genere):
        return "narrativa"
    if str(genere or "").strip() in GENERI_MANUALE:
        return "manuale"
    return "saggistica"


# Campi del progetto: nome nel progetto -> chiave del widget.
CAMPI_PROGETTO = {
    "verita_nascosta": "book_hidden_truth",
    "mappa_semi": "book_setup_map",
    "tesi_centrale": "book_thesis",
    "obiettivi_prerequisiti": "book_learning_goals",
    "registro_coerenza": "book_continuity_log",
}

# Campi specifici di ogni tipo (oltre a scaletta e scheda di coerenza, comuni).
CAMPI_PER_TIPO = {
    "narrativa": ("scheda_personaggi", "verita_nascosta", "mappa_semi"),
    "saggistica": ("tesi_centrale",),
    "manuale": ("obiettivi_prerequisiti",),
}

# Intestazioni tecniche dei blocchi restituiti dalla proposta del progetto.
INTESTAZIONI_BLOCCHI = {
    "scheda_personaggi": "PERSONAGGI E MONDO",
    "verita_nascosta": "VERITÀ NASCOSTA",
    "mappa_semi": "MAPPA DEI SEMI",
    "tesi_centrale": "TESI CENTRALE",
    "obiettivi_prerequisiti": "OBIETTIVI E PREREQUISITI",
    "scaletta": "SCALETTA",
}


def _pulito(valore, limite: int) -> str:
    testo = str(valore or "").strip()
    return testo[:limite].rstrip() + ("…" if len(testo) > limite else "")


def _norm(testo: str) -> str:
    return re.sub(r"\s+", " ", str(testo or "")).strip().casefold()


# ---------------------------------------------------------------------------
# Mappa dei semi (misteri, indizi, promesse)
# ---------------------------------------------------------------------------

_CHIAVI_COMPARE = r"compare|appare|appears?|introduced|aparece|appara[iî]t|erscheint|apare|появляется|يظهر|出现"
_CHIAVI_RISOLVE = r"si\s+risolve|risolto|risolve|resolved?|resolves|se\s+resuelve|se\s+r[ée]sout|l[öo]st\s+sich|aufgel[öo]st|se\s+rezolv[ăa]|разрешается|يُحل|يحل|解决"


def leggi_semi(testo: str) -> list[dict[str, str]]:
    """Legge righe come «- La lettera | compare: Capitolo 2 | si risolve: Capitolo 9»."""
    semi = []
    for riga in str(testo or "").splitlines():
        riga = re.sub(r"^\s*(?:[-•*]|\d+[.)])\s*", "", riga).strip()
        if not riga or "|" not in riga:
            continue
        parti = [parte.strip() for parte in riga.split("|")]
        seme = {"seme": parti[0], "compare": "", "risolve": ""}
        for parte in parti[1:]:
            compare = re.match(rf"(?i)^(?:{_CHIAVI_COMPARE})\s*[:：]\s*(.+)$", parte)
            risolve = re.match(rf"(?i)^(?:{_CHIAVI_RISOLVE})\s*[:：]\s*(.+)$", parte)
            if compare:
                seme["compare"] = compare.group(1).strip()
            elif risolve:
                seme["risolve"] = risolve.group(1).strip()
        if seme["seme"]:
            semi.append(seme)
    return semi


_PREFISSO_CAPITOLO = re.compile(
    r"(?i)^(?:capitolo|chapter|kapitel|cap[ií]tulo|chapitre|capitolul|глава|الفصل|章节|第)\s*(\d+)"
)


def _numero_capitolo(voce: str) -> str:
    voce = str(voce or "").strip()
    trovato = _PREFISSO_CAPITOLO.match(voce)
    if trovato:
        return trovato.group(1)
    sotto = re.match(r"^(\d+)\.\d+", voce)
    return sotto.group(1) if sotto else ""


def voce_corrisponde(riferimento: str, sezione: str) -> bool:
    """Un riferimento «Capitolo 3» vale per il capitolo 3 e per i suoi sottocapitoli."""
    rif, sez = _norm(riferimento), _norm(sezione)
    if not rif or not sez:
        return False
    if rif == sez or sez.startswith(rif) or rif.startswith(sez):
        return True
    numero_rif = _numero_capitolo(riferimento)
    if numero_rif and _PREFISSO_CAPITOLO.match(str(riferimento).strip()) and not re.match(r"^\d+\.\d+", str(riferimento).strip()):
        return _numero_capitolo(sezione) == numero_rif
    return False


def semi_della_sezione(testo_semi: str, sezione: str) -> tuple[list[str], list[str]]:
    """Semi da introdurre e semi da risolvere nella sezione corrente."""
    da_piantare, da_risolvere = [], []
    for seme in leggi_semi(testo_semi):
        if seme["compare"] and voce_corrisponde(seme["compare"], sezione):
            da_piantare.append(seme["seme"])
        if seme["risolve"] and voce_corrisponde(seme["risolve"], sezione):
            da_risolvere.append(seme["seme"])
    return da_piantare, da_risolvere


def controllo_semi(testo_semi: str, sezioni: Sequence[str], contenuti: Mapping[str, str]) -> list[dict[str, str]]:
    """Controllo locale: semi senza risoluzione, con rimandi inesistenti o non ancora scritti."""
    esiti = []
    for seme in leggi_semi(testo_semi):
        if not seme["risolve"]:
            esiti.append({"seme": seme["seme"], "problema": "senza_risoluzione", "voce": ""})
            continue
        voci = [sezione for sezione in sezioni if voce_corrisponde(seme["risolve"], sezione)]
        if not voci:
            esiti.append({"seme": seme["seme"], "problema": "voce_inesistente", "voce": seme["risolve"]})
        elif not any(str(contenuti.get(voce, "") or "").strip() for voce in voci):
            esiti.append({"seme": seme["seme"], "problema": "non_ancora_scritto", "voce": seme["risolve"]})
    return esiti


def punti_aperti_registro(registro: str) -> list[str]:
    """Voci elencate sotto l'ultima intestazione della scheda di coerenza.

    Le istruzioni chiedono di mettere misteri, promesse e rimandi ancora
    aperti sotto l'ultima intestazione: così la lettura non dipende dalla lingua.
    """
    blocco: list[str] = []
    for riga in str(registro or "").splitlines():
        pulita = riga.strip()
        if not pulita:
            continue
        if not re.match(r"^[-•*]", pulita):
            blocco = []
            continue
        voce = re.sub(r"^[-•*]\s*", "", pulita).strip()
        if voce and voce not in {"…", "...", "-"} and not re.match(r"(?i)^(nessun|none|ninguno|aucun|keine|niciun|нет|لا يوجد|无)", voce):
            blocco.append(voce)
    return blocco


# ---------------------------------------------------------------------------
# Struttura dei capitoli (apertura, corpo, chiusura) per tipo di opera
# ---------------------------------------------------------------------------

_REGEX_PARTE = re.compile(r"(?i)^(?:parte|part|partie|teil|partea|часть|الجزء|部分)\b")
_REGEX_CAPITOLO = re.compile(r"(?i)^(?:capitolo|chapter|kapitel|cap[ií]tulo|chapitre|capitolul|глава|الفصل|章节)\s+\d+")
_REGEX_SOTTO = re.compile(r"^\d+\.\d+")


def posizione_nel_capitolo(sezione: str, ordine: Sequence[str]) -> tuple[bool, bool]:
    """(apre_capitolo, chiude_capitolo) per una voce dell'indice."""
    voci = [str(voce).strip() for voce in ordine if str(voce).strip()]
    sezione = str(sezione or "").strip()
    if sezione not in voci:
        return True, True
    posizione = voci.index(sezione)
    precedente = voci[posizione - 1] if posizione else ""
    successiva = voci[posizione + 1] if posizione + 1 < len(voci) else ""
    if _REGEX_SOTTO.match(sezione):
        apre = not _REGEX_SOTTO.match(precedente) or _numero_capitolo(precedente) != _numero_capitolo(sezione)
    else:
        apre = True
    chiude = (
        not successiva
        or bool(_REGEX_CAPITOLO.match(successiva))
        or bool(_REGEX_PARTE.match(successiva))
        or (_REGEX_SOTTO.match(successiva) and _numero_capitolo(successiva) != _numero_capitolo(sezione))
    )
    if _REGEX_CAPITOLO.match(sezione) and _REGEX_SOTTO.match(successiva):
        chiude = False  # cornice di un capitolo con sottocapitoli
    return apre, bool(chiude)


def direttive_struttura(tipo: str, apre: bool, chiude: bool, marcatore: str = "[DA VERIFICARE]") -> str:
    """Regole di apertura, corpo e chiusura della sezione corrente."""
    righe = ["=== STRUTTURA DI QUESTA SEZIONE ==="]
    if tipo == "narrativa":
        if apre:
            righe.append("- Apri il capitolo con un aggancio: una scena già in movimento, un gesto, una domanda; mai un riassunto del capitolo precedente.")
        righe.append("- La scena fa avanzare la trama o approfondisce un personaggio; il protagonista prende decisioni attive.")
        righe.append("- Varia il tipo di scena rispetto alla precedente (azione, confronto, indagine, intimità, pericolo, scoperta).")
        righe.append("- Mostra l'interiorità del personaggio di riferimento: desideri, paure, ricordi, contraddizioni. I silenzi hanno un motivo.")
        if chiude:
            righe.append("- Questa sezione chiude il capitolo: dai almeno una risposta parziale e lascia una domanda nuova o una decisione in sospeso che spinga a continuare, senza colpi di scena artificiali.")
    elif tipo == "manuale":
        if apre:
            righe.append("- Apri con il problema reale che il capitolo risolve e con l'obiettivo concreto; spiega in breve il PERCHÉ prima del COME.")
        righe.append("- Procedure in passi numerati, un'azione per passo, ognuno con il risultato atteso (\"dovresti vedere…\").")
        righe.append("- Definisci ogni termine tecnico alla prima occorrenza e usalo sempre allo stesso modo; non usare concetti non ancora spiegati.")
        righe.append("- Per ogni procedura: un esempio completo e gli errori comuni con la soluzione. Segnala rischi, sicurezza o perdita di dati con un'avvertenza chiara.")
        righe.append(f"- Non dare istruzioni non verificabili o inventate: se un dato, un menu o una versione non è certo, scrivi subito dopo {marcatore}.")
        if chiude:
            righe.append("- Questa sezione chiude il capitolo: termina con un riepilogo puntato e un esercizio o una verifica pratica.")
    else:
        if apre:
            righe.append("- Apri con un aggancio concreto: una storia, un caso o una domanda reale del lettore; mai con un riassunto.")
        righe.append("- Sviluppa: idea chiara e memorabile → spiegazione → prove ed esempi → obiezione principale e risposta.")
        righe.append("- Distingui fatti, interpretazioni e opinioni. Concreto batte astratto: esempi, dettagli, numeri, immagini specifiche.")
        righe.append(f"- Non inventare dati, studi, citazioni o fonti: se un dato non è certo, formulalo con prudenza oppure scrivi subito dopo {marcatore}.")
        if chiude:
            righe.append("- Questa sezione chiude il capitolo: termina con una sintesi memorabile, un'applicazione pratica e un collegamento al capitolo successivo.")
    return "\n".join(righe)


# ---------------------------------------------------------------------------
# Marcatori per i dati da verificare
# ---------------------------------------------------------------------------

MARCATORI_VERIFICA = {
    "Italiano": "[DA VERIFICARE]",
    "English": "[TO VERIFY]",
    "Español": "[POR VERIFICAR]",
    "Français": "[À VÉRIFIER]",
    "Deutsch": "[ZU PRÜFEN]",
    "Română": "[DE VERIFICAT]",
    "Русский": "[ПРОВЕРИТЬ]",
    "العربية": "[يجب التحقق]",
    "中文": "[待核实]",
}
_REGEX_MARCATORE = re.compile(
    r"\s*\[(?:" + "|".join(re.escape(m[1:-1]) for m in MARCATORI_VERIFICA.values()) + r")\]",
    re.IGNORECASE,
)


def marcatore_verifica(lingua: str) -> str:
    return MARCATORI_VERIFICA.get(lingua, MARCATORI_VERIFICA["Italiano"])


def rimuovi_marcatori_verifica(testo: str) -> str:
    """Toglie i marcatori dal testo esportato (Word, PDF)."""
    return _REGEX_MARCATORE.sub("", str(testo or ""))


def trova_marcatori_verifica(contenuti: Mapping[str, str]) -> list[dict[str, str]]:
    """Frasi che contengono un marcatore, per l'elenco di controllo dell'autore."""
    trovati = []
    for sezione, testo in contenuti.items():
        for frase in re.split(r"(?<=[.!?。！？])\s+|\n+", str(testo or "")):
            if _REGEX_MARCATORE.search(frase):
                trovati.append({"sezione": str(sezione), "frase": _pulito(frase, 220)})
    return trovati


# ---------------------------------------------------------------------------
# Ripetizioni sull'intero libro, frasi fatte, dialoghi
# ---------------------------------------------------------------------------

FRASI_FATTE = (
    # Italiano
    "come se", "quel tanto che bastava", "un colpo secco", "trattenne il fiato", "trattenne il respiro",
    "in un mondo in cui", "è importante sottolineare che", "in conclusione possiamo dire",
    "non era soltanto", "per la prima volta", "rimase in silenzio", "abbassò lo sguardo",
    "strinse la mandibola", "un brivido lungo la schiena", "il cuore in gola",
    # English
    "held her breath", "held his breath", "a shiver ran down", "in a world where",
    "it is important to note that", "in conclusion", "let out a breath she didn't know",
)
SOGLIA_FRASI_FATTE = 2
SOGLIA_RIPETIZIONI = 3


def _testo_con_spazi(testo: str) -> bool:
    testo = str(testo or "")
    return bool(testo) and testo.count(" ") > len(testo) / 25


def ripetizioni_nel_libro(contenuti: Mapping[str, str], lunghezza: int = 4, limite: int = 10) -> list[tuple[str, int]]:
    """Espressioni di 4 parole ripetute più di 3 volte in tutto il manoscritto."""
    conteggio: Counter[str] = Counter()
    for testo in contenuti.values():
        if not _testo_con_spazi(testo):
            continue  # cinese e lingue senza spazi: il conteggio per parole non è affidabile
        parole = re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)?", str(testo).casefold())
        for i in range(len(parole) - lunghezza + 1):
            gruppo = parole[i:i + lunghezza]
            if sum(1 for parola in gruppo if len(parola) >= 4) < 2:
                continue  # solo articoli e preposizioni: non è un'immagine ripetuta
            conteggio[" ".join(gruppo)] += 1
    ripetute = [(frase, n) for frase, n in conteggio.items() if n > SOGLIA_RIPETIZIONI]
    ripetute.sort(key=lambda dato: (-dato[1], dato[0]))
    return ripetute[:limite]


def frasi_fatte_nel_libro(contenuti: Mapping[str, str]) -> list[tuple[str, int]]:
    """Frasi fatte usate più di 2 volte in tutto il libro."""
    testo = " ".join(str(valore or "") for valore in contenuti.values()).casefold()
    risultati = [(frase, len(re.findall(rf"\b{re.escape(frase)}\b", testo))) for frase in FRASI_FATTE]
    return sorted([(f, n) for f, n in risultati if n > SOGLIA_FRASI_FATTE], key=lambda dato: -dato[1])


def dialoghi_senza_caporali(contenuti: Mapping[str, str], lingua: str) -> bool:
    """Romanzo italiano con dialoghi tra virgolette dritte o inglesi invece delle caporali."""
    if lingua != "Italiano":
        return False
    testo = " ".join(str(valore or "") for valore in contenuti.values())
    virgolette = testo.count('"') + testo.count("“") + testo.count("”")
    caporali = testo.count("«")
    return virgolette >= 6 and virgolette > caporali * 2


# ---------------------------------------------------------------------------
# Prompt: proposta del progetto, scheda di coerenza, revisione del capitolo
# ---------------------------------------------------------------------------

_ISTRUZIONI_BLOCCO = {
    "scheda_personaggi": "Personaggi principali con nome e cognome distinti: ruolo, età, lavoro, due tratti fisici, cosa vuole, cosa teme, cosa nasconde, modo di parlare. Il protagonista ha un difetto, una ferita e un arco di cambiamento. Poi luoghi principali (una pianta chiara: i luoghi non cambiano natura) e, se serve, le regole del mondo o della magia.",
    "verita_nascosta": "Premessa in una frase: [protagonista] vuole [obiettivo concreto] ma [ostacolo], altrimenti [posta in gioco]. Poi cosa è successo davvero: chi, come, perché, con una cronologia precisa. Se la trama si basa su un inganno scrivi due cronologie: quella vera e quella fatta credere. Nel romance indica l'ostacolo emotivo vero; nella biografia solo fatti noti.",
    "mappa_semi": "Da 5 a 7 misteri, indizi o promesse principali, uno per riga, nel formato esatto: - descrizione | compare: <titolo esatto di una voce dell'indice> | si risolve: <titolo esatto di una voce successiva>. Nessun seme senza risoluzione.",
    "tesi_centrale": "La tesi in una frase e perché è nuova, utile o controcorrente; poi il problema del lettore (domanda, dolore o curiosità) e le 5-12 idee chiave in ordine logico, una per riga.",
    "obiettivi_prerequisiti": "Obiettivi di apprendimento: cosa saprà FARE il lettore alla fine, in termini concreti e verificabili (uno per riga). Poi i prerequisiti: conoscenze, strumenti, materiali, versioni dei programmi. Poi gli apparati utili (glossario, checklist, risoluzione problemi, avvertenze di sicurezza).",
}

_PUNTI_SCALETTA = {
    "narrativa": "da 3 a 6 punti brevi: chi è in scena e dove, che cosa vuole il personaggio, quale conflitto incontra, che cosa cambia, con quale aggancio si chiude",
    "saggistica": "da 3 a 6 punti brevi: domanda di apertura, idea principale, prove o esempio concreto, obiezione e risposta, che cosa porta via il lettore, collegamento alla sezione successiva",
    "manuale": "da 3 a 6 punti brevi: obiettivo, concetti chiave, procedura passo-passo, esempio completo, errori comuni, esercizio o verifica",
}


def leggi_blocchi_progetto(testo: str) -> dict[str, str]:
    """Divide la proposta del progetto nei suoi blocchi («=== TESI CENTRALE ===»)."""
    inverso = {intestazione.casefold(): campo for campo, intestazione in INTESTAZIONI_BLOCCHI.items()}
    blocchi: dict[str, list[str]] = {}
    corrente = ""
    for riga in str(testo or "").splitlines():
        intestazione = re.match(r"^\s*[#*\s]*={2,}\s*(.+?)\s*={2,}[*\s]*$", riga)
        if intestazione:
            corrente = inverso.get(intestazione.group(1).strip().casefold(), "")
            if corrente:
                blocchi.setdefault(corrente, [])
            continue
        if corrente:
            blocchi[corrente].append(riga)
    return {campo: "\n".join(righe).strip() for campo, righe in blocchi.items() if "\n".join(righe).strip()}


def prompt_genera_progetto(
    *,
    tipo: str,
    sezioni: Sequence[str],
    indice: str,
    titolo: str,
    genere: str,
    trama: str,
    obiettivo: str,
    risultato: str,
    voce_narrante: str,
    lingua: str,
    campi_esistenti: Mapping[str, str],
    scaletta_esistente: str = "",
) -> str:
    """Chiede in un'unica risposta i campi vuoti del progetto e la scaletta."""
    da_compilare = [campo for campo in CAMPI_PER_TIPO.get(tipo, ()) if not str(campi_esistenti.get(campo, "") or "").strip()]
    gia_scritti = "\n\n".join(
        f"{INTESTAZIONI_BLOCCHI[campo]} (scritto dall'autore, è canone):\n{_pulito(valore, 3000)}"
        for campo, valore in campi_esistenti.items()
        if str(valore or "").strip() and campo in INTESTAZIONI_BLOCCHI
    )
    blocchi_richiesti = "\n".join(
        f"=== {INTESTAZIONI_BLOCCHI[campo]} ===\n{_ISTRUZIONI_BLOCCO[campo]}" for campo in da_compilare
    )
    elenco = "\n".join(f"[{sezione}]" for sezione in sezioni)
    nota_scaletta = ""
    if str(scaletta_esistente or "").strip():
        nota_scaletta = (
            "\nScaletta già scritta dall'autore: riporta identiche le voci già presenti e completa solo le altre.\n"
            f"{_pulito(scaletta_esistente, 6000)}\n"
        )
    tipo_descritto = {"narrativa": "romanzo", "manuale": "manuale", "saggistica": "saggio"}.get(tipo, "libro")
    return f"""Sei un editor senior. Progetta il {tipo_descritto} '{titolo}' ({genere}) prima della stesura, in {lingua}.

TRAMA O ARGOMENTO:
{_pulito(trama, 2500)}

OBIETTIVO: {_pulito(obiettivo, 400)}
RISULTATO / PROMESSA AL LETTORE: {_pulito(risultato, 400)}
{f"VOCE NARRANTE: {voce_narrante}" if tipo == "narrativa" else ""}

{gia_scritti}

INDICE COMPLETO:
{_pulito(indice, 5000)}
{nota_scaletta}
Restituisci SOLO i blocchi seguenti, con le intestazioni esattamente così, e i contenuti in {lingua}.
Non inventare dati, studi o fatti reali non noti. Mantieni coerenza totale tra i blocchi e con l'indice.

{blocchi_richiesti}

=== SCALETTA ===
Per OGNUNA delle voci qui sotto scrivi {_PUNTI_SCALETTA.get(tipo, _PUNTI_SCALETTA["saggistica"])} (massimo 25 parole per punto).
Ogni voce fa avanzare il libro rispetto alla precedente, senza ripetere ciò che è assegnato ad altre voci;
le Parti possono avere 2-3 punti. Riporta ogni titolo esattamente come scritto tra parentesi quadre:
[Titolo della voce]
- punto

VOCI:
{elenco}
"""


INTESTAZIONI_REGISTRO = {
    "narrativa": ("DOVE SONO I PERSONAGGI E COSA HANNO CON SÉ", "TEMPO DELLA STORIA", "CHI SA COSA", "MISTERI E PROMESSE ANCORA APERTI"),
    "saggistica": ("IDEE E TERMINI GIÀ SPIEGATI", "ESEMPI E STORIE GIÀ USATI", "PROMESSE AL LETTORE ANCORA DA MANTENERE"),
    "manuale": ("CONCETTI E TERMINI INTRODOTTI", "STRUMENTI E VERSIONI DI RIFERIMENTO", "PROCEDURE GIÀ SPIEGATE", "RIMANDI INTERNI ANCORA DA COMPLETARE"),
}


def prompt_aggiorna_registro(*, tipo: str, registro_attuale: str, sezione: str, testo_sezione: str, lingua: str) -> str:
    """Aggiorna la scheda di coerenza con ciò che è appena successo nella sezione."""
    intestazioni = INTESTAZIONI_REGISTRO.get(tipo, INTESTAZIONI_REGISTRO["saggistica"])
    modello = "\n".join(f"{intestazione}\n- …" for intestazione in intestazioni)
    testo = str(testo_sezione or "").strip()
    if len(testo) > 7000:
        testo = f"{testo[:2500]}\n[…]\n{testo[-4000:]}"
    return f"""Aggiorna la SCHEDA DI COERENZA di un libro dopo la sezione «{sezione}».

SCHEDA ATTUALE:
{_pulito(registro_attuale, 4000) or "(vuota)"}

TESTO DELLA SEZIONE APPENA SCRITTA:
{testo}

Restituisci la scheda completa aggiornata in {lingua}, con queste intestazioni (traducile in {lingua})
nello stesso ordine e voci brevi precedute da «- »:
{modello}

Regole: registra solo ciò che il testo afferma; togli ciò che non è più vero; l'ultima intestazione
contiene SOLO ciò che è ancora aperto (togli i punti risolti in questa sezione). Massimo 350 parole.
Nessun commento prima o dopo la scheda."""


_DOMANDE_REVISIONE = {
    "narrativa": "Il protagonista ha scelto qualcosa? C'è almeno una rivelazione? Ogni scena fa avanzare la trama o un personaggio? Il capitolo apre con un aggancio e chiude con un motivo per continuare?",
    "saggistica": "L'idea principale è chiara, provata e applicabile? Ci sono dati, studi o citazioni che sembrano inventati o non verificabili? L'obiezione principale è affrontata?",
    "manuale": "Un principiante riuscirebbe a seguire ogni passo senza aiuto? Sono usati termini non ancora spiegati? Ogni procedura ha risultato atteso, esempio, errori comuni? C'è riepilogo con esercizio?",
}


def prompt_revisione_capitolo(
    *,
    tipo: str,
    capitolo: str,
    testi: Sequence[tuple[str, str]],
    progetto: str,
    scaletta_capitolo: str,
    registro: str,
    lingua: str,
) -> str:
    """Autorevisione del capitolo: un rapporto, senza riscrivere il testo."""
    corpo = "\n\n".join(f"### {titolo}\n{str(testo or '').strip()}" for titolo, testo in testi if str(testo or "").strip())
    return f"""Sei un editor senior. Rivedi il capitolo «{capitolo}» e scrivi un rapporto in {lingua}. NON riscrivere il testo.

PROGETTO DEL LIBRO (canone):
{_pulito(progetto, 3500) or "(non disponibile)"}

SCALETTA DEL CAPITOLO:
{_pulito(scaletta_capitolo, 2000) or "(non disponibile)"}

SCHEDA DI COERENZA PRIMA DEL CAPITOLO:
{_pulito(registro, 2500) or "(non disponibile)"}

TESTO DEL CAPITOLO:
{corpo[:30000]}

Verifica, citando sempre la frase o il punto preciso:
1. È coerente con progetto, scaletta e scheda? Contraddizioni o ripetizioni rispetto a ciò che è già stato detto?
2. Che cosa ha guadagnato il lettore (emozione, svolta, idea, competenza)? Se nulla, dillo.
3. {_DOMANDE_REVISIONE.get(tipo, _DOMANDE_REVISIONE["saggistica"])}
4. Frasi, immagini o schemi ripetuti o frasi fatte da sostituire.
5. Il lettore vorrebbe andare avanti? Perché?

Formato: prima 3 righe di sintesi; poi «PROBLEMI» con un elenco puntato (sezione, frase, correzione proposta);
poi «PUNTI DI FORZA» in 2-3 righe. Testo semplice, senza Markdown."""


def progetto_come_testo(campi: Mapping[str, str]) -> str:
    """Riepilogo del progetto per i prompt (solo campi compilati)."""
    return "\n\n".join(
        f"{INTESTAZIONI_BLOCCHI.get(campo, campo.upper())}:\n{str(valore).strip()}"
        for campo, valore in campi.items()
        if str(valore or "").strip()
    )


def blocco_progetto_sezione(
    *,
    tipo: str,
    sezione: str,
    campi: Mapping[str, str],
    scaletta_sezione: Sequence[str],
    registro: str,
    apre: bool,
    chiude: bool,
    marcatore: str,
) -> str:
    """Dati del progetto e direttive per la sezione corrente (tutti i generi)."""
    righe = []
    if tipo == "narrativa":
        verita = str(campi.get("verita_nascosta", "") or "").strip()
        if verita:
            righe.append("=== VERITÀ NASCOSTA (solo per l'autore: NON rivelarla prima del momento previsto) ===\n" + _pulito(verita, 2500))
        da_piantare, da_risolvere = semi_della_sezione(campi.get("mappa_semi", ""), sezione)
        if da_piantare:
            righe.append("Semi da introdurre in questa parte del libro, con naturalezza e senza spiegarli (se non già presenti):\n" + "\n".join(f"- {s}" for s in da_piantare))
        if da_risolvere:
            righe.append("Semi da risolvere qui, in modo chiaro e coerente con la verità nascosta:\n" + "\n".join(f"- {s}" for s in da_risolvere))
    elif tipo == "saggistica":
        tesi = str(campi.get("tesi_centrale", "") or "").strip()
        if tesi:
            righe.append("=== TESI E IDEE CHIAVE DEL LIBRO ===\n" + _pulito(tesi, 2000))
    else:
        obiettivi = str(campi.get("obiettivi_prerequisiti", "") or "").strip()
        if obiettivi:
            righe.append("=== OBIETTIVI DI APPRENDIMENTO E PREREQUISITI ===\n" + _pulito(obiettivi, 2000))
    if tipo != "narrativa" and scaletta_sezione:
        righe.append(f"Scaletta approvata per «{sezione}» (segui questi punti in ordine):\n" + "\n".join(f"- {p}" for p in scaletta_sezione))
    if str(registro or "").strip():
        righe.append(
            "=== SCHEDA DI COERENZA (stato attuale del libro: non contraddirla, non ripetere ciò che è già stato detto, "
            "non usare ciò che non è ancora stato introdotto) ===\n" + _pulito(registro, 3000)
        )
    righe.append(direttive_struttura(tipo, apre, chiude, marcatore))
    return "\n\n".join(righe)


def istruzioni_chat_progetto() -> str:
    """Regole della chat guidata: compila da sola il progetto del libro (versione compatta)."""
    return """PROGETTO DEL LIBRO — COMPILALO SEMPRE TU, senza domande aggiuntive, dopo APPROFONDIMENTI:
- Romanzi: VERITÀ NASCOSTA: premessa in una frase e cosa è successo davvero, con la cronologia (2-5 righe).
  MAPPA DEI SEMI: 3-5 righe nel formato «- descrizione | compare: Capitolo N | si risolve: Capitolo M» (N e M tra 1 e 12).
- Biografia: solo VERITÀ NASCOSTA con fatti noti e cronologia reale.
- Saggi: TESI CENTRALE: tesi in una frase, problema del lettore e 5-8 idee chiave, una per riga.
- Manuali e Ricettario, Test Prep, Quiz, Meditazione: OBIETTIVI E PREREQUISITI: cosa saprà fare il lettore e cosa serve prima (3-6 righe).
Sii breve: questi campi si possono arricchire dopo. Mai dati o fatti reali inventati."""
