"""Regression tests for the DeepSeek-only guided sidebar chat path."""

import ast
import re
import time
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace


TREE = ast.parse((Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8"))


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
        "TRADUZIONI": {name: {} for name in ("Italiano", "English", "Español", "Français", "Deutsch")},
    }
    for node in TREE.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in names for target in node.targets
        ):
            exec(compile(ast.Module(body=[node], type_ignores=[]), "app.py", "exec"), namespace)
    return load_functions({
        "_valore_scelta_chat_guidata", "estrai_scheda_chat_guidata",
        "scelta_personalizzazione_chat_deepseek", "campi_personalizzazione_deepseek",
        "prompt_scheda_chat_guidata_deepseek", "scheda_finale_deepseek_valida",
    }, namespace)


CARD = """1. TITOLO DEL LIBRO: Comprare un'auto usata senza fregature
2. NOME AUTORE: [Inserisci il tuo nome]
3. LINGUA: Italiano
4. GENERE LETTERARIO: Manuale Pratico
5. TIPOLOGIA SCRITTURA: Standard
6. STILE DI RACCONTO: Diretto e Pratico (Action-oriented)
7. PUNTO DI VISTA: Tu (Diretto, confidenziale e personale)
8. LUNGHEZZA DELLE SEZIONI: Standard KDP
9. CERVELLO AI: DeepSeek V4 Pro
10. OBIETTIVO DEL LIBRO: Aiutare il lettore a valutare un'auto usata.
11. RISULTATO FINALE DESIDERATO: Una scelta d'acquisto più consapevole.
12. TRAMA O ARGOMENTO: Controlli documentali e meccanici per principianti.
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
        card = CARD.replace("10. OBIETTIVO DEL LIBRO: Aiutare il lettore a valutare un'auto usata.\n", "")
        card = self._without_numbers(card) + PERSONALIZATION
        self.assertFalse(self.app["scheda_finale_deepseek_valida"](card, "D"))


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
            "TIMEOUT_INDICE_SECONDI": 150,
            "CommercialCreditError": type("CommercialCreditError", (Exception,), {}),
            "uuid": uuid,
            "time": time,
            "re": re,
            "usa_deepseek_pro": lambda: self.deepseek,
            "charge_credits": lambda *args, **kwargs: "charged-reference",
            "refund_credits": lambda *args, **kwargs: self.refunds.append((args, kwargs)),
            "registra_esito_chiamata_ai": lambda *args, **kwargs: self.logged.append((args, kwargs)),
            "_client_e_modello_testuale": lambda model: (client, "deepseek-v4-pro" if self.deepseek else "gpt-editorial"),
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

    def test_deepseek_does_not_spend_output_on_thinking(self):
        valid = lambda text: parser_namespace()["scheda_finale_deepseek_valida"](text, "A")
        result = self.call_chat(valid)
        self.assertTrue(result.startswith("TITOLO DEL LIBRO:"))
        self.assertEqual(self.requests[0]["extra_body"], {"thinking": {"type": "disabled"}})
        self.assertEqual(self.requests[0]["max_tokens"], 3000)
        self.assertEqual(self.refunds, [])

    def test_short_dialogue_reply_remains_allowed(self):
        self.answer.choices[0].message.content = "Vuoi personalizzare il libro? A, B, C o D?"
        self.assertIn("personalizzare", self.call_chat())
        self.assertEqual(self.refunds, [])

    def test_incomplete_card_is_refunded(self):
        self.answer.choices[0].message.content = "TITOLO DEL LIBRO: Auto usate"
        valid = lambda text: parser_namespace()["scheda_finale_deepseek_valida"](text, "A")
        self.assertTrue(self.call_chat(valid).startswith("ERRORE:"))
        self.assertEqual(len(self.refunds), 1)
        self.assertIs(self.logged[0][0][0], self.answer)

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

    def test_niche_final_uses_output_budget_without_thinking(self):
        detailed = "PROMPT FINALE PER CHAT GUIDATA SCRITTORE SITE\n" + (
            "1. Mercato italiano e libro sulle auto usate: controlli verificabili.\n" * 35
        )
        self.answer.choices[0].message.content = detailed
        result = self.app["chiedi_gpt"](
            "Report della nicchia", "Crea prompt", model="gpt-editorial",
            reason="chat_nicchia_prompt_finale", max_completion_tokens=4200,
        )
        self.assertEqual(result, detailed.strip())
        self.assertEqual(self.requests[0]["extra_body"], {"thinking": {"type": "disabled"}})
        self.assertEqual(self.requests[0]["max_tokens"], 4200)
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
    def test_only_deepseek_gets_detailed_eight_part_brief(self):
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
        self.assertNotIn("otto parti numerate", gpt_system)
        self.assertEqual(gpt_options["max_completion_tokens"], 2600)

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
