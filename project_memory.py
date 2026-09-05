"""Memoria unica del progetto editoriale.

Qui vive la protezione dei testi contro rerun, cambi di tab, pause e
ripristini. Il modulo non costruisce alcuna UI: riceve lo stato Streamlit dal
chiamante e conserva le stesse chiavi usate dalle versioni precedenti.
"""

from __future__ import annotations

from collections.abc import Callable, MutableMapping, Sequence
from typing import Any


CHIAVE_MEMORIA_SEZIONI = "memoria_sezioni_editor"
CHIAVE_MEMORIA_PROTETTA = "memoria_manoscritto_protetta"
CHIAVE_ARCHIVIO_STESURA_COMPLETA = "archivio_stesura_completa"
# Registro esclusivo della singola esecuzione di "Scrivi tutto il libro".
# Non è una quinta copia destinata all'utente: è la ricevuta anti-rerun che
# impedisce a un widget transitorio di far rigenerare una sezione già pagata.
CHIAVE_SEZIONI_CONFERMATE_JOB = "job_scrittura_sezioni_confermate"
CHIAVE_REGISTRO_SEZIONI = "registro_sezioni_manoscritto"
CHIAVE_SEZIONI_DA_REIDRATARE = "sezioni_editor_da_reidratare"
CHIAVE_SEZIONE_EDITOR_ATTIVA = "sezione_editor_attiva"
CHIAVE_SELETTORE_EDITOR = "sezione_editor_selezionata"
CHIAVE_VERSIONI_WIDGET_SEZIONI = "versioni_widget_sezioni"
CHIAVE_MEMORIA_SIDEBAR = "memoria_sidebar_editor"
CHIAVE_PROGETTO_UNICO = "progetto_editoriale_unico"

CAMPI_SALVATAGGIO_PROGETTO = {
    "titolo": "book_title",
    "autore": "book_author",
    "lingua": "editor_language",
    "genere": "book_genre",
    "tipologia_scrittura": "book_writing_style",
    "stile_racconto": "book_narrative_style",
    "punto_di_vista": "book_point_of_view",
    "obiettivo": "book_goal",
    "risultato_finale": "book_desired_result",
    "argomento": "book_plot",
    "approfondimenti": "book_further_details",
    "voce_personale": "book_personal_voice",
    "materiale_personale": "book_personal_material",
    "priorita_personali": "book_personal_priorities",
    "confini_personali": "book_personal_boundaries",
    "modalita_checkpoint": "book_personal_checkpoint_mode",
    "note_checkpoint": "book_personal_checkpoint_notes",
    "lunghezza": "profilo_lunghezza_stesura",
    "provider_ia": "provider_ia",
}


def memoria_progetto_unica(stato: MutableMapping[str, Any]) -> dict[str, Any]:
    """Restituisce la fotografia editoriale unica, riparando dati parziali."""
    progetto = stato.setdefault(CHIAVE_PROGETTO_UNICO, {})
    if not isinstance(progetto, dict):
        progetto = {}
        stato[CHIAVE_PROGETTO_UNICO] = progetto
    for nome in ("sidebar", "contenuti", "fonti", "immagini"):
        if not isinstance(progetto.get(nome), dict):
            progetto[nome] = {}
    progetto["indice"] = str(progetto.get("indice", "") or "")
    return progetto


def sidebar_memorizzata_corrente(stato: MutableMapping[str, Any]) -> dict[str, Any]:
    """Restituisce tutti i campi editoriali, anche dopo un rerun."""
    progetto = memoria_progetto_unica(stato)
    memoria = dict(progetto.get("sidebar", {}) or {})
    memoria.update(dict(stato.get(CHIAVE_MEMORIA_SIDEBAR, {}) or {}))
    for nome, chiave in CAMPI_SALVATAGGIO_PROGETTO.items():
        if chiave in stato:
            memoria[nome] = stato.get(chiave, "")
    stato[CHIAVE_MEMORIA_SIDEBAR] = dict(memoria)
    progetto["sidebar"] = dict(memoria)
    return memoria


