"""Contesto del manoscritto e vincoli di output per la scheda KDP."""

import json
import unittest

from project_metadata import (
    campiona_testo_manoscritto,
    crea_prompt_metadati_kdp,
    formatta_metadati_kdp,
)


class ProjectMetadataTests(unittest.TestCase):
    def test_sample_reaches_middle_and_end_of_long_manuscript(self):
        testo = "INIZIO " + ("apertura " * 6000) + "CENTRO " + ("sviluppo " * 6000) + "FINALE " + ("conclusione " * 6000)
        campione = campiona_testo_manoscritto(testo, ["Capitolo 1", "Capitolo 2"])
        self.assertIn("INIZIO", campione)
        self.assertIn("PARTE CENTRA DEL MANOSCRITTO", campione)
        self.assertIn("sviluppo", campione)
        self.assertIn("FINALE DEL MANOSCRITTO", campione)
        self.assertIn("conclusione", campione)
        self.assertIn("Capitolo 2", campione)
        self.assertLess(len(campione), 19000)

    def test_prompt_targets_search_intent_without_keyword_stuffing(self):
        prompt = crea_prompt_metadati_kdp("testo del libro " * 100, "Italiano")
        self.assertIn("SEO e AEO", prompt)
        self.assertIn("2–3 parole", prompt)
        self.assertIn("massimo 3.500 caratteri", prompt)
        self.assertIn("non hai dati di ricerca", prompt)

    def test_output_has_exactly_seven_short_distinct_fields(self):
        dati = {
            "descrizione": "Una guida pratica per chi vuole capire un argomento complesso. " * 6,
            "parole_chiave": [
                "scelta consapevole", "errori comuni", "guida pratica", "controlli preliminari",
                "documenti essenziali", "costi nascosti", "decisione informata",
            ],
        }
        output = formatta_metadati_kdp(json.dumps(dati), "Italiano")
        self.assertIn("DESCRIZIONE KDP", output)
        self.assertIn("7. decisione informata", output)
        dati["parole_chiave"][0] = "frase molto lunga e generica"
        with self.assertRaises(ValueError):
            formatta_metadati_kdp(json.dumps(dati), "Italiano")

    def test_rejects_insufficient_text_and_missing_keyword(self):
        with self.assertRaises(ValueError):
            campiona_testo_manoscritto("troppo breve")
        with self.assertRaises(ValueError):
            formatta_metadati_kdp(json.dumps({"descrizione": "x" * 500, "parole_chiave": ["tema preciso"] * 6}), "Italiano")


if __name__ == "__main__":
    unittest.main()
