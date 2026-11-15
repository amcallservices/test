"""Le ricerche parallele non devono riusare lo stesso riferimento su Supabase.

La tabella writer_ai_usage_events ha unique (user_id, reference): un secondo
evento con lo stesso riferimento verrebbe rifiutato e il suo costo perso.
"""
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from types import SimpleNamespace

import source_research

TREE = ast.parse((Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8"))
NOMI = {"ricerca_preliminare_per_indice", "_ricerche_web_in_parallelo", "livello_ricerca_fonti", "costo_ricerca_fonti"}

RISPOSTA = """MAPPA CONCETTUALE INTERNA
Mappa.

SCHEDE FONTI
### FONTE
Titolo: Uno
URL: https://uno.example.org/{n}
Pertinenza: 9
Tema: sonno
Fatti chiave:
- fatto
Utile per: tutto
"""


def carica(livello, risposte):
    eventi, rimborsi, stato = [], [], {"profondita_ricerca_fonti": livello}
    contatore = iter(range(100))

    def esegui(istruzioni, deepseek):
        n = next(contatore)
        esito = risposte[n] if n < len(risposte) else risposte[-1]
        if isinstance(esito, Exception):
            raise esito
        return SimpleNamespace(output_text=esito.format(n=n))

    def registra(risposta, *, riferimento=None, amount=0, riferimento_padre="", **_):
        eventi.append((riferimento, amount, riferimento_padre))

    ns = {
        "st": SimpleNamespace(session_state=stato),
        "ricerca_fonti_core": source_research,
        "CREDIT_COSTS": {"indice_ricerca_web": 4, "indice_ricerca_web_approfondita": 8},
        "ThreadPoolExecutor": ThreadPoolExecutor, "as_completed": as_completed,
        "_esegui_ricerca_web_fonti": esegui,
        "firma_ricerca_preliminare": lambda *a: "firma",
        "usa_deepseek_pro": lambda: False,
        "MODELLO_DEEPSEEK_PRO": "ds", "MODELLO_ANALISI_FONTI": "gpt",
        "addebita_azione_diretta": lambda *a, **k: "RIF",
        "registra_esito_chiamata_ai": registra,
        "refund_credits": lambda *a, **k: rimborsi.append(k.get("amount")),
        "separa_mappa_e_registro_fonti_web": lambda t: (t, ""),
        "conserva_solo_fonti_web_selezionate": lambda r: r,
        "salva_progetto_corrente": lambda *a: True,
        "sidebar_memorizzata_corrente": lambda: {},
        "CHIAVE_MEMORIA_SEZIONI": "mem",
    }
    for nodo in TREE.body:
        if isinstance(nodo, ast.FunctionDef) and nodo.name in NOMI:
            exec(compile(ast.Module(body=[nodo], type_ignores=[]), "app.py", "exec"), ns)
    return ns, eventi, rimborsi, stato


def test_approfondita_un_riferimento_per_evento():
    # Solo 1 fonte per ricerca: scatta anche il secondo giro.
    ns, eventi, rimborsi, stato = carica("approfondita", [RISPOSTA])
    assert ns["ricerca_preliminare_per_indice"]("T", "Saggio", "A", "O", "Italiano", "")
    riferimenti = [e[0] for e in eventi]
    assert len(riferimenti) == 4 and len(set(riferimenti)) == 4
    assert riferimenti[0] == "RIF"
    # Un solo evento porta il costo; gli altri sono fasi collegate.
    assert [e[1] for e in eventi].count(8) == 1
    assert all(e[2] == "RIF" for e in eventi[1:])
    assert rimborsi == []


def test_fallimento_parziale_e_totale():
    ns, eventi, rimborsi, _ = carica("approfondita", [RISPOSTA, TimeoutError(), TimeoutError()] + [RISPOSTA])
    assert ns["ricerca_preliminare_per_indice"]("T", "Saggio", "A", "O", "Italiano", "")
    assert len({e[0] for e in eventi}) == len(eventi)

    ns, eventi, rimborsi, stato = carica("standard", [TimeoutError()])
    assert ns["ricerca_preliminare_per_indice"]("T", "Saggio", "A", "O", "Italiano", "") == ""
    assert rimborsi == [4]
    assert len({e[0] for e in eventi}) == len(eventi)

    # Risposta senza testo: evento riuscito + evento di rimborso, riferimenti diversi.
    ns, eventi, rimborsi, _ = carica("standard", [""])
    assert ns["ricerca_preliminare_per_indice"]("T", "Saggio", "A", "O", "Italiano", "") == ""
    assert rimborsi == [4]
