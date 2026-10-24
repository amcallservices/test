"""Trascrizione dei brevi messaggi vocali delle due chat editoriali."""

from io import BytesIO
import wave

MODELLO_TRASCRIZIONE = "gpt-transcribe"
DURATA_MASSIMA_SECONDI = 90
DIMENSIONE_MASSIMA_BYTE = 25 * 1024 * 1024


def durata_registrazione_wav(audio: bytes) -> float:
    """Valida la registrazione prima di inviarla al servizio di trascrizione."""
    if not audio or len(audio) > DIMENSIONE_MASSIMA_BYTE:
        raise ValueError("dimensione_audio_non_valida")
    try:
        with wave.open(BytesIO(audio), "rb") as registrazione:
            frequenza = registrazione.getframerate()
            durata = registrazione.getnframes() / frequenza if frequenza else 0
    except (EOFError, wave.Error, ZeroDivisionError) as exc:
        raise ValueError("formato_audio_non_valido") from exc
    if durata < 0.4:
        raise ValueError("audio_troppo_breve")
    if durata > DURATA_MASSIMA_SECONDI:
        raise ValueError("audio_troppo_lungo")
    return durata


def trascrivi_registrazione(audio: bytes, api_key: str, *, post=None) -> tuple[str, float]:
    """Restituisce testo nella lingua parlata senza salvare il file audio."""
    durata = durata_registrazione_wav(audio)
    if not api_key:
        raise ValueError("chiave_api_assente")
    if post is None:
        import requests
        post = requests.post
    risposta = post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {api_key}"},
        data={"model": MODELLO_TRASCRIZIONE},
        files={"file": ("messaggio-vocale.wav", audio, "audio/wav")},
        timeout=90,
    )
    risposta.raise_for_status()
    testo = str(risposta.json().get("text", "") or "").strip()
    if not testo:
        raise ValueError("trascrizione_vuota")
    return testo, durata
