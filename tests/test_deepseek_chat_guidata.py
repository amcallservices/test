"""Regression tests for sidebar parsing and the GPT-only chat paths."""

import ast
import re
import time
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace

import book_project
import narrative_i18n
import narrative_prompts
from project_text import rimuovi_preambolo_ai


TREE = ast.parse((Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8"))
COMMERCIAL_TREE = ast.parse((Path(__file__).resolve().parents[1] / "commercial_layer.py").read_text(encoding="utf-8"))


def load_functions(names, namespace):
    for node in TREE.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            exec(compile(ast.Module(body=[node], type_ignores=[]), "app.py", "exec"), namespace)
    return namespace


def parser_namespace():
    names = {
        "CAMPI_CHAT_GUIDATA_SIDEBAR", "CAMPI_CHAT_GUIDATA_ETICHETTE_TRADOTTE",
        "CAMPI_CHAT_GUIDATA_OBBLIGATORI", "OPZIONI_CHAT_GUIDATA",
    }
    namespace = {
        "re": re,
        "narrative_prompts_core": narrative_prompts,
        "narrative_i18n_core": narrative_i18n,
        "book_project_core": book_project,
        "TRADUZIONI": {name: {} for name in ("Italiano", "English", "Español", "Français", "Deutsch")},
    }
    for node in TREE.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in names for target in node.targets
        ):
            exec(compile(ast.Module(body=[node], type_ignores=[]), "app.py", "exec"), namespace)
    return load_functions({
        "_valore_scelta_chat_guidata", "estrai_scheda_chat_guidata",
        "estrai_scheda_chat_guidata_da_cronologia", "scheda_chat_guidata_per_sidebar",
        "scelta_personalizzazione_chat_deepseek", "campi_personalizzazione_deepseek",
        "prompt_scheda_chat_guidata_deepseek", "scheda_finale_deepseek_valida",
        "campi_obbligatori_chat_guidata",
    }, namespace)


CARD = """1. TITOLO DEL LIBRO: Comprare un'auto usata senza fregature
2. NOME AUTORE: [Inserisci il tuo nome]
3. LINGUA: Italiano
4. GENERE LETTERARIO: Manuale Pratico
5. TIPOLOGIA SCRITTURA: Standard
6. STILE DI RACCONTO: Diretto e Pratico (Action-oriented)
7. RITMO DEL LIBRO: Equilibrato e progressivo
8. PUNTO DI VISTA: Tu (Diretto, confidenziale e personale)
9. LUNGHEZZA DELLE SEZIONI: Standard KDP
10. CERVELLO AI: DeepSeek V4 Pro
11. OBIETTIVO DEL LIBRO: Aiutare il lettore a valutare un'auto usata.
12. RISULTATO FINALE DESIDERATO: Una scelta d'acquisto più consapevole.
13. TRAMA O ARGOMENTO: Controlli documentali e meccanici per principianti.
"""
PERSONALIZATION = """VOCE O PROSPETTIVA PERSONALE: Tono pratico e rassicurante, senza attribuire esperienze all'autore.
PRIORITÀ PERSONALI PER IL LETTORE: Controlli verificabili prima dell'acquisto.
CONFINI PERSONALI DA RISPETTARE: Nessuna garanzia di assenza di rischi; verificare dati e norme aggiornate.
"""


class DeepSeekCardTests(unittest.TestCase):
    def setUp(self):
        self.app = parser_namespace()

    def test_final_prompt_is_concise_and_preserves_selected_engine(self):
        prompt = self.app["prompt_scheda_chat_guidata_deepseek"]("Italiano", "DeepSeek V4 Pro")
        self.assertIn("CERVELLO AI deve essere esattamente: DeepSeek V4 Pro", prompt)
        self.assertIn("GENERE LETTERARIO:", prompt)
        self.assertIn("Manuale Pratico", prompt)
        self.assertIn("NON porre domande", prompt)
        self.assertIn("VOCE O PROSPETTIVA PERSONALE:", prompt)
        self.assertIn("PRIORITÀ PERSONALI PER IL LETTORE:", prompt)
        self.assertIn("CONFINI PERSONALI DA RISPETTARE:", prompt)
        self.assertIn("RITMO DEL LIBRO:", prompt)

    def test_no_personalization_does_not_require_optional_fields(self):
        prompt = self.app["prompt_scheda_chat_guidata_deepseek"]("Italiano", "DeepSeek V4 Pro", "A")
        self.assertIn("non aggiungere campi di personalizzazione", prompt)
        self.assertTrue(self.app["scheda_finale_deepseek_valida"](self._without_numbers(CARD), "A"))

    def _without_numbers(self, card):
        return re.sub(r"(?m)^(\s*)\d{1,2}[.)]\s+(?=[^\n:]{2,90}:)", r"\1", card)

    def test_complete_card_is_transferable(self):
        card = self._without_numbers(CARD) + PERSONALIZATION
        self.assertTrue(self.app["scheda_finale_deepseek_valida"](card, "D"))
        parsed = self.app["estrai_scheda_chat_guidata"](card)
        self.assertIn("voce_personale", parsed)
        self.assertIn("priorita_personali", parsed)
        self.assertIn("confini_personali", parsed)
        self.assertEqual(parsed["ritmo_libro"], "Equilibrato e progressivo")

    def test_existing_card_without_rhythm_remains_transferable(self):
        card_without_rhythm = re.sub(
            r"(?m)^7\. RITMO DEL LIBRO:.*\n", "", CARD
        )
        conversation = [{"role": "assistant", "content": self._without_numbers(card_without_rhythm)}]
        parsed = self.app["scheda_chat_guidata_per_sidebar"](
            conversation, "Italiano", "GPT-5.4 (OpenAI)"
        )
        self.assertTrue(
            self.app["CAMPI_CHAT_GUIDATA_OBBLIGATORI"].issubset(parsed)
        )
        self.assertEqual(parsed["ritmo_libro"], "Equilibrato e progressivo")

    def test_personalization_choice_controls_required_fields(self):
        card = self._without_numbers(CARD)
        self.assertFalse(self.app["scheda_finale_deepseek_valida"](card, "B"))
        self.assertFalse(self.app["scheda_finale_deepseek_valida"](card, "C"))
        self.assertFalse(self.app["scheda_finale_deepseek_valida"](card, "D"))
        self.assertTrue(self.app["scheda_finale_deepseek_valida"](card + PERSONALIZATION, "B"))
        self.assertTrue(self.app["scheda_finale_deepseek_valida"](card + PERSONALIZATION, "C"))

    def test_choice_b_and_followup_are_remembered(self):
        conversation = [
            {"role": "user", "content": "Voglio scrivere un libro sulle auto usate"},
            {"role": "assistant", "content": "Vuoi personalizzare il libro? A/B/C/D"},
            {"role": "user", "content": "B"},
            {"role": "assistant", "content": "Quali dettagli personali vuoi aggiungere?"},
            {"role": "user", "content": "Usa un tono pratico; ho una lista di controlli"},
        ]
        self.assertEqual(self.app["scelta_personalizzazione_chat_deepseek"](conversation), ("B", True))

    def test_english_book_idea_is_not_mistaken_for_choice_a(self):
        conversation = [
            {"role": "assistant", "content": "What book would you like to create?"},
            {"role": "user", "content": "A book about buying used cars safely"},
        ]
        self.assertEqual(self.app["scelta_personalizzazione_chat_deepseek"](conversation), ("", False))

    def test_missing_required_field_is_rejected(self):
        card = CARD.replace("11. OBIETTIVO DEL LIBRO: Aiutare il lettore a valutare un'auto usata.\n", "")
        card = self._without_numbers(card) + PERSONALIZATION
        self.assertFalse(self.app["scheda_finale_deepseek_valida"](card, "D"))


class EditorialOpinionSamplingTests(unittest.TestCase):
    def test_long_manuscript_uses_a_distributed_compact_sample(self):
        app = load_functions(
            {"campione_manoscritto_per_parere_editoriale"},
            {"pulisci_testo_editoriale": lambda testo: str(testo or "")},
        )
        manuscript = {
            "Capitolo 1": "A" * 800,
            "Capitolo 2": "B" * 800,
            "Capitolo 3": "C" * 800,
        }
        sample, complete = app["campione_manoscritto_per_parere_editoriale"](
            manuscript, limite_caratteri=900
        )
        self.assertFalse(complete)
        self.assertLessEqual(len(sample), 1100)
        for title in manuscript:
            self.assertIn(title, sample)


class DeepSeekBillingTests(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.refunds = []
        self.logged = []
        self.deepseek = True
        self.answer = SimpleNamespace(
            choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content=CARD))]
        )
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=self.create_response)))
        client.with_options = lambda **kwargs: client
        self.state = {}
        namespace = {
            "st": SimpleNamespace(session_state=self.state),
            "AI_REQUEST_CREDITS": 1,
            "MODELLO_STESURA": "gpt-mini",
            "MODELLO_EDITORIALE": "gpt-editorial",
            "MODELLO_ANALISI_FONTI": "gpt-sources",
            "MODELLO_CONTROLLO_COPYRIGHT_APPROFONDITO": "gpt-copyright",
            "MODELLO_DEEPSEEK_PRO": "deepseek-v4-pro",
            "CHAT_SOLO_GPT_OPERAZIONI": frozenset({
                "chat_sidebar_guidata", "chat_nicchia_dialogo",
                "chat_nicchia_report_iniziale", "chat_nicchia_ricerca_approfondita",
                "chat_nicchia_prompt_finale",
            }),
            "TIMEOUT_INDICE_SECONDI": 150,
            "CommercialCreditError": type("CommercialCreditError", (Exception,), {}),
            "uuid": uuid,
            "time": time,
            "re": re,
            "rimuovi_preambolo_ai": rimuovi_preambolo_ai,
            "usa_deepseek_pro": lambda: self.deepseek,
            "charge_credits": lambda *args, **kwargs: "charged-reference",
            "refund_credits": lambda *args, **kwargs: self.refunds.append((args, kwargs)),
            "registra_esito_chiamata_ai": lambda *args, **kwargs: self.logged.append((args, kwargs)),
            "_client_e_modello_testuale": lambda model, *, forza_gpt=False: (
                client, "deepseek-v4-pro" if self.deepseek and not forza_gpt else model
            ),
        }
        self.app = load_functions({"chiedi_gpt"}, namespace)

    def create_response(self, **request):
        self.requests.append(request)
        return self.answer

    def call_chat(self, validator=None):
        return self.app["chiedi_gpt"](
            "Brief", "Prepara la scheda", model="gpt-editorial",
            reason="chat_sidebar_guidata", timeout_seconds=90,
            max_completion_tokens=3000, validatore_deepseek=validator,
        )

    def test_guided_chat_uses_gpt_even_with_deepseek_selected(self):
        valid = lambda text: parser_namespace()["scheda_finale_deepseek_valida"](text, "A")
        result = self.call_chat(valid)
        self.assertTrue(result.startswith("1. TITOLO DEL LIBRO:"))
        self.assertEqual(self.requests[0]["model"], "gpt-editorial")
        self.assertNotIn("extra_body", self.requests[0])
        self.assertEqual(self.requests[0]["max_completion_tokens"], 3000)
        self.assertEqual(self.refunds, [])

    def test_short_dialogue_reply_remains_allowed(self):
        self.answer.choices[0].message.content = "Vuoi personalizzare il libro? A, B, C o D?"
        self.assertIn("personalizzare", self.call_chat())
        self.assertEqual(self.refunds, [])

    def test_gpt_chat_keeps_the_existing_card_parser(self):
        self.answer.choices[0].message.content = "TITOLO DEL LIBRO: Auto usate"
        valid = lambda text: parser_namespace()["scheda_finale_deepseek_valida"](text, "A")
        self.assertEqual(self.call_chat(valid), "TITOLO DEL LIBRO: Auto usate")
        self.assertEqual(self.refunds, [])

    def test_truncated_reply_is_refunded(self):
        self.answer.choices[0].finish_reason = "length"
        self.assertTrue(self.call_chat().startswith("ERRORE:"))
        self.assertEqual(len(self.refunds), 1)

    def test_gpt_request_and_response_are_unchanged(self):
        self.deepseek = False
        self.answer.choices[0].message.content = "Risposta GPT"
        self.assertEqual(self.call_chat(lambda _: False), "Risposta GPT")
        self.assertNotIn("extra_body", self.requests[0])
        self.assertEqual(self.requests[0]["max_completion_tokens"], 3000)
        self.assertEqual(self.refunds, [])

    def test_niche_final_uses_gpt_output_budget(self):
        detailed = "PROMPT FINALE PER CHAT GUIDATA SCRITTORE SITE\n" + (
            "1. Mercato italiano e libro sulle auto usate: controlli verificabili.\n" * 35
        )
        self.answer.choices[0].message.content = detailed
        result = self.app["chiedi_gpt"](
            "Report della nicchia", "Crea prompt", model="gpt-editorial",
            reason="chat_nicchia_prompt_finale", max_completion_tokens=4200,
        )
        self.assertEqual(result, detailed.strip())
        self.assertEqual(self.requests[0]["model"], "gpt-editorial")
        self.assertNotIn("extra_body", self.requests[0])
        self.assertEqual(self.requests[0]["max_completion_tokens"], 4200)
        self.assertEqual(self.refunds, [])

    def test_short_niche_final_is_available_for_free_expansion(self):
        self.answer.choices[0].message.content = "PROMPT FINALE PER CHAT GUIDATA SCRITTORE SITE\nIdea: auto usate."
        self.assertIn("Idea: auto usate.", self.app["chiedi_gpt"](
            "Report", "Crea prompt", model="gpt-editorial",
            reason="chat_nicchia_prompt_finale", max_completion_tokens=4200,
        ))
        self.assertEqual(self.refunds, [])

    def test_truncated_niche_final_is_refunded(self):
        self.answer.choices[0].message.content = "PROMPT FINALE PER CHAT GUIDATA SCRITTORE SITE\n" + "Dettaglio. " * 250
        self.answer.choices[0].finish_reason = "length"
        self.assertTrue(self.app["chiedi_gpt"](
            "Report", "Crea prompt", model="gpt-editorial",
            reason="chat_nicchia_prompt_finale", max_completion_tokens=4200,
        ).startswith("ERRORE:"))
        self.assertEqual(len(self.refunds), 1)

    def test_deepseek_writing_reference_is_available_for_unsaved_section_refund(self):
        references = []
        self.state["_riferimenti_stesura_deepseek_corrente"] = references
        self.app["chiedi_gpt"]("Scrivi", "System", reason="generazione_testo")
        self.assertEqual(references, ["charged-reference"])


