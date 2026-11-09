import string
import unittest

import book_project as bp
import book_project_i18n as i18n


ORDINE = [
    "Prefazione", "Parte I: L'arrivo", "Capitolo 1: La casa", "1.1 La lettera", "1.2 La telefonata",
    "Capitolo 2: Giulia", "Parte II: Il caso", "Capitolo 3: Il pozzo",
]


class TipoEStrutturaTests(unittest.TestCase):
    def test_tipo_opera(self):
        self.assertEqual(bp.tipo_opera("Thriller / Noir"), "narrativa")
        self.assertEqual(bp.tipo_opera("Ricettario"), "manuale")
        self.assertEqual(bp.tipo_opera("Business & Marketing"), "saggistica")

    def test_apertura_e_chiusura_dei_capitoli(self):
        self.assertEqual(bp.posizione_nel_capitolo("1.1 La lettera", ORDINE), (True, False))
        self.assertEqual(bp.posizione_nel_capitolo("1.2 La telefonata", ORDINE), (False, True))
        self.assertEqual(bp.posizione_nel_capitolo("Capitolo 1: La casa", ORDINE), (True, False))
        self.assertEqual(bp.posizione_nel_capitolo("Capitolo 3: Il pozzo", ORDINE), (True, True))

    def test_direttive_per_tipo(self):
        romanzo = bp.direttive_struttura("narrativa", True, True)
        self.assertIn("aggancio", romanzo)
        self.assertIn("chiude il capitolo", romanzo)
        manuale = bp.direttive_struttura("manuale", False, True, "[TO VERIFY]")
        self.assertIn("dovresti vedere", manuale)
        self.assertIn("riepilogo puntato", manuale)
        self.assertIn("[TO VERIFY]", manuale)
        self.assertNotIn("aggancio", bp.direttive_struttura("saggistica", False, False))


class SemiTests(unittest.TestCase):
    SEMI = "- La lettera del padre | compare: Capitolo 1 | si risolve: Capitolo 3\n- La chiave | compare: 1.2 La telefonata | si risolve: Capitolo 9\n- Il pozzo"

    def test_semi_per_sezione(self):
        self.assertEqual(bp.semi_della_sezione(self.SEMI, "1.1 La lettera"), (["La lettera del padre"], []))
        self.assertEqual(bp.semi_della_sezione(self.SEMI, "Capitolo 3: Il pozzo"), ([], ["La lettera del padre"]))

    def test_controllo_semi(self):
        esiti = {e["seme"]: e["problema"] for e in bp.controllo_semi(self.SEMI, ORDINE, {"Capitolo 3: Il pozzo": ""})}
        self.assertEqual(esiti["La lettera del padre"], "non_ancora_scritto")
        self.assertEqual(esiti["La chiave"], "voce_inesistente")

    def test_esempio_semi_letto_in_ogni_lingua(self):
        capitoli = {
            "Italiano": ("Capitolo 2: x", "Capitolo 11: y"), "English": ("Chapter 2: x", "Chapter 11: y"),
            "Español": ("Capítulo 2: x", "Capítulo 11: y"), "Français": ("Chapitre 2 : x", "Chapitre 11 : y"),
            "Deutsch": ("Kapitel 2: x", "Kapitel 11: y"), "Română": ("Capitolul 2: x", "Capitolul 11: y"),
            "Русский": ("Глава 2: x", "Глава 11: y"), "العربية": ("الفصل 2: x", "الفصل 11: y"),
            "中文": ("第2章：x", "第11章：y"),
        }
        for lingua in i18n.LINGUE:
            with self.subTest(lingua=lingua):
                prima, ultima = capitoli[lingua]
                semi = bp.leggi_semi(i18n.TESTI[lingua]["modello_semi"])
                self.assertTrue(semi[0]["compare"] and semi[0]["risolve"], semi)
                self.assertTrue(bp.voce_corrisponde(semi[0]["compare"], prima))
                self.assertTrue(bp.voce_corrisponde(semi[0]["risolve"], ultima))

    def test_punti_aperti_della_scheda(self):
        registro = "CHI SA COSA\n- Marco sa della lettera\nMISTERI E PROMESSE ANCORA APERTI\n- chi l'ha scritta\n- nessuno"
        self.assertEqual(bp.punti_aperti_registro(registro), ["chi l'ha scritta"])


