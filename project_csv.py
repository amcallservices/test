"""Importazione ed esportazione CSV del progetto editoriale.

Il modulo gestisce solo file e fotografie serializzate: lo stato Streamlit e
l'interfaccia rimangono in app.py, così un CSV può essere verificato senza
toccare l'editor o la sidebar.
"""

from __future__ import annotations

import base64
import csv
import json
from io import StringIO
from typing import Any, Iterable, Mapping


LIMITE_CAMPO_CSV_PROGETTO = 50 * 1024 * 1024


def imposta_limite_lettura_csv_progetto() -> int:
    """Abilita fotografie CSV complete di libri, fonti e immagini."""
    limite = LIMITE_CAMPO_CSV_PROGETTO
    while limite >= 131_072:
        try:
            csv.field_size_limit(limite)
            return limite
        except OverflowError:
            limite //= 2
    return csv.field_size_limit()


def esporta_fotografia_csv(fotografia: Mapping[str, Any]) -> bytes:
    """Serializza un progetto completo, più copie leggibili di compatibilità."""
    immagini = {}
    for sezione, immagine in (fotografia.get("immagini", {}) or {}).items():
        dati = dict(immagine or {})
        raw = dati.pop("bytes", None)
        if raw:
            dati["bytes_b64"] = base64.b64encode(raw).decode("ascii")
        if dati:
            immagini[sezione] = dati
    fotografia_completa = {
        "versione": 2,
        "sidebar": dict(fotografia.get("sidebar", {}) or {}),
        "indice": str(fotografia.get("indice", "") or ""),
        "contenuti": dict(fotografia.get("contenuti", {}) or {}),
        "fonti": dict(fotografia.get("fonti", {}) or {}),
        "immagini": immagini,
    }
    fotografia_b64 = base64.b64encode(
        json.dumps(fotografia_completa, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=["tipo", "chiave", "valore"], lineterminator="\n")
    writer.writeheader()
    writer.writerow({"tipo": "formato", "chiave": "scrittore_site", "valore": "2"})
    writer.writerow({"tipo": "progetto", "chiave": "fotografia_completa_v2", "valore": fotografia_b64})
    for nome, valore in fotografia_completa["sidebar"].items():
        writer.writerow({"tipo": "sidebar", "chiave": nome, "valore": str(valore or "")})
    indice = fotografia_completa["indice"]
    writer.writerow({"tipo": "progetto", "chiave": "indice_raw", "valore": indice})
    writer.writerow({"tipo": "progetto", "chiave": "indice_backup", "valore": indice})
    for sezione, testo in fotografia_completa["contenuti"].items():
        if str(testo).strip():
            writer.writerow({"tipo": "sezione", "chiave": sezione, "valore": str(testo)})
    return buffer.getvalue().encode("utf-8-sig")


def importa_fotografia_csv(dati_grezzi: bytes, campi_sidebar_validi: Iterable[str]) -> dict[str, Any]:
    """Legge CSV nuovi e vecchi, senza troncare indice o manoscritto."""
    try:
        if not dati_grezzi:
            raise ValueError("il file è vuoto")
        testo_csv = None
        for codifica in ("utf-8-sig", "utf-16", "cp1252"):
            try:
                testo_csv = dati_grezzi.decode(codifica)
                break
            except UnicodeDecodeError:
                continue
        if testo_csv is None:
            raise ValueError("codifica non supportata")
        testo_csv = testo_csv.lstrip("\ufeff").replace("\x00", "")
        prima_riga, _, resto = testo_csv.partition("\n")
        separatore = ","
        if prima_riga.strip().lower().startswith("sep="):
            separatore = prima_riga.strip()[4:5] or ","
            testo_csv = resto
            prima_riga = testo_csv.partition("\n")[0]
        elif "\t" in prima_riga:
            separatore = "\t"
        elif ";" in prima_riga and "," not in prima_riga:
            separatore = ";"
        elif "|" in prima_riga and "," not in prima_riga:
            separatore = "|"
        imposta_limite_lettura_csv_progetto()
        righe = list(csv.DictReader(StringIO(testo_csv, newline=""), delimiter=separatore, quotechar='"'))
        righe = [{str(k or "").strip().lower().lstrip("\ufeff"): v for k, v in r.items()} for r in righe]
    except Exception as exc:
        raise ValueError(f"Il file CSV non è leggibile: {exc}") from exc
    if not righe or not {"tipo", "chiave", "valore"}.issubset(righe[0]):
        raise ValueError("Questo file non è un archivio CSV di Scrittore Site.")
    for riga in righe:
        if riga.get("tipo") == "progetto" and riga.get("chiave") == "fotografia_completa_v2":
            try:
                fotografia = json.loads(base64.b64decode(str(riga.get("valore") or "")).decode("utf-8"))
                indice = str(fotografia.get("indice", "") or "")
                if not indice.strip():
                    raise ValueError("la fotografia non contiene l'indice")
                immagini = {}
                for sezione, dati in (fotografia.get("immagini", {}) or {}).items():
                    elemento = dict(dati or {})
                    if elemento.get("bytes_b64"):
                        elemento["bytes"] = base64.b64decode(elemento.pop("bytes_b64"))
                    immagini[sezione] = elemento
                return {
                    "sidebar": dict(fotografia.get("sidebar", {}) or {}),
                    "indice_raw": indice,
                    "indice_backup": indice,
                    "contenuti": dict(fotografia.get("contenuti", {}) or {}),
                    "fonti": dict(fotografia.get("fonti", {}) or {}),
                    "immagini_capitoli": immagini,
                }
            except Exception as exc:
                raise ValueError(f"La fotografia completa del CSV è danneggiata: {exc}") from exc
    snapshot: dict[str, Any] = {
        "sidebar": {}, "indice_raw": "", "indice_backup": "", "contenuti": {}, "fonti": {}, "immagini_capitoli": {}
    }
    formato_valido = False
    validi = set(campi_sidebar_validi)
    for riga in righe:
        tipo, chiave, valore = riga.get("tipo", ""), riga.get("chiave", ""), riga.get("valore", "")
        if tipo == "formato" and chiave == "scrittore_site" and valore in {"1", "2"}:
            formato_valido = True
        elif tipo == "sidebar" and chiave in validi:
            snapshot["sidebar"][chiave] = valore
        elif tipo == "progetto" and chiave in {"indice_raw", "indice_backup"}:
            snapshot[chiave] = valore
        elif tipo == "sezione" and chiave:
            snapshot["contenuti"][chiave] = valore
    if not formato_valido:
        raise ValueError("Questo CSV non è stato esportato da Scrittore Site o usa un formato non supportato.")
    indice = str(snapshot["indice_raw"] or snapshot["indice_backup"] or "")
    if not indice.strip() and snapshot["contenuti"]:
        indice = "\n".join(snapshot["contenuti"].keys())
        snapshot["indice_raw"] = indice
        snapshot["indice_backup"] = indice
    if not indice.strip():
        raise ValueError("Il CSV è valido, ma non contiene un indice ripristinabile.")
    return snapshot
