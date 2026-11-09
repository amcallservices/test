import unittest

from project_text import estratto_finale, rimuovi_preambolo_ai


class RimuoviPreamboloTests(unittest.TestCase):
    def test_conserva_righe_narrative_che_iniziano_con_formule(self):
        testo = (
            "Ok, pensò Marco, ora basta.\n"
            "Ecco perché nessuno era tornato.\n"
            "Sicuramente lei mentiva.\n"
            "Il treno partì."
        )
        self.assertEqual(rimuovi_preambolo_ai(testo), testo)

    def test_rimuove_preambolo_con_due_punti(self):
        testo = "Ecco il capitolo richiesto:\n\nIl treno partì all'alba."
        self.assertEqual(rimuovi_preambolo_ai(testo), "Il treno partì all'alba.")

    def test_rimuove_conferma_breve(self):
        self.assertEqual(rimuovi_preambolo_ai("Certamente!\nIl treno partì."), "Il treno partì.")

    def test_rimuove_preambolo_che_parla_della_sezione(self):
        testo = "Ecco la sezione richiesta.\nIl treno partì."
        self.assertEqual(rimuovi_preambolo_ai(testo), "Il treno partì.")

    def test_controlla_solo_la_prima_riga(self):
        testo = "Il treno partì.\nEcco il capitolo:\nFine."
        self.assertEqual(rimuovi_preambolo_ai(testo), testo)

    def test_testo_vuoto(self):
        self.assertEqual(rimuovi_preambolo_ai(""), "")
        self.assertEqual(rimuovi_preambolo_ai(None), "")


class EstrattoFinaleTests(unittest.TestCase):
    def test_testo_breve_resta_intero(self):
        self.assertEqual(estratto_finale("Breve scena.", 900), "Breve scena.")

    def test_restituisce_la_fine_non_l_inizio(self):
        inizio = "Marco si svegliò presto nella casa sul lago. " * 30
        finale = "Alla fine Giulia chiuse la porta e partì da sola nella notte."
        estratto = estratto_finale(inizio + finale, 300)
        self.assertTrue(estratto.endswith(finale))
        self.assertLessEqual(len(estratto), 301)

    def test_inizia_da_una_frase_intera(self):
        testo = ("Una frase qualsiasi del capitolo. " * 40) + "Ultima frase."
        estratto = estratto_finale(testo, 200)
        self.assertTrue(estratto.startswith("…Una frase"))


if __name__ == "__main__":
    unittest.main()
