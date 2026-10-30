import unittest

from narrative_engine import (
    costruisci_memoria_narrativa,
    contesto_narrativo,
    controlla_unita_narrativa,
    genere_narrativo,
    piano_scena,
)
from project_memory import CHIAVE_PROGETTO_UNICO, aggiorna_memoria_editoriale


INDICE = """Parte I: Il ritorno
Capitolo 1: La stazione
1.1 Andrea rivede Marta
Capitolo 2: La scelta"""


class NarrativeEngineTests(unittest.TestCase):
    def setUp(self):
        self.contenuti = {
            "Parte I: Il ritorno": "Andrea arriva a Roma. La pioggia gli ricorda una promessa mai mantenuta.",
            "Capitolo 1: La stazione": "Marta aspetta Andrea nella stazione di Roma. Andrea tace, ma consegna a Marta la lettera di Pietro.",
        }

    def test_attiva_la_memoria_solo_per_i_generi_narrativi(self):
        self.assertTrue(genere_narrativo("Narrativo"))
        self.assertTrue(genere_narrativo("Romanzo Rosa"))
        self.assertFalse(genere_narrativo("Manuale Pratico"))
        memoria = costruisci_memoria_narrativa(INDICE, self.contenuti, "Manuale Pratico")
        self.assertFalse(memoria["attiva"])

    def test_registra_scene_e_presenze_confermate(self):
        memoria = costruisci_memoria_narrativa(INDICE, self.contenuti, "Narrativo")
        self.assertTrue(memoria["attiva"])
        self.assertIn("Capitolo 1: La stazione", memoria["scene"])
        self.assertIn("Andrea", memoria["personaggi"])
        self.assertGreaterEqual(memoria["personaggi"]["Andrea"]["presenze"], 2)
        self.assertEqual(memoria["scene"]["Capitolo 1: La stazione"]["stato"], "confermata")

    def test_contesto_non_tratta_il_futuro_come_un_fatto(self):
        memoria = costruisci_memoria_narrativa(INDICE, self.contenuti, "Narrativo")
        contesto = contesto_narrativo("1.1 Andrea rivede Marta", INDICE.splitlines(), memoria)
        self.assertIn("Eventi già confermati", contesto)
        self.assertIn("Prepara senza svolgerla", contesto)
        self.assertIn("Capitolo 2: La scelta", contesto)

    def test_piano_scena_collega_la_scena_precedente_senza_inventare_fatti(self):
        memoria = costruisci_memoria_narrativa(INDICE, self.contenuti, "Narrativo")
        piano = piano_scena("1.1 Andrea rivede Marta", INDICE.splitlines(), memoria)
        self.assertIn("lettera", piano["situazione_iniziale"])
        self.assertIn("cambiamento", piano)
        self.assertIn("azioni", piano)

    def test_avvisa_solo_su_ripresa_molto_simile(self):
        memoria = costruisci_memoria_narrativa(INDICE, self.contenuti, "Narrativo")
        testo = memoria["scene"]["Capitolo 1: La stazione"]["chiusura"]
        avvisi = controlla_unita_narrativa("1.1 Andrea rivede Marta", testo, memoria)
        self.assertTrue(any("possibile ripresa" in avviso for avviso in avvisi))

    def test_memoria_ricalcolata_rispetta_la_modifica_manualizzata(self):
        modificati = dict(self.contenuti)
        modificati["Capitolo 1: La stazione"] = "Marta parte da Milano e consegna ad Andrea una chiave. Andrea lascia Roma."
        memoria = costruisci_memoria_narrativa(INDICE, modificati, "Narrativo")
        self.assertIn("Milano", memoria["scene"]["Capitolo 1: La stazione"]["luoghi_citati"])
        self.assertIn("chiave", memoria["scene"]["Capitolo 1: La stazione"]["chiusura"])

    def test_memoria_del_progetto_si_riallinea_dopo_una_modifica_manuale(self):
        stato = {
            CHIAVE_PROGETTO_UNICO: {
                "indice": INDICE,
                "contenuti": dict(self.contenuti),
                "sidebar": {"genere": "Narrativo"},
                "fonti": {}, "immagini": {}, "memoria_editoriale": {},
            }
        }
        prima = aggiorna_memoria_editoriale(stato)
        stato[CHIAVE_PROGETTO_UNICO]["contenuti"]["Capitolo 1: La stazione"] = (
            "Marta trova Andrea a Milano e gli porge una chiave antica."
        )
        dopo = aggiorna_memoria_editoriale(stato, "Capitolo 1: La stazione", modificata_manualmente=True)
        self.assertTrue(prima["narrativa"]["attiva"])
        self.assertIn("Milano", dopo["narrativa"]["scene"]["Capitolo 1: La stazione"]["luoghi_citati"])
        self.assertTrue(dopo["sezioni"]["Capitolo 1: La stazione"]["modificata_manualmente"])


if __name__ == "__main__":
    unittest.main()
