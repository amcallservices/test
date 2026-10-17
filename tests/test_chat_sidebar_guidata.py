"""Regression tests for the guided chat without starting the Streamlit UI."""

import ast
import re
import time
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace


APP_TREE = ast.parse((Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8"))


def load_functions(names, namespace):
    for node in APP_TREE.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            exec(compile(ast.Module(body=[node], type_ignores=[]), "app.py", "exec"), namespace)
    return namespace


def parser_namespace():
    constants = {
        "CAMPI_CHAT_GUIDATA_SIDEBAR",
        "CAMPI_CHAT_GUIDATA_ETICHETTE_TRADOTTE",
        "CAMPI_CHAT_GUIDATA_OBBLIGATORI",
        "OPZIONI_CHAT_GUIDATA",
    }
    languages = (
        "Italiano", "English", "Español", "Français", "Deutsch",
        "Română", "Русский", "العربية", "中文",
    )
    namespace = {"re": re, "TRADUZIONI": {language: {} for language in languages}}
    for node in APP_TREE.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in constants for target in node.targets
        ):
            exec(compile(ast.Module(body=[node], type_ignores=[]), "app.py", "exec"), namespace)
    return load_functions(
        {
            "_valore_scelta_chat_guidata",
            "estrai_scheda_chat_guidata",
            "estrai_scheda_chat_guidata_da_cronologia",
            "scheda_chat_guidata_per_sidebar",
            "risposta_chat_guidata_trasferibile",
        },
        namespace,
    )


COMPLETE_CARD = """1. TITOLO DEL LIBRO: Il giardino delle idee
2. NOME AUTORE: Ada Rossi
3. LINGUA: Italiano
4. GENERE LETTERARIO: Manuale Pratico
5. TIPOLOGIA SCRITTURA: Standard
6. STILE DI RACCONTO: Diretto e Pratico (Action-oriented)
7. PUNTO DI VISTA: Tu (Diretto, confidenziale e personale)
8. LUNGHEZZA DELLE SEZIONI: Standard KDP
9. CERVELLO AI: DeepSeek V4 Pro
10. OBIETTIVO DEL LIBRO: Aiutare il lettore a coltivare idee.
11. RISULTATO FINALE DESIDERATO: Un progetto personale concreto.
12. TRAMA O ARGOMENTO: Metodi creativi per principianti.
"""


class GuidedChatParsingTests(unittest.TestCase):
    def setUp(self):
        self.app = parser_namespace()

    def test_numbered_deepseek_card_is_transferable(self):
        self.assertTrue(
            self.app["risposta_chat_guidata_trasferibile"](
                COMPLETE_CARD, [], "Italiano", "DeepSeek V4 Pro"
            )
        )

    def test_partial_card_is_not_transferable(self):
        partial = COMPLETE_CARD.replace("10. OBIETTIVO DEL LIBRO: Aiutare il lettore a coltivare idee.\n", "")
        self.assertFalse(
            self.app["risposta_chat_guidata_trasferibile"](
                partial, [], "Italiano", "DeepSeek V4 Pro"
            )
        )

    def test_selected_language_is_not_required_in_model_text(self):
        without_language = COMPLETE_CARD.replace("3. LINGUA: Italiano\n", "")
        self.assertTrue(
            self.app["risposta_chat_guidata_trasferibile"](
                without_language, [], "English", "DeepSeek V4 Pro"
            )
        )

    def test_translated_labels_remain_transferable(self):
        fields = self.app["estrai_scheda_chat_guidata"](COMPLETE_CARD)
        italian_labels = self.app["CAMPI_CHAT_GUIDATA_SIDEBAR"]
        translated_labels = self.app["CAMPI_CHAT_GUIDATA_ETICHETTE_TRADOTTE"]
        languages = ("English", "Español", "Français", "Deutsch", "Română", "Русский", "العربية", "中文")
        for index, language in enumerate(languages):
            card = "\n".join(
                f"{translated_labels[field][index]}: {language if field == 'lingua' else fields[field]}"
                for field in italian_labels.values() if field in fields
            )
            with self.subTest(language=language):
                self.assertTrue(
                    self.app["risposta_chat_guidata_trasferibile"](
                        card, [], language, "DeepSeek V4 Pro"
                    )
                )


class GuidedChatBillingTests(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.refunds = []
        self.logged = []
        self.deepseek = True
        self.answer = SimpleNamespace(
            choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content="Scheda completa"))]
        )
        completions = SimpleNamespace(create=self.create_response)
        client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
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
            "usa_deepseek_pro": lambda: self.deepseek,
            "charge_credits": lambda *args, **kwargs: "charged-reference",
            "refund_credits": lambda *args, **kwargs: self.refunds.append((args, kwargs)),
            "registra_esito_chiamata_ai": lambda *args, **kwargs: self.logged.append((args, kwargs)),
            "_client_e_modello_testuale": lambda model: (client, "deepseek-v4-pro"),
        }
        self.app = load_functions({"chiedi_gpt"}, namespace)

    def create_response(self, **request):
        self.requests.append(request)
        return self.answer

    def call_chat(self, validator=None):
        return self.app["chiedi_gpt"](
            "Brief", "Prepara la scheda", model="gpt-editorial",
            reason="chat_sidebar_guidata", timeout_seconds=90,
            max_completion_tokens=2600, validatore_risposta=validator,
        )

    def test_deepseek_guided_chat_disables_thinking(self):
        self.assertEqual(self.call_chat(lambda text: text == "Scheda completa"), "Scheda completa")
        self.assertEqual(self.requests[0]["extra_body"], {"thinking": {"type": "disabled"}})
        self.assertEqual(self.requests[0]["max_tokens"], 2600)
        self.assertEqual(self.refunds, [])

    def test_gpt_guided_chat_keeps_its_existing_request_format(self):
        self.deepseek = False
        self.assertEqual(self.call_chat(), "Scheda completa")
        self.assertEqual(self.requests[0]["max_completion_tokens"], 2600)
        self.assertNotIn("extra_body", self.requests[0])

    def test_truncated_response_is_refunded(self):
        self.answer.choices[0].finish_reason = "length"
        self.assertTrue(self.call_chat().startswith("ERRORE:"))
        self.assertEqual(len(self.refunds), 1)
        self.assertIs(self.logged[0][0][0], self.answer)
        self.assertTrue(self.logged[0][1]["rimborsata"])

    def test_non_transferable_final_card_is_refunded(self):
        self.assertTrue(self.call_chat(lambda text: False).startswith("ERRORE:"))
        self.assertEqual(len(self.refunds), 1)


if __name__ == "__main__":
    unittest.main()
