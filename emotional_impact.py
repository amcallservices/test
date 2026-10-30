"""Istruzioni locali per un coinvolgimento emotivo naturale nella stesura.

Il modulo non conserva dati, non chiama provider AI e non interpreta il testo
già prodotto. Trasforma soltanto il brief già disponibile in direttive brevi
per il prompt della sezione corrente.
"""

from __future__ import annotations

from typing import Any


GENERI_NARRATIVI = frozenset({
    "Romanzo Rosa", "Thriller / Noir", "Fantasy", "Fantascienza", "Narrativo",
    "Romanzo Classico", "Contemporaneo", "Biografia",
})


def _testo(valore: Any, limite: int = 520) -> str:
    return " ".join(str(valore or "").split())[:limite]


def _narrativo(genere: str) -> bool:
    valore = _testo(genere).casefold()
    return valore in {genere.casefold() for genere in GENERI_NARRATIVI} or "romanzo" in valore


def _profilo_genere(genere: str) -> str:
    valore = _testo(genere).casefold()
    if "thriller" in valore or "noir" in valore:
        return "Costruisci curiosità, rischio e sospetto soltanto dai fatti già previsti: non inventare indizi, minacce o rivelazioni."
    if "rosa" in valore:
        return "Fai maturare attrazione, vulnerabilità e incomprensioni attraverso scelte e dialoghi credibili, senza dichiarazioni sentimentali prefabbricate."
    if "fantasy" in valore or "fantascienza" in valore:
        return "Lascia emergere meraviglia, pericolo e legami dai dettagli del mondo e dalle decisioni, senza contraddire le sue regole già stabilite."
    if "storico" in valore:
        return "Rendi credibili reazioni e conflitti nel contesto storico e culturale indicato, senza psicologie contemporanee inserite a forza."
    if "biografia" in valore:
        return "Mantieni sobrietà e fedeltà ai fatti disponibili: l'interesse nasce da decisioni, conseguenze e contesto, non da drammatizzazioni inventate."
    if "classico" in valore or "contemporaneo" in valore:
        return "Privilegia sfumature, ambivalenze e sottotesto; ogni passaggio emotivo deve nascere dalla situazione concreta."
    return "Sviluppa conflitti, relazioni e conseguenze con misura, rispettando la personalità dei personaggi e il canone già confermato."


def istruzioni_impatto_emotivo(
    *,
    sezione: str,
    genere: str,
    tipologia: str,
    stile: str,
    obiettivo: str,
    brief_personale: str = "",
    contesto_narrativo: str = "",
    ruolo_sezione: str = "",
) -> str:
    """Restituisce un'aggiunta pronta per il prompt, senza effetti collaterali.

    La coerenza con indice, memoria e indicazioni esplicite dell'autore resta
    sempre prioritaria. Nei libri non narrativi l'impatto è chiarezza utile,
    non teatralizzazione.
    """
    titolo = _testo(sezione, 220)
    obiettivo = _testo(obiettivo, 360)
    tipologia = _testo(tipologia, 120)
    stile = _testo(stile, 120)
    personale = _testo(brief_personale, 360)
    contesto = _testo(contesto_narrativo, 420)

    if not _narrativo(genere):
        righe = [
            "=== COINVOLGIMENTO DEL LETTORE ===",
            "Per questo testo non narrativo, coinvolgi con chiarezza, esempi pertinenti, domande utili e applicazioni concrete.",
            "Non introdurre scene, conflitti, tensione o emozioni artificiali; precisione, sicurezza e struttura richiesta restano prioritarie.",
            "Non alterare ricette, quiz, esercizi, procedure o contenuti tecnici previsti dall'indice.",
        ]
        if obiettivo:
            righe.append(f"Mantieni il focus sul risultato dichiarato: {obiettivo}")
        return "\n".join(righe)

    righe = [
        "=== EMOTIONAL IMPACT ENGINE — ISTRUZIONI INTERNE ===",
        "Subordinato a indice, canone e scelte dell'autore: non creare eventi, personaggi, indizi, ricordi o rivelazioni.",
        f"Per «{titolo}», coerente con tipologia «{tipologia}» e stile «{stile}», valuta internamente emozione plausibile, risposta del lettore, conflitto desiderio/timore, cambiamento, sottotesto e conseguenza; non stampare etichette o piani.",
        "Mostra soprattutto con decisioni, azioni, dialoghi e dettagli concreti; usa narrazione diretta solo quando è più chiara. Le reazioni dipendono dai personaggi, non da gesti standard.",
        "Alterna intensità e quiete secondo il ritmo: non drammatizzare scene ordinarie, moralizzare, chiudere sempre solennemente o creare cliffhanger artificiali.",
        "Evita scorciatoie ripetitive (come se, sembrava, per la prima volta, non era soltanto, silenzi o reazioni fisiche stereotipate): usale soltanto se specifiche e non ricorrenti.",
        "Mantieni dialoghi naturali, ambivalenze e spazio per l'interpretazione; non trasformare i personaggi in psicologi o moralisti.",
        _profilo_genere(genere),
    ]
    if ruolo_sezione == "parte":
        righe.append("Essendo una Parte, costruisci una scena breve e compiuta: non spiegare al lettore che cosa dovrebbe provare o capire.")
    if obiettivo:
        righe.append(f"L'effetto emotivo deve restare al servizio dell'obiettivo del libro: {obiettivo}")
    if personale:
        righe.append("Le istruzioni personali dell'autore prevalgono su questo modulo e vanno rispettate senza attribuirgli esperienze non dichiarate.")
    if contesto:
        righe.append("Usa il contesto narrativo già fornito come canone: non duplicare o contraddire fatti, relazioni e conseguenze confermate.")
    return "\n".join(righe)