class DeepSeekNichePromptTests(unittest.TestCase):
    def test_gpt_gets_detailed_eight_part_brief_for_both_sidebar_choices(self):
        requests = []
        deepseek = [True]
        detailed = "PROMPT FINALE PER CHAT GUIDATA SCRITTORE SITE\n" + "Analisi pertinente. " * 120
        namespace = {
            "re": re,
            "usa_deepseek_pro": lambda: deepseek[0],
            "_cronologia_chat_nicchia": lambda conversation: "Report confermato",
            "CREDIT_COSTS": {"chat_nicchia_prompt_finale": 1},
            "MODELLO_EDITORIALE": "gpt-editorial",
            "chiedi_gpt": lambda prompt, system, **kwargs: requests.append((system, kwargs)) or detailed,
        }
        app = load_functions({"_prompt_finale_chat_nicchia"}, namespace)
        app["_prompt_finale_chat_nicchia"]([], "Italiano")
        deepseek_system, deepseek_options = requests[-1]
        self.assertIn("otto parti numerate", deepseek_system)
        self.assertIn("recensioni positive e negative", deepseek_system)
        self.assertIn("chiedi SEMPRE se vuole personalizzare", deepseek_system)
        self.assertEqual(deepseek_options["max_completion_tokens"], 4200)
        deepseek[0] = False
        app["_prompt_finale_chat_nicchia"]([], "Italiano")
        gpt_system, gpt_options = requests[-1]
        self.assertIn("otto parti numerate", gpt_system)
        self.assertEqual(gpt_options["max_completion_tokens"], 4200)

    def test_short_deepseek_prompt_is_expanded_without_second_charge(self):
        calls = []
        answers = ["# PROMPT FINALE PER CHAT GUIDATA SCRITTORE SITE\nIdea: auto usate.",
                   "# PROMPT FINALE PER CHAT GUIDATA SCRITTORE SITE\n" + "Dettagli verificati. " * 120]
        namespace = {
            "re": re,
            "usa_deepseek_pro": lambda: True,
            "_cronologia_chat_nicchia": lambda conversation: "Report confermato sulle auto usate",
            "CREDIT_COSTS": {"chat_nicchia_prompt_finale": 1},
            "MODELLO_EDITORIALE": "gpt-editorial",
            "chiedi_gpt": lambda prompt, system, **kwargs: calls.append(kwargs) or answers.pop(0),
        }
        app = load_functions({"_prompt_finale_chat_nicchia"}, namespace)
        result = app["_prompt_finale_chat_nicchia"]([], "Italiano")
        self.assertTrue(result.startswith("PROMPT FINALE PER CHAT GUIDATA SCRITTORE SITE"))
        self.assertIn("Dettagli verificati", result)
        self.assertEqual([call["addebita"] for call in calls], [True, False])