def chiave_widget_sezione(stato: MutableMapping[str, Any], sezione: str, chiave_sezione: Callable[[str], str]) -> str:
    versione = int(stato.setdefault(CHIAVE_VERSIONI_WIDGET_SEZIONI, {}).get(sezione, 0))
    return f"{chiave_sezione(sezione)}_v{versione}"


def leggi_sezione_memorizzata(
    stato: MutableMapping[str, Any],
    sezione: str,
    chiave_sezione: Callable[[str], str],
    chiave_precedente: Callable[[str], str],
) -> str:
    """Legge una sezione dando priorità alla memoria stabile del progetto."""
    chiave = chiave_sezione(sezione)
    progetto = memoria_progetto_unica(stato)
    testo_unico = str(progetto.get("contenuti", {}).get(sezione, "") or "")
    if testo_unico.strip():
        stato.setdefault(CHIAVE_MEMORIA_SEZIONI, {})[sezione] = testo_unico
        stato.setdefault(CHIAVE_MEMORIA_PROTETTA, {})[sezione] = testo_unico
        stato[chiave] = testo_unico
        return testo_unico

    # Durante la stesura completa questa ricevuta ha priorità sullo stato dei
    # widget. Se un rerun ha temporaneamente svuotato una delle copie visive,
    # qui la ricostruiamo prima che la coda possa decidere di rigenerare la
    # stessa sezione e addebitare inutilmente una seconda chiamata.
    confermate = stato.get(CHIAVE_SEZIONI_CONFERMATE_JOB, {})
    testo_confermato = (
        str(confermate.get(sezione, "") or "")
        if isinstance(confermate, dict)
        else ""
    )
    if testo_confermato.strip():
        progetto["contenuti"][sezione] = testo_confermato
        stato.setdefault(CHIAVE_MEMORIA_SEZIONI, {})[sezione] = testo_confermato
        stato.setdefault(CHIAVE_MEMORIA_PROTETTA, {})[sezione] = testo_confermato
        stato.setdefault(CHIAVE_ARCHIVIO_STESURA_COMPLETA, {})[sezione] = testo_confermato
        stato[chiave] = testo_confermato
        return testo_confermato
    memoria = stato.setdefault(CHIAVE_MEMORIA_SEZIONI, {})
    memoria_protetta = stato.setdefault(CHIAVE_MEMORIA_PROTETTA, {})
    valore_widget = stato.get(chiave, "") or stato.get(chiave_precedente(sezione), "")
    if not str(memoria.get(sezione, "")).strip() and str(valore_widget).strip():
        memoria[sezione] = valore_widget
        memoria_protetta[sezione] = valore_widget
    if not str(memoria.get(sezione, "")).strip() and str(memoria_protetta.get(sezione, "")).strip():
        memoria[sezione] = memoria_protetta[sezione]
    valore_memoria = memoria.get(sezione, "")
    if str(valore_memoria).strip():
        progetto["contenuti"][sezione] = valore_memoria
        return valore_memoria
    archivio = stato.setdefault(CHIAVE_ARCHIVIO_STESURA_COMPLETA, {})
    testo = memoria_protetta.get(sezione, "") or archivio.get(sezione, "") or valore_widget or ""
    if str(testo).strip():
        progetto["contenuti"][sezione] = testo
    return testo


def scrivi_sezione_memorizzata(
    stato: MutableMapping[str, Any], sezione: str, contenuto: str, chiave_sezione: Callable[[str], str]
) -> str:
    """Scrive insieme nell'archivio del progetto, nella copia protetta e nel widget."""
    testo = contenuto or ""
    progetto = memoria_progetto_unica(stato)
    memoria = stato.setdefault(CHIAVE_MEMORIA_SEZIONI, {})
    precedente = str(progetto.get("contenuti", {}).get(sezione, "") or "")
    progetto["contenuti"][sezione] = testo
    memoria[sezione] = testo
    stato.setdefault(CHIAVE_MEMORIA_PROTETTA, {})[sezione] = testo
    stato[chiave_sezione(sezione)] = testo
    if str(testo) != precedente:
        versioni = stato.setdefault(CHIAVE_VERSIONI_WIDGET_SEZIONI, {})
        versioni[sezione] = int(versioni.get(sezione, 0)) + 1
    registro = stato.setdefault(CHIAVE_REGISTRO_SEZIONI, [])
    if sezione not in registro:
        registro.append(sezione)
    da_reidratare = set(stato.get(CHIAVE_SEZIONI_DA_REIDRATARE, []) or [])
    da_reidratare.add(sezione)
    stato[CHIAVE_SEZIONI_DA_REIDRATARE] = list(da_reidratare)
    return testo


