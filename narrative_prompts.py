"""Istruzioni di stesura dedicate alla narrativa.

Il modulo non usa Streamlit e non chiama provider AI: costruisce soltanto
testi per i prompt e legge i dati che l'autore scrive nel progetto
(narratore, tempo verbale, scaletta, scheda personaggi). In questo modo le
regole dei romanzi restano separate da quelle di manuali e saggi e possono
essere provate in isolamento.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from narrative_engine import genere_narrativo


NARRATORI = (
    "Terza persona vicina a un personaggio",
    "Prima persona (il protagonista racconta)",
    "Terza persona onnisciente",
    "Terza persona a più punti di vista (uno per scena)",
)
NARRATORE_PREDEFINITO = NARRATORI[0]

TEMPI_VERBALI = (
    "Passato (passato remoto e imperfetto)",
    "Presente",
)
TEMPO_PREDEFINITO = TEMPI_VERBALI[0]

_DIRETTIVE_NARRATORE = {
    NARRATORI[0]: (
        "Racconta in terza persona restando vicino a un solo personaggio per scena: il lettore sa, "
        "vede e sente solo ciò che sa, vede e sente quel personaggio. Non entrare nei pensieri degli altri."
    ),
    NARRATORI[1]: (
        "Racconta in prima persona con la voce del protagonista: lessico, giudizi e percezioni sono i suoi. "
        "Il narratore non può sapere ciò che non ha visto, sentito o dedotto."
    ),
    NARRATORI[2]: (
        "Racconta in terza persona con un narratore che conosce pensieri e destini di tutti, ma usa questa "
        "conoscenza con misura: scegli in ogni scena su chi concentrarti e non saltare da una mente all'altra "
        "nella stessa frase."
    ),
    NARRATORI[3]: (
        "Racconta in terza persona alternando il punto di vista tra personaggi, ma uno solo per scena. "
        "Se cambi personaggio di riferimento, fallo solo con uno stacco netto di scena."
    ),
}
_DIRETTIVE_TEMPO = {
    TEMPI_VERBALI[0]: "Usa i tempi del passato (passato remoto per le azioni, imperfetto per sfondi e abitudini) in modo coerente.",
    TEMPI_VERBALI[1]: "Usa il presente narrativo in modo coerente; il passato solo per ricordi chiaramente segnalati.",
}


def direttiva_voce_narrante(narratore: str, tempo: str) -> str:
    """Traduce le scelte dell'autore in una regola chiara per il modello."""
    narratore = narratore if narratore in _DIRETTIVE_NARRATORE else NARRATORE_PREDEFINITO
    tempo = tempo if tempo in _DIRETTIVE_TEMPO else TEMPO_PREDEFINITO
    return (
        f"Narratore: {narratore}. {_DIRETTIVE_NARRATORE[narratore]}\n"
        f"Tempo verbale: {tempo}. {_DIRETTIVE_TEMPO[tempo]}\n"
        "Mantieni narratore e tempo identici in tutto il libro, salvo un cambio esplicito voluto dall'autore."
    )


def descrizione_punto_di_vista(narratore: str, tempo: str) -> str:
    """Valore breve usato dove il resto dell'app si aspetta il «punto di vista»."""
    narratore = narratore if narratore in _DIRETTIVE_NARRATORE else NARRATORE_PREDEFINITO
    tempo = tempo if tempo in _DIRETTIVE_TEMPO else TEMPO_PREDEFINITO
    return f"{narratore} · {tempo}"


def _pulito(valore, limite: int) -> str:
    testo = str(valore or "").strip()
    return testo[:limite].rstrip() + ("…" if len(testo) > limite else "")


