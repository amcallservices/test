import unittest

from project_memory import (
    CHIAVE_ARCHIVIO_STESURA_COMPLETA,
    CHIAVE_MEMORIA_PROTETTA,
    CHIAVE_MEMORIA_SEZIONI,
    CHIAVE_PROGETTO_UNICO,
    elenco_sezioni_indice_attivo,
    rimuovi_sezioni_fuori_indice,
)
from project_outline import conta_sezioni_indice, normalizza_indice_generato


class StesuraRispettaIndiceTests(unittest.TestCase):
    def test_indice_elimina_elenchi_esplicativi_numerati(self):
        indice = """Parte I: La partenza
Capitolo 1: Il lago
1.1 La prima sera
1. Verificare il timbro e cercare i registri
2. Controllare i conti rimasti aperti
Capitolo 2: La scelta
2.1 Una conseguenza"""

        pulito = normalizza_indice_generato(indice)

        self.assertNotIn("1. Verificare", pulito)
        self.assertNotIn("2. Controllare", pulito)
        self.assertIn("1.1 La prima sera", pulito)
        self.assertEqual(conta_sezioni_indice(pulito), 5)

    def test_stesura_usa_solo_le_voci_dell_indice_attivo(self):
        indice_attivo = ["Prefazione", "Parte I: Nuovo inizio", "Capitolo 1: Il presente"]
        archivio_precedente = ["Capitolo 42: Vecchia conclusione", "1. Una sezione estranea"]

        sezioni = elenco_sezioni_indice_attivo(
            [*indice_attivo], lambda _sezione: False
        )

        self.assertEqual(sezioni, indice_attivo)
        self.assertFalse(set(archivio_precedente).intersection(sezioni))

    def test_sostituzione_indice_elimina_contenuti_e_coda_obsoleti(self):
        stato = {
            CHIAVE_PROGETTO_UNICO: {
                "contenuti": {"Capitolo 1: Attuale": "Testo nuovo", "Capitolo 42: Vecchio": "Testo vecchio"},
                "immagini": {}, "sidebar": {}, "fonti": {}, "memoria_editoriale": {},
            },
            CHIAVE_MEMORIA_SEZIONI: {"Capitolo 1: Attuale": "Testo nuovo", "Capitolo 42: Vecchio": "Testo vecchio"},
            CHIAVE_MEMORIA_PROTETTA: {"Capitolo 1: Attuale": "Testo nuovo", "Capitolo 42: Vecchio": "Testo vecchio"},
            CHIAVE_ARCHIVIO_STESURA_COMPLETA: {"Capitolo 1: Attuale": "Testo nuovo", "Capitolo 42: Vecchio": "Testo vecchio"},
            "job_scrittura_coda": ["Capitolo 42: Vecchio"],
        }

        rimossi = rimuovi_sezioni_fuori_indice(
            stato,
            ["Capitolo 1: Attuale"],
            lambda sezione: "widget_" + sezione,
            lambda sezione: "precedente_" + sezione,
        )

        self.assertEqual(rimossi, ["Capitolo 42: Vecchio"])
        self.assertEqual(stato[CHIAVE_PROGETTO_UNICO]["contenuti"], {"Capitolo 1: Attuale": "Testo nuovo"})
        self.assertEqual(stato["job_scrittura_coda"], [])


if __name__ == "__main__":
    unittest.main()
