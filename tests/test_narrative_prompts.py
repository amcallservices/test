import unittest

from editorial_rules import vincolo_parole_con_tolleranza
from emotional_impact import istruzioni_impatto_emotivo
import narrative_prompts as np


class VoceNarranteTests(unittest.TestCase):
    def test_prima_persona_e_presente(self):
        testo = np.direttiva_voce_narrante(np.NARRATORI[1], np.TEMPI_VERBALI[1])
        self.assertIn("prima persona", testo)
        self.assertIn("presente", testo)

    def test_valori_sconosciuti_usano_il_predefinito(self):
        testo = np.direttiva_voce_narrante("boh", "")
        self.assertIn(np.NARRATORE_PREDEFINITO, testo)
        self.assertIn(np.TEMPO_PREDEFINITO, testo)


class ScalettaTests(unittest.TestCase):
    SCALETTA = """[Capitolo 1: Il lago]
- Marco arriva alla casa sul lago
- trova la lettera del padre

**[1.1 La soffitta]**
1. Marco sale in soffitta
2) scopre il diario

[Capitolo 2: Vuoto]
"""

    def test_legge_punti_per_sezione(self):
        self.assertEqual(
            np.scaletta_della_sezione(self.SCALETTA, "Capitolo 1:  Il lago"),
            ["Marco arriva alla casa sul lago", "trova la lettera del padre"],
        )

    def test_intestazioni_decorate_e_numeri(self):
        self.assertEqual(
            np.scaletta_della_sezione(self.SCALETTA, "1.1 La soffitta"),
            ["Marco sale in soffitta", "scopre il diario"],
        )

    def test_voce_senza_punti_e_ignorata(self):
        self.assertEqual(np.scaletta_della_sezione(self.SCALETTA, "Capitolo 2: Vuoto"), [])

    def test_prompt_conserva_la_scaletta_dell_autore(self):
        prompt = np.prompt_genera_scaletta(
            sezioni=["Capitolo 1: Il lago", "Capitolo 2: Vuoto"], indice="Capitolo 1: Il lago\nCapitolo 2: Vuoto",
            titolo="Il lago", genere="Narrativo", trama="Marco torna a casa.", obiettivo="emozionare",
            scheda_personaggi="", voce_narrante="Prima persona", lingua="Italiano",
            scaletta_esistente=self.SCALETTA,
        )
        self.assertIn("[Capitolo 2: Vuoto]", prompt)
        self.assertIn("riportala identica", prompt)


class PromptNarrativoTests(unittest.TestCase):
    def _sistema(self, genere="Thriller / Noir"):
        return np.system_prompt_narrativa(
            lingua="Italiano", titolo="Il lago", genere=genere, tipologia="Storytelling Immersivo",
            stile_racconto="Coinvolgente e Narrativo", ritmo="Serrato e dinamico", descrizione_ritmo="",
            obiettivo="tenere alta la tensione", voce_narrante="Narratore: Prima persona",
            regole_genere="Tensione e indizi.", modulo_lunghezza="=== LUNGHEZZA ===",
        )

    def test_non_contiene_direttive_da_manuale(self):
        testo = self._sistema().lower()
        for vietato in ("checklist", "procedura numerata", "neuromarketing", "dopamina", "30 anni"):
            self.assertNotIn(vietato, testo)

    def test_chiede_di_ripetere_nomi_e_continuita(self):
        testo = self._sistema()
        self.assertIn("DEVONO tornare", testo)
        self.assertIn("Riparti da dove si è chiusa", testo)

    def test_biografia_vieta_invenzioni(self):
        self.assertIn("non inventare eventi", self._sistema("Biografia"))

    def test_blocco_sezione_con_e_senza_scaletta(self):
        con = np.blocco_sezione_narrativa(sezione="Cap 1", scaletta_sezione=["arriva"], scheda_personaggi="Marco: 30 anni")
        self.assertIn("- arriva", con)
        self.assertIn("Marco: 30 anni", con)
        senza = np.blocco_sezione_narrativa(sezione="Cap 1", scaletta_sezione=[], scheda_personaggi="")
        self.assertIn("non c'è una scaletta", senza)


class LunghezzaTests(unittest.TestCase):
    def test_margine_saggistica_10_per_cento(self):
        self.assertEqual(vincolo_parole_con_tolleranza("Standard KDP", "Manuale Tecnico"), (558, 770))

    def test_margine_narrativa_piu_ampio(self):
        self.assertEqual(vincolo_parole_con_tolleranza("Standard KDP", "Romanzo Rosa"), (496, 804))

    def test_senza_genere_resta_compatibile(self):
        self.assertEqual(vincolo_parole_con_tolleranza("Standard KDP"), (558, 770))


class GeneriUnificatiTests(unittest.TestCase):
    def test_contemporaneo_riceve_istruzioni_narrative(self):
        testo = istruzioni_impatto_emotivo(
            sezione="Capitolo 1", genere="Contemporaneo", tipologia="", stile="", obiettivo="",
        )
        self.assertIn("EMOTIONAL IMPACT ENGINE", testo)


if __name__ == "__main__":
    unittest.main()