def normalizza_narratore(valore: str) -> str:
    """Riconosce il narratore anche se la chat lo scrive in forma breve."""
    testo = re.sub(r"[*_`]", "", str(valore or "")).strip().casefold()
    if not testo:
        return ""
    for opzione in NARRATORI:
        if testo == opzione.casefold():
            return opzione
    # Forme brevi in tutte le lingue del sito (la chat può rispondere
    # con le parole dell'utente invece del valore tecnico).
    prima = ("prima persona", "first person", "primera persona", "première personne", "premiere personne",
             "ich-erzähler", "ich-erzahler", "erste person", "persoana întâi", "persoana intai",
             "первое лицо", "первого лица", "ضمير المتكلم", "第一人称")
    onnisciente = ("onniscien", "omniscien", "allwissend", "всезнающ", "عليم", "全知")
    multipli = ("più punti", "piu punti", "multipl", "alterna", "varios puntos", "plusieurs points",
                "mehrere perspektiv", "mehreren perspektiv", "mai multe perspective", "нескольк", "متعدد", "多视角", "多个视角")
    terza = ("terza persona", "third person", "tercera persona", "troisième personne", "troisieme personne",
             "er-erzähl", "sie-erzähl", "personale", "dritte person", "persoana a treia", "третье лицо",
             "третьего лица", "ضمير الغائب", "第三人称")
    if any(chiave in testo for chiave in prima):
        return NARRATORI[1]
    if any(chiave in testo for chiave in onnisciente):
        return NARRATORI[2]
    if any(chiave in testo for chiave in multipli):
        return NARRATORI[3]
    if any(chiave in testo for chiave in terza):
        return NARRATORI[0]
    return ""


def normalizza_tempo_verbale(valore: str) -> str:
    """Riconosce il tempo verbale anche se la chat lo scrive in forma breve."""
    testo = re.sub(r"[*_`]", "", str(valore or "")).strip().casefold()
    if not testo:
        return ""
    for opzione in TEMPI_VERBALI:
        if testo == opzione.casefold():
            return opzione
    presente = ("present", "présent", "gegenwart", "präsens", "prasens", "prezent", "настоящ", "المضارع", "الحاضر", "现在时", "现在")
    passato = ("passat", "past", "remoto", "pasado", "pretérito", "passé", "passe", "vergangen", "präteritum",
               "prateritum", "trecut", "прошедш", "الماضي", "过去")
    if any(testo.startswith(chiave) or chiave in testo for chiave in presente):
        return TEMPI_VERBALI[1]
    if any(testo.startswith(chiave) or chiave in testo for chiave in passato):
        return TEMPI_VERBALI[0]
    return ""


def istruzioni_chat_romanzi() -> str:
    """Regole aggiuntive per la chat guidata che compila la sidebar (versione compatta)."""
    narratori = "; ".join(NARRATORI)
    tempi = "; ".join(TEMPI_VERBALI)
    return f"""ROMANZI E BIOGRAFIE (Romanzo Rosa, Thriller / Noir, Fantasy, Fantascienza, Narrativo, Romanzo Classico, Contemporaneo, Biografia)
Scrivi PUNTO DI VISTA: Impersonale / Terza Persona (Distaccato, analitico, oggettivo) e, subito dopo, queste righe obbligatorie:
NARRATORE: una sola opzione tra {narratori}
TEMPO VERBALE: una sola opzione tra {tempi}
Se l'utente non li indica, scegli tu (di norma «{NARRATORE_PREDEFINITO}» e «{TEMPO_PREDEFINITO}») senza fare domande.
PERSONAGGI E MONDO: compilalo sempre tu, una riga per personaggio «- Nome Cognome: ruolo, età, carattere, cosa vuole, cosa teme»,
più i luoghi principali; conserva ciò che ha detto l'utente. Nella Biografia solo persone e fatti reali noti."""


# ---------------------------------------------------------------------------
# Scaletta per sezione
# ---------------------------------------------------------------------------

# Tollera intestazioni decorate dal modello, per esempio "**[Capitolo 1: …]**".
_INTESTAZIONE_SCALETTA = re.compile(r"^[\s#*_]*\[(.+?)\][\s*_:]*$")


