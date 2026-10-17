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


class DeepSeekCardTests(unittest.TestCase):
    def setUp(self):
        self.app = parser_namespace()

    def test_final_prompt_is_concise_and_preserves_selected_engine(self):
        prompt = self.app["prompt_scheda_chat_guidata_deepseek"]("Italiano", "DeepSeek V4 Pro")
        self.assertIn("CERVELLO AI deve essere esattamente: DeepSeek V4 Pro", prompt)
        self.assertIn("GENERE LETTERARIO:", prompt)
        self.assertIn("Manuale Pratico", prompt)
        self.assertIn("NON porre domande", prompt)

    def test_complete_card_is_transferable(self):
        card = re.sub(r"(?m)^(\s*)\d{1,2}[.)]\s+(?=[^\n:]{2,90}:)", r"\1", CARD)
        self.assertTrue(self.app["scheda_finale_deepseek_valida"](card))

    def test_missing_required_field_is_rejected(self):
        card = CARD.replace("10. OBIETTIVO DEL LIBRO: Aiutare il lettore a valutare un'auto usata.\n", "")
        card = re.sub(r"(?m)^(\s*)\d{1,2}[.)]\s+(?=[^\n:]{2,90}:)", r"\1", card)
        self.assertFalse(self.app["scheda_finale_deepseek_valida"](card))


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
        namespace = {
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
        valid = parser_namespace()["scheda_finale_deepseek_valida"]
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
        valid = parser_namespace()["scheda_finale_deepseek_valida"]
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


if __name__ == "__main__":
    unittest.main()