class GptOnlyChatIntegrationTests(unittest.TestCase):
    def test_niche_research_uses_openai_web_search_with_deepseek_selected(self):
        requests = []
        refunds = []
        response = SimpleNamespace(output_text="Report documentato", usage=None)
        openai = SimpleNamespace(responses=SimpleNamespace(create=lambda **kwargs: requests.append(kwargs) or response))
        openai.with_options = lambda **kwargs: openai
        namespace = {
            "CREDIT_COSTS": {"chat_nicchia_report_iniziale": 5},
            "TIMEOUT_RICERCA_WEB_SECONDI": 90,
            "MODELLO_ANALISI_FONTI": "gpt-sources",
            "client_openai": openai,
            "client_deepseek": None,
            "addebita_azione_diretta": lambda *args, **kwargs: "ref",
            "refund_credits": lambda *args, **kwargs: refunds.append(args),
            "registra_esito_chiamata_ai": lambda *args, **kwargs: None,
            "usa_deepseek_pro": lambda: True,
        }
        app = load_functions({"_ricerca_web_chat_nicchia"}, namespace)
        self.assertEqual(app["_ricerca_web_chat_nicchia"]("Auto usate", "Italiano", "chat_nicchia_report_iniziale"), "Report documentato")
        self.assertEqual(requests[0]["model"], "gpt-sources")
        self.assertEqual(requests[0]["tools"], [{"type": "web_search_preview"}])
        self.assertEqual(refunds, [])

    def test_gpt_chat_charge_ignores_deepseek_selection(self):
        state = {"commercial_user_context": {"id": "reader"}, "commercial_demo_credits": 30}
        ledger = []
        chat_costs = {
            "chat_sidebar_guidata": 1,
            "chat_nicchia_dialogo": 1,
            "chat_nicchia_report_iniziale": 5,
            "chat_nicchia_ricerca_approfondita": 8,
            "chat_nicchia_prompt_finale": 1,
        }
        namespace = {
            "st": SimpleNamespace(session_state=state),
            "AI_REQUEST_CREDITS": 1,
            "CHAT_SOLO_GPT_OPERAZIONI": frozenset(chat_costs),
            "DEEPSEEK_UNITI_PER_CREDITO": 3,
            "CommercialCreditError": type("CommercialCreditError", (Exception,), {}),
            "uuid": uuid,
            "_is_admin": lambda user: False,
            "usa_deepseek": lambda: True,
            "_mode": lambda: "demo",
            "_supabase_ready": lambda: False,
            "_balance": lambda user_id: state["commercial_demo_credits"],
            "_demo_ledger": lambda *args: ledger.append(args),
            "_salva_contesto_addebito": lambda *args, **kwargs: None,
            "_registra_ancora_economica": lambda *args: None,
            "_unita_deepseek": lambda *args: 1,
        }
        for node in COMMERCIAL_TREE.body:
            if isinstance(node, ast.FunctionDef) and node.name == "charge_credits":
                exec(compile(ast.Module(body=[node], type_ignores=[]), "commercial_layer.py", "exec"), namespace)
        for reason, cost in chat_costs.items():
            namespace["charge_credits"](reason, amount=cost)
        self.assertEqual(state["commercial_demo_credits"], 14)
        self.assertNotIn("commercial_deepseek_charges", state)
        self.assertEqual(ledger[0][1], -1)
        namespace["charge_credits"]("scrittura_sezione", amount=1)
        self.assertEqual(state["commercial_demo_credits"], 14)
        self.assertEqual(state["commercial_demo_deepseek_units"], 1)

    def test_niche_estimate_uses_gpt_tariff_when_deepseek_is_selected(self):
        app = load_functions({"stima_crediti_per_cervello"}, {
            "CHAT_SOLO_GPT_OPERAZIONI": frozenset({"chat_nicchia_report_iniziale"}),
            "usa_deepseek_pro": lambda: True,
            "re": re,
        })
        self.assertEqual(app["stima_crediti_per_cervello"]("chat_nicchia_report_iniziale", 5), 5)

    def test_failed_first_request_gets_one_free_retry(self):
        calls = []
        answers = ["ERRORE: risposta interrotta", "# PROMPT FINALE PER CHAT GUIDATA SCRITTORE SITE\n" + "Contenuto. " * 220]
        namespace = {
            "re": re,
            "usa_deepseek_pro": lambda: True,
            "_cronologia_chat_nicchia": lambda conversation: "Report confermato",
            "CREDIT_COSTS": {"chat_nicchia_prompt_finale": 1},
            "MODELLO_EDITORIALE": "gpt-editorial",
            "chiedi_gpt": lambda prompt, system, **kwargs: calls.append(kwargs) or answers.pop(0),
        }
        app = load_functions({"_prompt_finale_chat_nicchia"}, namespace)
        result = app["_prompt_finale_chat_nicchia"]([], "Italiano")
        self.assertTrue(result.startswith("PROMPT FINALE PER CHAT GUIDATA SCRITTORE SITE"))
        self.assertEqual([call["addebita"] for call in calls], [True, False])