def _normalizza_titolo(titolo: str) -> str:
    return re.sub(r"\s+", " ", str(titolo or "")).strip().casefold()


def leggi_scaletta(testo: str) -> dict[str, list[str]]:
    """Legge la scaletta scritta nel formato:

        [Capitolo 1: Il lago]
        - Marco arriva alla casa
        - trova la lettera

    Restituisce titolo normalizzato → punti. Le righe vuote o senza
    intestazione precedente vengono ignorate.
    """
    risultato: dict[str, list[str]] = {}
    corrente = ""
    for riga in str(testo or "").splitlines():
        intestazione = _INTESTAZIONE_SCALETTA.match(riga)
        if intestazione:
            corrente = _normalizza_titolo(intestazione.group(1))
            risultato.setdefault(corrente, [])
            continue
        punto = re.sub(r"^\s*(?:[-•*]|\d+[.)])\s*", "", riga).strip()
        if corrente and punto:
            risultato[corrente].append(punto)
    return {titolo: punti for titolo, punti in risultato.items() if punti}


def scaletta_della_sezione(testo_scaletta: str, sezione: str) -> list[str]:
    """Punti della scaletta per una voce dell'indice, se l'autore li ha scritti."""
    return leggi_scaletta(testo_scaletta).get(_normalizza_titolo(sezione), [])


def prompt_genera_scaletta(
    *,
    sezioni: Sequence[str],
    indice: str,
    titolo: str,
    genere: str,
    trama: str,
    obiettivo: str,
    scheda_personaggi: str,
    voce_narrante: str,
    lingua: str,
    scaletta_esistente: str = "",
) -> str:
    """Chiede al modello i punti chiave di ogni scena, prima della stesura."""
    elenco = "\n".join(f"[{sezione}]" for sezione in sezioni)
    gia_scritte = leggi_scaletta(scaletta_esistente)
    da_conservare = [s for s in sezioni if _normalizza_titolo(s) in gia_scritte]
    nota_conservazione = ""
    if da_conservare:
        nota_conservazione = (
            "\nL'autore ha già scritto la scaletta di alcune voci: riportala identica e completa solo le altre.\n"
            f"SCALETTA GIÀ SCRITTA DALL'AUTORE:\n{_pulito(scaletta_esistente, 6000)}\n"
        )
    return f"""Prepara la SCALETTA del romanzo '{titolo}' ({genere}), in {lingua}.

TRAMA E PREMESSA:
{_pulito(trama, 2500)}

OBIETTIVO DEL LIBRO: {_pulito(obiettivo, 400)}
VOCE NARRANTE: {voce_narrante}

PERSONAGGI E MONDO (canone dell'autore):
{_pulito(scheda_personaggi, 3000) or "Non ancora definiti: ricavali dalla trama senza contraddirla."}

INDICE COMPLETO:
{_pulito(indice, 5000)}
{nota_conservazione}
Per OGNUNA delle voci seguenti scrivi da 3 a 6 punti brevi (massimo 25 parole ciascuno):
chi è in scena, dove, che cosa vuole il personaggio, quale ostacolo incontra, che cosa cambia
e con quale situazione concreta si chiude la scena. Ogni voce deve far avanzare la storia
rispetto alla precedente; non ripetere eventi già assegnati ad altre voci. Le Parti possono
avere 2-3 punti. Mantieni la coerenza con trama, personaggi e voce narrante.

Rispondi SOLO in questo formato, riportando ogni titolo esattamente come scritto tra parentesi quadre:
[Titolo della voce]
- punto
- punto

VOCI:
{elenco}
"""


# ---------------------------------------------------------------------------
# Scheda personaggi e mondo
# ---------------------------------------------------------------------------

MODELLO_SCHEDA_PERSONAGGI = """PERSONAGGI
- Nome: ruolo, età, aspetto, carattere, che cosa vuole, che cosa teme
- Nome: …

RELAZIONI
- Nome e Nome: rapporto

LUOGHI E MONDO
- Luogo: descrizione, regole da rispettare

CRONOLOGIA E FATTI GIÀ STABILITI
- …"""


