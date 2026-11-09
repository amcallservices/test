"""Simula il deploy parziale di Streamlit: app.py nuovo, modulo vecchio in memoria."""

import ast
import hashlib
import importlib
import sys
import types
import unittest
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]


def carica_funzioni_ricarica():
    sorgente = (RADICE / "app.py").read_text(encoding="utf-8")
    albero = ast.parse(sorgente)
    nomi = {"_firma_file_modulo", "ricarica_moduli_locali_aggiornati", "marca_moduli_locali_caricati"}
    namespace = {"hashlib": hashlib, "importlib": importlib, "sys": sys}
    for nodo in albero.body:
        if isinstance(nodo, ast.Assign) and any(
            getattr(t, "id", "") == "MODULI_LOCALI_AGGIORNABILI" for t in nodo.targets
        ):
            exec(compile(ast.Module(body=[nodo], type_ignores=[]), "app.py", "exec"), namespace)
    for nodo in albero.body:
        if isinstance(nodo, ast.FunctionDef) and nodo.name in nomi:
            exec(compile(ast.Module(body=[nodo], type_ignores=[]), "app.py", "exec"), namespace)
    return namespace


class RicaricaModuliTests(unittest.TestCase):
    def setUp(self):
        self.app = carica_funzioni_ricarica()
        import project_text
        self.originale = project_text

    def tearDown(self):
        sys.modules["project_text"] = importlib.reload(self.originale)

    def test_modulo_vecchio_in_memoria_viene_ricaricato(self):
        import project_text
        # Versione "vecchia": senza le funzioni nuove e senza firma.
        del project_text.rimuovi_preambolo_ai
        if hasattr(project_text, "_firma_file_caricato"):
            del project_text._firma_file_caricato
        ricaricati = self.app["ricarica_moduli_locali_aggiornati"](("project_text",))
        self.assertEqual(ricaricati, ["project_text"])
        self.assertTrue(hasattr(sys.modules["project_text"], "rimuovi_preambolo_ai"))

    def test_modulo_aggiornato_non_viene_ricaricato(self):
        self.app["marca_moduli_locali_caricati"](("project_text",))
        self.assertEqual(self.app["ricarica_moduli_locali_aggiornati"](("project_text",)), [])

    def test_modulo_con_firma_diversa_viene_ricaricato(self):
        import project_text
        project_text._firma_file_caricato = "versione-precedente"
        self.assertEqual(self.app["ricarica_moduli_locali_aggiornati"](("project_text",)), ["project_text"])


if __name__ == "__main__":
    unittest.main()