if __name__ == "__main__":
    unittest.main()


CARD_ROMANZO = """TITOLO DEL LIBRO: Il lago
NOME AUTORE: [Inserisci il tuo nome]
LINGUA: Italiano
GENERE LETTERARIO: Thriller / Noir
TIPOLOGIA SCRITTURA: Storytelling Immersivo
STILE DI RACCONTO: Coinvolgente e Narrativo
RITMO DEL LIBRO: Serrato e dinamico
NARRATORE: **Prima persona**
TEMPO VERBALE: presente
LUNGHEZZA DELLE SEZIONI: Standard KDP
CERVELLO AI: GPT-5.4 (OpenAI)
OBIETTIVO DEL LIBRO: Tenere il lettore in tensione fino all'ultima pagina.
RISULTATO FINALE DESIDERATO: Un thriller completo e coerente.
TRAMA O ARGOMENTO: Marco torna nella casa del padre sul lago e trova una lettera.
APPROFONDIMENTI (FACOLTATIVO): Indizi distribuiti con equilibrio.
PERSONAGGI E MONDO (FACOLTATIVO):
- Marco: ingegnere, ostinato, vuole la verità sul padre
- Giulia: sorella di Marco, protettiva
"""


class ChatGuidataRomanziTests(unittest.TestCase):
    def setUp(self):
        self.app = parser_namespace()

    def test_scheda_romanzo_compila_voce_e_personaggi(self):
        scheda = self.app["estrai_scheda_chat_guidata"](CARD_ROMANZO)
        self.assertEqual(scheda["narratore"], narrative_prompts.NARRATORI[1])
        self.assertEqual(scheda["tempo_verbale"], narrative_prompts.TEMPI_VERBALI[1])
        self.assertEqual(scheda["scheda_personaggi"].splitlines(), [
            "- Marco: ingegnere, ostinato, vuole la verità sul padre",
            "- Giulia: sorella di Marco, protettiva",
        ])
        self.assertNotIn("PERSONAGGI", scheda["approfondimenti"])

    def test_romanzo_non_richiede_il_pronome_rivolto_al_lettore(self):
        self.assertTrue(self.app["scheda_finale_deepseek_valida"](CARD_ROMANZO, "A"))

    def test_chat_vecchia_senza_narratore_resta_trasferibile(self):
        vecchia = "\n".join(
            riga for riga in CARD_ROMANZO.splitlines()
            if not riga.startswith(("NARRATORE", "TEMPO VERBALE"))
        )
        scheda = self.app["scheda_chat_guidata_per_sidebar"](
            [{"role": "assistant", "content": vecchia}], "Italiano", "GPT-5.4 (OpenAI)"
        )
        self.assertEqual(scheda["narratore"], narrative_prompts.NARRATORE_PREDEFINITO)
        obbligatori = self.app["campi_obbligatori_chat_guidata"](scheda["genere"])
        self.assertTrue(obbligatori.issubset(scheda))

    def test_manuale_richiede_ancora_il_punto_di_vista(self):
        obbligatori = self.app["campi_obbligatori_chat_guidata"]("Manuale Pratico")
        self.assertIn("punto_di_vista", obbligatori)
        self.assertNotIn("narratore", obbligatori)

    def test_prompt_deepseek_spiega_i_campi_dei_romanzi(self):
        prompt = self.app["prompt_scheda_chat_guidata_deepseek"]("Italiano", "DeepSeek V4 Pro", "A")
        self.assertIn("NARRATORE:", prompt)
        self.assertIn("PERSONAGGI E MONDO", prompt)