class ControlliLocaliTests(unittest.TestCase):
    def test_marcatori_in_tutte_le_lingue(self):
        for lingua, marcatore in bp.MARCATORI_VERIFICA.items():
            with self.subTest(lingua=lingua):
                testo = f"Il dato è 42 {marcatore}. Fine."
                self.assertEqual(len(bp.trova_marcatori_verifica({"S": testo})), 1)
                self.assertNotIn(marcatore, bp.rimuovi_marcatori_verifica(testo))

    def test_ripetizioni_e_frasi_fatte(self):
        testo = "Marco guardava il lago immobile sotto la luna. " * 5 + "Era come se. Come se. Come se."
        ripetute = dict(bp.ripetizioni_nel_libro({"A": testo}))
        self.assertIn("marco guardava il lago", ripetute)
        self.assertIn("come se", dict(bp.frasi_fatte_nel_libro({"A": testo})))
        self.assertEqual(bp.ripetizioni_nel_libro({"A": "大海" * 400}), [])

    def test_caporali_solo_in_italiano(self):
        testo = {"A": '"Ciao," disse. "Vieni?" "No." "Perché?"'}
        self.assertTrue(bp.dialoghi_senza_caporali(testo, "Italiano"))
        self.assertFalse(bp.dialoghi_senza_caporali(testo, "English"))


class PromptTests(unittest.TestCase):
    def test_progetto_chiede_solo_campi_vuoti(self):
        prompt = bp.prompt_genera_progetto(
            tipo="narrativa", sezioni=["Capitolo 1: La casa"], indice="Capitolo 1: La casa", titolo="Il lago",
            genere="Thriller / Noir", trama="t", obiettivo="o", risultato="r", voce_narrante="Prima persona",
            lingua="Italiano", campi_esistenti={"scheda_personaggi": "- Marco: 34 anni"},
        )
        self.assertIn("=== VERITÀ NASCOSTA ===", prompt)
        self.assertIn("=== MAPPA DEI SEMI ===", prompt)
        self.assertNotIn("=== PERSONAGGI E MONDO ===", prompt)
        self.assertIn("- Marco: 34 anni", prompt)

    def test_lettura_blocchi(self):
        blocchi = bp.leggi_blocchi_progetto("=== OBIETTIVI E PREREQUISITI ===\n- saper fare\n=== SCALETTA ===\n[Cap 1]\n- a")
        self.assertEqual(blocchi["obiettivi_prerequisiti"], "- saper fare")
        self.assertEqual(blocchi["scaletta"], "[Cap 1]\n- a")

    def test_blocco_sezione_romanzo_con_semi_e_verita(self):
        blocco = bp.blocco_progetto_sezione(
            tipo="narrativa", sezione="Capitolo 3: Il pozzo",
            campi={"verita_nascosta": "Il padre è vivo.", "mappa_semi": SemiTests.SEMI},
            scaletta_sezione=[], registro="CHI SA COSA\n- Marco", apre=True, chiude=True, marcatore="[DA VERIFICARE]",
        )
        self.assertIn("NON rivelarla prima", blocco)
        self.assertIn("Semi da risolvere qui", blocco)
        self.assertIn("SCHEDA DI COERENZA", blocco)

    def test_istruzioni_chat_coprono_tutti_i_tipi(self):
        testo = bp.istruzioni_chat_progetto()
        for etichetta in ("VERITÀ NASCOSTA:", "MAPPA DEI SEMI:", "TESI CENTRALE:", "OBIETTIVI E PREREQUISITI:"):
            self.assertIn(etichetta, testo)


class TraduzioniProgettoTests(unittest.TestCase):
    def test_ogni_lingua_ha_tutte_le_voci_e_gli_stessi_segnaposto(self):
        base = i18n.TESTI["Italiano"]
        for lingua in i18n.LINGUE:
            with self.subTest(lingua=lingua):
                self.assertEqual(set(i18n.TESTI[lingua]), set(base))
                for chiave, valore in i18n.TESTI[lingua].items():
                    self.assertTrue(valore.strip(), chiave)
                    attesi = {c[1] for c in string.Formatter().parse(base[chiave]) if c[1]}
                    trovati = {c[1] for c in string.Formatter().parse(valore) if c[1]}
                    self.assertEqual(trovati, attesi, f"{lingua}/{chiave}")

    def test_lingua_sconosciuta_usa_italiano(self):
        self.assertEqual(i18n.testo("riquadro", "Klingon"), "🧭 Progetto del libro")


if __name__ == "__main__":
    unittest.main()
