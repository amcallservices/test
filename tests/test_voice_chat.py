"""Voice messages remain editable and never consume a second user credit."""

import ast
from io import BytesIO
from pathlib import Path
import unittest
import wave

from voice_chat import durata_registrazione_wav, trascrivi_registrazione


def wav_silenzioso(secondi: int) -> bytes:
    dati = BytesIO()
    with wave.open(dati, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(16000)
        audio.writeframes(b"\0\0" * 16000 * secondi)
    return dati.getvalue()


class VoiceChatTests(unittest.TestCase):
    def test_valid_wav_is_sent_for_transcription(self):
        audio = wav_silenzioso(1)
        richieste = []

        class Risposta:
            def raise_for_status(self):
                return None

            def json(self):
                return {"text": "  La mia idea di libro  "}

        def post(url, **opzioni):
            richieste.append((url, opzioni))
            return Risposta()

        testo, durata = trascrivi_registrazione(audio, "chiave-test", post=post)
        self.assertEqual((testo, durata), ("La mia idea di libro", 1.0))
        self.assertEqual(richieste[0][1]["data"]["model"], "gpt-transcribe")
        self.assertEqual(richieste[0][1]["files"]["file"][1], audio)

    def test_invalid_or_long_audio_stops_before_api_call(self):
        with self.assertRaises(ValueError):
            durata_registrazione_wav(b"non un wav")
        with self.assertRaises(ValueError):
            durata_registrazione_wav(wav_silenzioso(91))

    def test_audio_cost_uses_duration_and_gpt_provider(self):
        tree = ast.parse((Path(__file__).resolve().parents[1] / "commercial_layer.py").read_text(encoding="utf-8"))
        nodo = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_dettaglio_costo_api_calcolato_usd")
        namespace = {"Any": object, "dt": __import__("datetime")}
        exec(compile(ast.Module(body=[nodo], type_ignores=[]), "commercial_layer.py", "exec"), namespace)
        costo = namespace["_dettaglio_costo_api_calcolato_usd"](
            "GPT-5.4 (OpenAI)", "gpt-transcribe", {"audio_seconds": 60}
        )
        self.assertEqual(costo["total_usd"], 0.0045)
        self.assertEqual(costo["output_usd"], 0.0)


if __name__ == "__main__":
    unittest.main()