def scrivi_sezione_stesura_completa(
    stato: MutableMapping[str, Any], sezione: str, contenuto: str, chiave_sezione: Callable[[str], str]
) -> str:
    testo = scrivi_sezione_memorizzata(stato, sezione, contenuto, chiave_sezione)
    stato.setdefault(CHIAVE_ARCHIVIO_STESURA_COMPLETA, {})[sezione] = testo
    confermate = stato.get(CHIAVE_SEZIONI_CONFERMATE_JOB)
    if isinstance(confermate, dict) and str(testo or "").strip():
        confermate[sezione] = testo
    return testo


def contenuto_memorizzato_puro(
    stato: MutableMapping[str, Any], sezione: str, chiave_precedente: Callable[[str], str]
) -> str:
    contenuto_unico = memoria_progetto_unica(stato).get("contenuti", {}).get(sezione, "")
    if str(contenuto_unico).strip():
        return contenuto_unico
    confermate = stato.get(CHIAVE_SEZIONI_CONFERMATE_JOB, {})
    contenuto_confermato = (
        confermate.get(sezione, "") if isinstance(confermate, dict) else ""
    )
    if str(contenuto_confermato).strip():
        return contenuto_confermato
    contenuto = stato.setdefault(CHIAVE_MEMORIA_SEZIONI, {}).get(sezione, "")
    if not str(contenuto).strip():
        contenuto = stato.setdefault(CHIAVE_MEMORIA_PROTETTA, {}).get(sezione, "")
    if not str(contenuto).strip():
        contenuto = stato.setdefault(CHIAVE_ARCHIVIO_STESURA_COMPLETA, {}).get(sezione, "")
    if not str(contenuto).strip():
        contenuto = stato.get(chiave_precedente(sezione), "")
    return contenuto or ""


def elenco_sezioni_progetto(
    stato: MutableMapping[str, Any], sezioni_base: Sequence[str], sezione_dismessa: Callable[[str], bool]
) -> list[str]:
    """Unisce indice e memoria, senza perdere testi già generati."""
    progetto = memoria_progetto_unica(stato)
    risultato: list[str] = []
    for sezione in [
        *(sezioni_base or []),
        *progetto.get("contenuti", {}).keys(),
        *stato.get(CHIAVE_REGISTRO_SEZIONI, []),
        *dict(stato.get(CHIAVE_MEMORIA_SEZIONI, {}) or {}).keys(),
        *dict(stato.get(CHIAVE_MEMORIA_PROTETTA, {}) or {}).keys(),
        *dict(stato.get(CHIAVE_ARCHIVIO_STESURA_COMPLETA, {}) or {}).keys(),
    ]:
        if sezione and not sezione_dismessa(sezione) and sezione not in risultato:
            risultato.append(sezione)
    return risultato