def prompt_aggiorna_scheda(
    *,
    scheda_attuale: str,
    capitoli: Sequence[tuple[str, str]],
    trama: str,
    lingua: str,
) -> str:
    """Chiede di aggiornare la scheda leggendo i capitoli già scritti.

    Il testo dei capitoli è limitato per contenere il costo: per ogni voce
    si usano inizio e fine, dove di norma compaiono personaggi ed esiti.
    """
    blocchi = []
    for titolo, testo in capitoli:
        testo = str(testo or "").strip()
        if not testo:
            continue
        estratto = testo if len(testo) <= 1600 else f"{testo[:700]}\n[…]\n{testo[-900:]}"
        blocchi.append(f"### {titolo}\n{estratto}")
    capitoli_testo = "\n\n".join(blocchi)[:24000]
    return f"""Aggiorna la scheda personaggi e mondo di un romanzo, in {lingua}.

TRAMA: {_pulito(trama, 1500)}

SCHEDA ATTUALE (scritta o approvata dall'autore: ciò che contiene è canone e non va cambiato,
salvo che i capitoli mostrino chiaramente un'evoluzione):
{_pulito(scheda_attuale, 5000) or "(vuota)"}

CAPITOLI GIÀ SCRITTI:
{capitoli_testo}

Restituisci la scheda completa aggiornata, nello stesso formato, con intestazioni e contenuti
scritti in {lingua}:
{MODELLO_SCHEDA_PERSONAGGI}

Regole: aggiungi solo personaggi, relazioni, luoghi e fatti che compaiono davvero nei capitoli;
non inventare età, aspetto o passato non dichiarati; non riassumere la trama capitolo per capitolo;
massimo 600 parole. Nessun commento prima o dopo la scheda."""


# ---------------------------------------------------------------------------
# Prompt di sistema e blocco di sezione per la narrativa
# ---------------------------------------------------------------------------