class ChatGuidataProgettoTests(unittest.TestCase):
    def setUp(self):
        self.app = parser_namespace()

    def test_romanzo_compila_verita_e_semi(self):
        card = CARD_ROMANZO + """VERITÀ NASCOSTA:
PREMESSA: Marco vuole scoprire chi ha ucciso il padre ma la sorella mente, altrimenti perderà la casa.
- Il padre è stato ucciso dal socio nel 1998.
MAPPA DEI SEMI:
- La lettera del padre | compare: Capitolo 1 | si risolve: Capitolo 10
La chiave del pozzo | compare: Capitolo 3 | si risolve: Capitolo 11
"""
        scheda = self.app["estrai_scheda_chat_guidata"](card)
        self.assertEqual(len(scheda["verita_nascosta"].splitlines()), 2)
        self.assertEqual(scheda["mappa_semi"].splitlines()[1], "- La chiave del pozzo | compare: Capitolo 3 | si risolve: Capitolo 11")
        self.assertEqual(len(book_project.leggi_semi(scheda["mappa_semi"])), 2)

    def test_saggio_e_manuale(self):
        saggio = self.app["estrai_scheda_chat_guidata"]("TESI CENTRALE: Comprare usato è più sicuro se si segue un metodo.\n- Idea 1\n- Idea 2\nAPPROFONDIMENTI: x")
        self.assertIn("- Idea 2", saggio["tesi_centrale"])
        manuale = self.app["estrai_scheda_chat_guidata"]("Objectives and prerequisites: - You will be able to inspect a car\n- Prerequisite: a torch")
        self.assertIn("inspect a car", manuale["obiettivi_prerequisiti"])

    def test_istruzioni_chat_contengono_il_progetto(self):
        prompt = self.app["prompt_scheda_chat_guidata_deepseek"]("English", "DeepSeek V4 Pro", "A")
        self.assertIn("TESI CENTRALE:", prompt)
        self.assertIn("COMPILALO SEMPRE TU", prompt)


