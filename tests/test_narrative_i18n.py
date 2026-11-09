import unittest

import narrative_i18n as i18n
import narrative_prompts as np


class TraduzioniRomanziTests(unittest.TestCase):
    def test_ogni_lingua_ha_tutte_le_voci(self):
        chiavi = set(i18n.TESTI["Italiano"])
        for lingua in i18n.LINGUE:
            with self.subTest(lingua=lingua):
                self.assertEqual(set(i18n.TESTI[lingua]), chiavi)
                self.assertEqual(len(i18n.TESTI[lingua]["opzioni_narratore"]), len(np.NARRATORI))
                self.assertEqual(len(i18n.TESTI[lingua]["opzioni_tempo"]), len(np.TEMPI_VERBALI))
                for chiave, valore in i18n.TESTI[lingua].items():
                    self.assertTrue(valore, f"{lingua}: {chiave} vuoto")

    def test_conteggio_formattato_in_ogni_lingua(self):
        for lingua in i18n.LINGUE:
            with self.subTest(lingua=lingua):
                testo = i18n.testo("conteggio", lingua, n=3, totale=7)
                self.assertIn("3", testo)
                self.assertIn("7", testo)

    def test_lingua_sconosciuta_usa_italiano(self):
        self.assertEqual(i18n.testo("narratore", "Klingon"), "Chi racconta la storia")

    def test_etichette_mostrate_ma_valore_tecnico_invariato(self):
        self.assertEqual(i18n.etichetta_narratore(np.NARRATORI[1], "English"), "First person (the protagonist tells the story)")
        self.assertEqual(i18n.etichetta_tempo(np.TEMPI_VERBALI[1], "中文"), "现在时")
        self.assertEqual(i18n.etichetta_narratore("", "English"), "")

    def test_la_chat_riconosce_le_opzioni_in_ogni_lingua(self):
        for lingua in i18n.LINGUE:
            for indice, etichetta in enumerate(i18n.TESTI[lingua]["opzioni_narratore"]):
                with self.subTest(lingua=lingua, etichetta=etichetta):
                    self.assertEqual(np.normalizza_narratore(etichetta), np.NARRATORI[indice])
            for indice, etichetta in enumerate(i18n.TESTI[lingua]["opzioni_tempo"]):
                with self.subTest(lingua=lingua, etichetta=etichetta):
                    self.assertEqual(np.normalizza_tempo_verbale(etichetta), np.TEMPI_VERBALI[indice])

    def test_istruzioni_chat_con_nomi_nella_lingua_dell_utente(self):
        italiano = i18n.istruzioni_chat_romanzi("Italiano")
        self.assertNotIn("LINGUA DELL'UTENTE", italiano)
        for lingua in i18n.LINGUE[1:]:
            with self.subTest(lingua=lingua):
                testo = i18n.istruzioni_chat_romanzi(lingua)
                self.assertIn("NARRATORE:", testo)
                self.assertIn(i18n.TESTI[lingua]["opzioni_narratore"][1], testo)
                self.assertIn(f"= {np.NARRATORI[1]}", testo)


if __name__ == "__main__":
    unittest.main()
