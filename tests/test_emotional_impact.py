import ast
import unittest
from pathlib import Path

from emotional_impact import istruzioni_impatto_emotivo


class EmotionalImpactTests(unittest.TestCase):
    def prompt(self, **overrides):
        params = {
            "sezione": "Capitolo 3: La scelta di Marta",
            "genere": "Narrativo",
            "tipologia": "Storytelling Immersivo",
            "stile": "Coinvolgente e Narrativo",
            "obiettivo": "Raccontare una scelta difficile senza anticipare il finale.",
            "brief_personale": "Tono sobrio e dialoghi realistici.",
            "contesto_narrativo": "Andrea ha consegnato una lettera a Marta.",
            "ruolo_sezione": "sottocapitolo",
        }
        params.update(overrides)
        return istruzioni_impatto_emotivo(**params)

    def test_romanzo_richiede_emozioni_naturali_senza_eventi_nuovi(self):
        prompt = self.prompt()
        self.assertIn("non creare eventi", prompt)
        self.assertIn("decisioni, azioni, dialoghi", prompt)
        self.assertIn("spazio per l'interpretazione", prompt)

    def test_scena_tranquilla_non_diventa_artificialmente_drammatica(self):
        prompt = self.prompt()
        self.assertIn("non drammatizzare scene ordinarie", prompt)
        self.assertIn("cliffhanger artificiali", prompt)

    def test_dialoghi_rispettano_personalita_e_sottotesto(self):
        prompt = self.prompt()
        self.assertIn("dialoghi naturali", prompt)
        self.assertIn("sottotesto", prompt)
        self.assertIn("personaggi in psicologi", prompt)

    def test_thriller_aumenta_tensione_senza_nuovi_indizi(self):
        prompt = self.prompt(genere="Thriller / Noir")
        self.assertIn("curiosità, rischio e sospetto", prompt)
        self.assertIn("non inventare indizi", prompt)

    def test_manuale_rimane_pratico_e_non_teatrale(self):
        prompt = self.prompt(genere="Manuale Pratico")
        self.assertIn("testo non narrativo", prompt)
        self.assertIn("Non introdurre scene, conflitti, tensione", prompt)
        self.assertIn("ricette, quiz, esercizi, procedure", prompt)

    def test_memoria_e_istruzioni_autore_prevalgono(self):
        prompt = self.prompt()
        self.assertIn("canone", prompt)
        self.assertIn("istruzioni personali dell'autore prevalgono", prompt)

    def test_parte_narrativa_rimane_scena_e_non_spiegazione(self):
        prompt = self.prompt(ruolo_sezione="parte")
        self.assertIn("scena breve e compiuta", prompt)
        self.assertIn("non spiegare al lettore", prompt)

    def test_istruzioni_restano_compatte_e_senza_chiamate(self):
        prompt = self.prompt()
        self.assertLess(len(prompt), 3500)
        self.assertNotIn("http", prompt.casefold())
        self.assertNotIn("credito", prompt.casefold())

    def test_il_motore_e_collegato_una_sola_volta_al_prompt_condiviso(self):
        source = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        writer = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "crea_prompt_stesura_sezione"
        )
        writer_source = ast.get_source_segment(source, writer) or ""
        self.assertEqual(writer_source.count("emotional_impact_core.istruzioni_impatto_emotivo("), 1)
        self.assertEqual(writer_source.count("{istruzioni_impatto_emotivo}"), 2)


if __name__ == "__main__":
    unittest.main()
