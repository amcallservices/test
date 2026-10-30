"""Regression tests for DeepSeek-only adherence to the book and index."""

import ast
import unittest
from pathlib import Path
from types import SimpleNamespace


TREE = ast.parse((Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8"))


def load_functions(names, namespace):
    for node in TREE.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            exec(compile(ast.Module(body=[node], type_ignores=[]), "app.py", "exec"), namespace)
    return namespace


class DeepSeekFocusTests(unittest.TestCase):
    def test_checker_uses_book_and_index_and_is_conservative(self):
        requests = []
        answer = ["FUORI_TEMA: parla di un altro libro"]
        namespace = {
            "MODELLO_STESURA": "writing-model",
            "chiedi_gpt": lambda prompt, system, **kwargs: requests.append((prompt, kwargs)) or answer[0],
        }
        app = load_functions({"verifica_attinenza_sezione_deepseek"}, namespace)
        check = app["verifica_attinenza_sezione_deepseek"]
        self.assertIs(check("Testo di prova", "1.1 Controlli documentali", "Indice auto", "Auto usate", "Acquisto sicuro", "Italiano"), False)
        self.assertIn("Tema del libro dalla sidebar: Auto usate", requests[0][0])
        self.assertIn("Titolo della sezione: 1.1 Controlli documentali", requests[0][0])
        self.assertFalse(requests[0][1]["addebita"])
        answer[0] = "PERTINENTE"
        self.assertIs(check("Testo", "1.1", "Indice", "Auto", "Acquisto", "Italiano"), True)
        answer[0] = "ERRORE: timeout"
        self.assertIsNone(check("Testo", "1.1", "Indice", "Auto", "Acquisto", "Italiano"))

    def make_writer(self, deepseek, verdicts):
        saved = []
        repairs = []
        audited = []
        prompts = []
        refunds = []
        session_state = {}
        original = "Fuori tema. " * 100
        repaired = "Controllo documenti dell'auto usata. " * 80
        def generate_section(prompt, *args):
            prompts.append(prompt)
            if deepseek:
                references = session_state.get("_riferimenti_stesura_deepseek_corrente")
                if references is not None:
                    references.append("ref-one")
            return original
        namespace = {
            "st": SimpleNamespace(session_state=session_state),
            "AI_REQUEST_CREDITS": 1,
            "refund_credits": lambda reference, **kwargs: refunds.append(reference),
            "usa_deepseek_pro": lambda: deepseek,
            "tipo_sezione_editoriale": lambda _: "sottocapitolo",
            "sezione_simulazione_test_prep": lambda *args: False,
            "crea_prompt_stesura_sezione": lambda *args: "PROMPT ORIGINALE",
            "rafforza_focus_sezione_deepseek": lambda prompt, *args: prompt + " FOCUS DEEPSEEK",
            "PROFILI_LUNGHEZZA_STESURA": {"Standard KDP": {"max_completion_tokens": 2000}},
            "genera_contenuto_editoriale": generate_section,
            "pulisci_testo_editoriale": lambda text: text or "",
            "motivo_chiusura_tecnica": lambda text: "",
            "genera_bozza_sezione_con_chiusura": lambda prompt, system, section, lang, **kwargs: repairs.append(kwargs) or (repaired, True),
            "verifica_attinenza_sezione_deepseek": lambda text, *args: audited.append(text) or verdicts.pop(0),
            "scrivi_sezione_stesura_completa": lambda section, text: saved.append(text) or text,
            "narrative_core": SimpleNamespace(
                genere_narrativo=lambda _genere: False,
                controlla_unita_narrativa=lambda *_args: [],
            ),
            "memoria_core": SimpleNamespace(
                memoria_editoriale_progetto=lambda _state: {"narrativa": {}},
            ),
            "S_PROMPT": "SYSTEM",
        }
        app = load_functions({"scrivi_contenuto_dettagliato"}, namespace)
        args = ("1.1 Controlli documentali", "Indice", "Auto usate", "Manuale Pratico", "Pratico", "Diretto", "Tu", "Acquisto sicuro", "Italiano", "", "Standard KDP")
        return app["scrivi_contenuto_dettagliato"], args, saved, repairs, audited, original, repaired, refunds, session_state, prompts

    def test_off_topic_deepseek_section_is_rewritten_for_free_before_save(self):
        write, args, saved, repairs, audited, original, repaired, _, _, prompts = self.make_writer(True, [False, True])
        self.assertEqual(write(*args), repaired.strip())
        self.assertEqual(saved, [repaired.strip()])
        self.assertEqual(audited, [original.strip(), repaired.strip()])
        self.assertEqual(len(repairs), 1)
        self.assertIs(repairs[0]["addebita"], False)
        self.assertIn("FOCUS DEEPSEEK", prompts[0])

    def test_persistent_off_topic_does_not_replace_existing_section(self):
        write, args, saved, repairs, _, _, _, refunds, state, _ = self.make_writer(True, [False, False, False])
        with self.assertRaisesRegex(RuntimeError, "Non è stata salvata"):
            write(*args)
        self.assertEqual(saved, [])
        self.assertEqual(len(repairs), 2)
        self.assertEqual(refunds, ["ref-one"])
        self.assertNotIn("_riferimenti_stesura_deepseek_corrente", state)

    def test_gpt_writing_path_remains_unchanged(self):
        write, args, saved, repairs, audited, original, _, _, _, prompts = self.make_writer(False, [])
        self.assertEqual(write(*args), original.strip())
        self.assertEqual(saved, [original.strip()])
        self.assertEqual(repairs, [])
        self.assertEqual(audited, [])
        self.assertEqual(prompts, ["PROMPT ORIGINALE"])


if __name__ == "__main__":
    unittest.main()