class SceltaPersonalizzazioneMultilingueTests(unittest.TestCase):
    DOMANDA = {"role": "assistant", "content": "Vuoi personalizzare questo libro? A/B/C/D"}

    def setUp(self):
        self.scelta = parser_namespace()["scelta_personalizzazione_chat_deepseek"]

    def risposta(self, testo):
        return self.scelta([{"role": "user", "content": "Un thriller"}, self.DOMANDA, {"role": "user", "content": testo}])[0]

    def test_lettere_in_ogni_alfabeto(self):
        casi = {"d": "D", "D)": "D", "b.": "B", "Ｄ": "D", "Д": "D", "В": "B", "د": "D", "أ": "A",
                "opción C": "C", "Option b": "B", "вариант Д": "D", "选D": "D", "Je choisis A": "A", "ich wähle C": "C"}
        for testo, atteso in casi.items():
            with self.subTest(testo=testo):
                self.assertEqual(self.risposta(testo), atteso)

    def test_frasi_che_valgono_d_in_ogni_lingua(self):
        for testo in ("fai tu", "no sé, elige tú", "je ne sais pas", "keine Ahnung", "nu știu", "не знаю",
                      "لا أعرف", "你决定", "up to you", "proponi tu"):
            with self.subTest(testo=testo):
                self.assertEqual(self.risposta(testo), "D")

    def test_frasi_che_valgono_a(self):
        for testo in ("no", "Nein", "нет", "不用", "لا", "non voglio personalizzarlo"):
            with self.subTest(testo=testo):
                self.assertEqual(self.risposta(testo), "A")

    def test_frasi_normali_non_sono_scelte(self):
        for testo in ("a me piacerebbe un thriller", "в книге должен быть детектив", "с удовольствием расскажу"):
            with self.subTest(testo=testo):
                self.assertEqual(self.risposta(testo), "")