def system_prompt_narrativa(
    *,
    lingua: str,
    titolo: str,
    genere: str,
    tipologia: str,
    stile_racconto: str,
    ritmo: str,
    descrizione_ritmo: str,
    obiettivo: str,
    voce_narrante: str,
    regole_genere: str,
    modulo_lunghezza: str,
    modulo_fonti: str = "",
    specifica_editoriale: str = "",
) -> str:
    """Prompt di sistema per romanzi e biografie.

    Sostituisce, solo per questi generi, le direttive pensate per i manuali
    (checklist, procedure numerate, "esperto con 30 anni di esperienza",
    divieto di ripetere parole chiave, neuromarketing).
    """
    nota_biografia = ""
    if "biograf" in str(genere or "").casefold():
        nota_biografia = (
            "\n=== FEDELTÀ AI FATTI (BIOGRAFIA) ===\n"
            "Racconta con tecnica narrativa, ma non inventare eventi, dialoghi attribuiti a persone reali, date o "
            "testimonianze. Dove i fatti non sono noti, resta sobrio e non drammatizzare.\n"
        )
    return f"""Sei un romanziere madrelingua {lingua}, con una prosa curata da libro pubblicato.
Stai scrivendo '{titolo}', genere {genere}.

=== VOCE NARRANTE (VINCOLANTE) ===
{voce_narrante}

=== IDENTITÀ DEL LIBRO ===
- Tipologia di scrittura: {tipologia}
- Stile di racconto: {stile_racconto}
- Ritmo: {ritmo}. {descrizione_ritmo}
- Effetto da ottenere sul lettore: {obiettivo}
- Regole del genere: {regole_genere}
{nota_biografia}
=== MESTIERE DELLA SCENA ===
- Ogni sezione è una scena (o una breve sequenza di scene) in cui un personaggio vuole qualcosa, incontra
  un ostacolo e ne esce in una situazione diversa da quella iniziale.
- Fai accadere gli eventi davanti al lettore con azioni, dialoghi e dettagli concreti; riassumi solo i
  passaggi di raccordo. Il narratore commenta poco e non spiega il significato di ciò che accade.
- Dialoghi: battute brevi e naturali, con sottotesto; ogni personaggio parla a modo suo. Usa la
  punteggiatura del dialogo propria della lingua {lingua}, sempre la stessa in tutto il libro.
- Scegli pochi dettagli sensoriali precisi, non elenchi dei cinque sensi.
- Varia lunghezza di frasi e paragrafi secondo la tensione: più brevi nell'azione, più distesi nella quiete.
- Evita formule usurate (come se, sembrava, per la prima volta, non era soltanto, trattenne il respiro,
  strinse la mandibola, abbassò lo sguardo) e reazioni fisiche stereotipate.
- Niente morale finale, niente riassunto di ciò che il personaggio ha capito, niente chiusa solenne o
  cliffhanger artificiale in ogni sezione.

=== CONTINUITÀ (CRITICA) ===
- La scheda personaggi e mondo, la scaletta e la memoria delle sezioni precedenti sono canone: nomi,
  aspetto, età, relazioni, luoghi, regole del mondo e cronologia non cambiano senza una causa mostrata.
- Nomi, luoghi e motivi ricorrenti DEVONO tornare con le stesse parole: non sostituirli con sinonimi.
- Riparti da dove si è chiusa la sezione precedente. Non ripetere eventi già raccontati e non riassumere
  le scene precedenti.
- Non anticipare scene assegnate alle voci successive dell'indice.

=== CAPITOLI, SOTTOCAPITOLI E PARTI ===
- Un capitolo che ha sottocapitoli è solo una breve soglia: le scene appartengono ai sottocapitoli.
- Un sottocapitolo o un capitolo senza sottocapitoli sviluppa per intero la scena assegnata.

{modulo_lunghezza}

=== FORMATO ===
- Restituisci solo il testo del libro: nessun titolo della sezione, nessun Markdown, nessun commento,
  piano, nota o spiegazione sul lavoro svolto.
- Nessun URL, citazione o riferimento bibliografico.
- Termina con una frase completa.
{modulo_fonti}
{specifica_editoriale}
"""


def blocco_sezione_narrativa(
    *,
    sezione: str,
    scaletta_sezione: Sequence[str],
    scheda_personaggi: str,
) -> str:
    """Dati specifici della scena corrente da inserire nel prompt di sezione."""
    righe = ["=== SCENA DA SCRIVERE ==="]
    if scaletta_sezione:
        righe.append(f"Scaletta approvata dall'autore per «{sezione}» (segui questi punti in ordine, sviluppandoli in scena):")
        righe.extend(f"- {punto}" for punto in scaletta_sezione)
    else:
        righe.append(
            f"Per «{sezione}» non c'è una scaletta: ricava la scena dal titolo, dalla trama e da dove si è "
            "chiusa la sezione precedente, con un avanzamento reale della storia."
        )
    scheda = _pulito(scheda_personaggi, 4500)
    if scheda:
        righe.append("\n=== SCHEDA PERSONAGGI E MONDO (CANONE DELL'AUTORE) ===\n" + scheda)
    return "\n".join(righe)


__all__ = [
    "MODELLO_SCHEDA_PERSONAGGI", "NARRATORE_PREDEFINITO", "NARRATORI", "TEMPI_VERBALI", "TEMPO_PREDEFINITO",
    "blocco_sezione_narrativa", "descrizione_punto_di_vista", "direttiva_voce_narrante", "genere_narrativo",
    "istruzioni_chat_romanzi", "normalizza_narratore", "normalizza_tempo_verbale",
    "leggi_scaletta", "prompt_aggiorna_scheda", "prompt_genera_scaletta", "scaletta_della_sezione",
    "system_prompt_narrativa",
]
