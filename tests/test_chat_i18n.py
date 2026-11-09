import ast
import string
import unittest
from pathlib import Path

import chat_i18n

ORDINE = ("English", "Español", "Français", "Deutsch", "Română", "Русский", "العربية", "中文")


class ChatI18nTests(unittest.TestCase):
    def test_ogni_lingua_ha_tutte_le_voci_e_gli_stessi_segnaposto(self):
        base = chat_i18n.TESTI["Italiano"]
        for lingua in chat_i18n.LINGUE:
            with self.subTest(lingua=lingua):
                self.assertEqual(set(chat_i18n.TESTI[lingua]), set(base))
                for chiave, valore in chat_i18n.TESTI[lingua].items():
                    attesi = {c[1] for c in string.Formatter().parse(base[chiave]) if c[1]}
                    trovati = {c[1] for c in string.Formatter().parse(valore) if c[1]}
                    self.assertEqual(trovati, attesi, f"{lingua}/{chiave}")

    def test_ogni_campo_della_scheda_ha_il_nome_in_tutte_le_lingue(self):
        albero = ast.parse((Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8"))
        valori = {}
        for nodo in albero.body:
            if isinstance(nodo, ast.Assign) and any(getattr(t, "id", "") in ("CAMPI_CHAT_GUIDATA_SIDEBAR", "CAMPI_CHAT_GUIDATA_ETICHETTE_TRADOTTE") for t in nodo.targets):
                valori[nodo.targets[0].id] = ast.literal_eval(nodo.value)
        tradotte = valori["CAMPI_CHAT_GUIDATA_ETICHETTE_TRADOTTE"]
        for campo in set(valori["CAMPI_CHAT_GUIDATA_SIDEBAR"].values()):
            with self.subTest(campo=campo):
                self.assertEqual(len(tradotte.get(campo, ())), len(ORDINE))


if __name__ == "__main__":
    unittest.main()
