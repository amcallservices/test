"""Nomi dei due cervelli mostrati all'utente, nelle 9 lingue di Scrittore Site.

I valori tecnici salvati nei progetti e usati dal codice restano invariati
("GPT-5.4 (OpenAI)" e "DeepSeek V4 Pro"): qui cambia solo il nome visibile.
"""

from __future__ import annotations

VALORE_COSTOSO = "GPT-5.4 (OpenAI)"
VALORE_ECONOMICO = "DeepSeek V4 Pro"

NOMI = {
    "Italiano": ("Cervello costoso", "Cervello economico"),
    "English": ("Expensive brain", "Economy brain"),
    "Español": ("Cerebro caro", "Cerebro económico"),
    "Français": ("Cerveau coûteux", "Cerveau économique"),
    "Deutsch": ("Teures Gehirn", "Sparsames Gehirn"),
    "Română": ("Creier scump", "Creier economic"),
    "Русский": ("Дорогой мозг", "Экономный мозг"),
    "العربية": ("العقل المكلف", "العقل الاقتصادي"),
    "中文": ("高价大脑", "经济大脑"),
}


def nome_cervello(valore: str, lingua: str = "Italiano") -> str:
    """Nome visibile di un cervello a partire dal suo valore tecnico."""
    costoso, economico = NOMI.get(lingua, NOMI["Italiano"])
    testo = str(valore or "")
    if not testo:
        return ""
    return economico if "deepseek" in testo.casefold() else costoso
