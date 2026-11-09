import unittest

from brain_names import NOMI, VALORE_COSTOSO, VALORE_ECONOMICO, nome_cervello
from narrative_i18n import LINGUE


class NomiCervelliTests(unittest.TestCase):
    def test_nomi_in_italiano(self):
        self.assertEqual(nome_cervello(VALORE_COSTOSO), "Cervello costoso")
        self.assertEqual(nome_cervello(VALORE_ECONOMICO), "Cervello economico")

    def test_tutte_le_lingue(self):
        for lingua in LINGUE:
            with self.subTest(lingua=lingua):
                costoso, economico = NOMI[lingua]
                self.assertEqual(nome_cervello(VALORE_COSTOSO, lingua), costoso)
                self.assertEqual(nome_cervello(VALORE_ECONOMICO, lingua), economico)
                self.assertNotEqual(costoso, economico)

    def test_valori_tecnici_vecchi_e_vuoti(self):
        self.assertEqual(nome_cervello("GPT-5.4"), "Cervello costoso")
        self.assertEqual(nome_cervello("deepseek-v4-pro", "English"), "Economy brain")
        self.assertEqual(nome_cervello(""), "")


if __name__ == "__main__":
    unittest.main()