def sincronizza_modifica_manuale(
    stato: MutableMapping[str, Any],
    sezione: str,
    chiave_da_leggere: str,
    chiave_sezione: Callable[[str], str],
) -> None:
    """Salva una modifica reale dell'editor, mai un widget assente.

    Durante la stesura automatica Streamlit cambia sezione e ricrea i campi
    dell'editor. In quel passaggio la chiave del campo precedente può non
    essere ancora presente nello stato: leggerla come stringa vuota farebbe
    sembrare che l'utente abbia cancellato il testo e potrebbe eliminare una
    sezione già generata, come la Prefazione. Una chiave assente non è quindi
    mai una cancellazione esplicita. Se il campo esiste, invece, anche un
    contenuto vuoto continua a rappresentare la scelta volontaria dell'utente
    di svuotare la sezione.
    """
    if chiave_da_leggere not in stato:
        return

    contenuto = stato.get(chiave_da_leggere, "")
    confermate = stato.get(CHIAVE_SEZIONI_CONFERMATE_JOB, {})
    testo_confermato = (
        str(confermate.get(sezione, "") or "")
        if isinstance(confermate, dict)
        else ""
    )
    job_in_corso = bool(
        stato.get("job_scrittura_attivo")
        or stato.get("job_scrittura_pausa")
        or stato.get("job_scrittura_in_attesa")
    )
    if not str(contenuto or "").strip() and testo_confermato.strip() and job_in_corso:
        # Un campo vuoto durante il cambio automatico non è un comando
        # dell'utente: ripristina la sezione confermata e non toccare la coda.
        scrivi_sezione_memorizzata(stato, sezione, testo_confermato, chiave_sezione)
        stato.setdefault(CHIAVE_ARCHIVIO_STESURA_COMPLETA, {})[sezione] = testo_confermato
        return

    scrivi_sezione_memorizzata(stato, sezione, contenuto, chiave_sezione)
    archivio = stato.setdefault(CHIAVE_ARCHIVIO_STESURA_COMPLETA, {})
    if sezione in archivio:
        if str(contenuto or "").strip():
            archivio[sezione] = contenuto
        else:
            archivio.pop(sezione, None)
    if not str(contenuto or "").strip():
        memoria_progetto_unica(stato).get("contenuti", {}).pop(sezione, None)
        if isinstance(confermate, dict):
            confermate.pop(sezione, None)


def prepara_sezione_editor_selezionata(
    stato: MutableMapping[str, Any],
    chiave_sezione: Callable[[str], str],
    chiave_precedente: Callable[[str], str],
) -> None:
    precedente = stato.get(CHIAVE_SEZIONE_EDITOR_ATTIVA)
    if precedente:
        sincronizza_modifica_manuale(
            stato, precedente, chiave_widget_sezione(stato, precedente, chiave_sezione), chiave_sezione
        )
    selezionata = stato.get(CHIAVE_SELETTORE_EDITOR)
    if selezionata:
        stato[chiave_sezione(selezionata)] = contenuto_memorizzato_puro(stato, selezionata, chiave_precedente)
        stato[CHIAVE_SEZIONE_EDITOR_ATTIVA] = selezionata


def reidrata_sezioni_memorizzate(
    stato: MutableMapping[str, Any],
    sezioni: Sequence[str],
    chiave_sezione: Callable[[str], str],
    chiave_precedente: Callable[[str], str],
) -> None:
    progetto = memoria_progetto_unica(stato)
    memoria_unica = progetto.get("contenuti", {}) or {}
    memoria = stato.get(CHIAVE_MEMORIA_SEZIONI, {}) or {}
    memoria_protetta = stato.get(CHIAVE_MEMORIA_PROTETTA, {}) or {}
    archivio = stato.get(CHIAVE_ARCHIVIO_STESURA_COMPLETA, {}) or {}
    da_reidratare = set(stato.get(CHIAVE_SEZIONI_DA_REIDRATARE, []) or [])
    for sezione in sezioni:
        contenuto = memoria_unica.get(sezione, "") or memoria.get(sezione)
        if not str(contenuto or "").strip():
            contenuto = memoria_protetta.get(sezione, "")
        if not str(contenuto or "").strip():
            contenuto = archivio.get(sezione, "")
        chiave = chiave_sezione(sezione)
        if not str(contenuto or "").strip():
            contenuto = stato.get(chiave_precedente(sezione), "")
        if str(contenuto or "").strip() and (sezione in da_reidratare or not str(stato.get(chiave, "")).strip()):
            stato[chiave] = contenuto
            memoria[sezione] = contenuto
            memoria_protetta[sezione] = contenuto
            progetto["contenuti"][sezione] = contenuto
            da_reidratare.discard(sezione)
    if da_reidratare:
        stato[CHIAVE_SEZIONI_DA_REIDRATARE] = list(da_reidratare)
    else:
        stato.pop(CHIAVE_SEZIONI_DA_REIDRATARE, None)
