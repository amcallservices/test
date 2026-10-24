"""The outline remains available when editorial checks fail but chapters exist."""

import ast
import re
import unittest
from pathlib import Path
from types import SimpleNamespace


SOURCE = Path(__file__).resolve().parents[1] / "app.py"
TREE = ast.parse(SOURCE.read_text(encoding="utf-8"))
GENERATOR = [
    node for node in TREE.body
    if isinstance(node, ast.FunctionDef) and node.name == "genera_indice_controllato"
][-1]


class OutlineWarningTests(unittest.TestCase):
    def build_generator(self, responses, *, problems=None, audit=None):
        state = {}
        refunds = []
        replies = iter(responses)

        def check(indice, *args, **kwargs):
            if callable(problems):
                return problems(indice)
            return list(problems or [])

        namespace = {
            "st": SimpleNamespace(session_state=state),
            "re": re,
            "CREDIT_COSTS": {"indice_generazione_editoriale": 6},
            "TIMEOUT_INDICE_SECONDI": 150,
            "MODELLO_EDITORIALE": "gpt-editorial",
            "addebita_azione_diretta": lambda *args, **kwargs: "reference",
            "refund_credits": lambda *args, **kwargs: refunds.append((args, kwargs)),
            "chiedi_gpt": lambda *args, **kwargs: next(replies),
            "normalizza_indice_generato": lambda value: str(value).strip(),
            "firma_indice": lambda value: str(value).strip().casefold(),
            "criticita_indice_generato": check,
            "conta_sezioni_indice": lambda value: len(re.findall(r"(?im)^capitolo\s+\d+", value)),
            "stima_budget_parole_indice": lambda *args: {"raggiunge_soglia": True},
            "superamenti_budget_editoriale": lambda *args: [],
            "audit_editoriale_indice_generato": audit or (lambda indice, *args, **kwargs: (6, "troppo generico")),
        }
        exec(compile(ast.Module(body=[GENERATOR], type_ignores=[]), str(SOURCE), "exec"), namespace)
        return namespace["genera_indice_controllato"], state, refunds

    def generate(self, generator):
        return generator(
            "Prompt", "System", "Manuale Pratico", "Auto usate", "Controlli", "Aiutare",
            "Italiano", "Standard", "Diretto", "Tu", massimo_sezioni=65,
        )

    def test_low_editorial_score_publishes_best_readable_draft(self):
        first = "Capitolo 1: Controlli\n1.1 Documenti"
        improved = "Capitolo 1: Controlli\n1.1 Documenti e verifiche"
        generator, state, refunds = self.build_generator(
            [first, improved],
            audit=lambda indice, *args, **kwargs: (7 if "verifiche" in indice else 6, "serve revisione"),
        )
        self.assertEqual(self.generate(generator), improved)
        self.assertIn("Indice pubblicato con avviso", state["ultimo_controllo_indice"])
        self.assertIn("verifica manuale", state["ultimo_controllo_indice"])
        self.assertEqual(refunds, [])

    def test_recipe_count_mismatch_still_returns_chapter_outline(self):
        first = "\n".join(f"Capitolo {number}: Ricetta {number}" for number in range(1, 20))
        revised = "\n".join(f"Capitolo {number}: Ricetta {number}" for number in range(1, 18))
        generator, state, refunds = self.build_generator(
            [first, revised],
            problems=lambda indice: [f"sono richieste 15 ricette, ma l'indice contiene {len(indice.splitlines())} capitoli"],
        )
        result = self.generate(generator)
        self.assertEqual(result, revised)
        self.assertIn("sono richieste 15 ricette", state["ultimo_controllo_indice"])
        self.assertEqual(refunds, [])

    def test_failed_revision_keeps_first_readable_draft(self):
        first = "Capitolo 1: Controlli\n1.1 Documenti"
        generator, state, refunds = self.build_generator([first, "ERRORE: timeout"])
        self.assertEqual(self.generate(generator), first)
        self.assertIn("correzione automatica", state["ultimo_controllo_indice"])
        self.assertEqual(refunds, [])

    def test_unrecognizable_response_is_not_published_and_is_refunded(self):
        generator, state, refunds = self.build_generator(["Ecco alcuni consigli", "Ancora nessun indice"])
        self.assertEqual(self.generate(generator), "")
        self.assertIn("non contiene capitoli riconoscibili", state["ultimo_controllo_indice"])
        self.assertEqual(len(refunds), 1)


if __name__ == "__main__":
    unittest.main()
