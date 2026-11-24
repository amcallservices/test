import json
import re
from pathlib import Path

import user_tips as ut

LINGUE = ut.LINGUE


def stato(**v):
    base = {"job_attivo": False, "non_salvato": False, "firma_contenuti": "f1", "indice_pronto": False,
            "sezioni_scritte": 0, "sezioni_previste": 0, "brief_pronto": False, "tipo_opera": "saggistica",
            "livello_ricerca": "standard", "livello_consigliato": "standard", "scheda_personaggi_vuota": True}
    base.update(v)
    return base


def test_regole_dei_suggerimenti():
    assert ut.suggerimenti_attivi(stato()) == []
    assert ut.suggerimenti_attivi(stato(indice_pronto=True)) == ["dopo_indice"]
    assert ut.suggerimenti_attivi(stato(non_salvato=True, indice_pronto=True)) == ["salva", "dopo_indice"]
    assert ut.suggerimenti_attivi(stato(brief_pronto=True, livello_consigliato="approfondita")) == ["approfondita"]
    assert ut.suggerimenti_attivi(stato(brief_pronto=True, livello_consigliato="approfondita", livello_ricerca="approfondita")) == []
    assert "personaggi" in ut.suggerimenti_attivi(stato(tipo_opera="narrativa", indice_pronto=True, sezioni_scritte=1))
    assert ut.suggerimenti_attivi(stato(indice_pronto=True, sezioni_scritte=5, sezioni_previste=5)) == ["fine_libro"]
    # Durante la stesura automatica nessun suggerimento.
    assert ut.suggerimenti_attivi(stato(job_attivo=True, non_salvato=True)) == []
    # Mai più di due.
    assert len(ut.suggerimenti_attivi(stato(non_salvato=True, indice_pronto=True, tipo_opera="narrativa"))) == 2


def test_chiusura_dei_suggerimenti():
    s = stato(non_salvato=True, indice_pronto=True, firma_contenuti="A")
    assert ut.suggerimenti_attivi(s, {"dopo_indice": ""}) == ["salva"]
    # "salva" chiuso resta nascosto finché il contenuto non cambia.
    assert ut.suggerimenti_attivi(s, {"salva": "A", "dopo_indice": ""}) == []
    assert ut.suggerimenti_attivi(stato(non_salvato=True, firma_contenuti="B", indice_pronto=True),
                                  {"salva": "A", "dopo_indice": ""}) == ["salva"]


def test_testi_completi_in_tutte_le_lingue():
    for lingua in LINGUE:
        assert set(ut.SUGGERIMENTI[lingua]) == set(ut.SUGGERIMENTI["Italiano"]), lingua
        assert len(ut.CONSIGLI_ATTESA[lingua]) == len(ut.CONSIGLI_ATTESA["Italiano"]), lingua
        assert set(ut.SCHEDE_VUOTE[lingua]) == set(ut.SCHEDE_VUOTE["Italiano"]), lingua
        assert set(ut.AIUTI_CAMPI[lingua]) == set(ut.AIUTI_CAMPI["Italiano"]), lingua
        assert len(ut.TOUR[lingua]["passi"]) == len(ut.SELETTORI_TOUR), lingua
        assert ut.consiglio_attesa(lingua, 3).startswith("💡 ")
        assert ut.scheda_vuota("anteprima", lingua)[2] == 3
        assert ut.aiuto_campo("book_goal", lingua)
    assert ut.consiglio_attesa("Italiano", 0) != ut.consiglio_attesa("Italiano", 1)


def test_dati_tour_serializzabili_e_rtl():
    dati = ut.dati_tour("العربية")
    assert dati["rtl"] is True and len(dati["passi"]) == 24
    caricati = json.loads(json.dumps(dati, ensure_ascii=False))
    assert caricati["passi"][1]["sel"] == ".st-key-ss_blocco_crediti"
    assert ut.dati_tour("Italiano")["rtl"] is False
    # Le schede del percorso vengono aperte tutte, una volta ciascuna (0…6).
    schede = [p["scheda"] for p in caricati["passi"] if p["scheda"] is not None]
    assert schede == list(range(7))


def test_ogni_comando_della_visita_esiste():
    base = Path(__file__).resolve().parents[1]
    sorgente = (base / "app.py").read_text(encoding="utf-8") + (base / "commercial_layer.py").read_text(encoding="utf-8")
    for passo in ut.SELETTORI_TOUR:
        for selettore in (passo["sel"], passo.get("alt", "")):
            for chiave in re.findall(r"\.st-key-([a-z_]+)", selettore):
                assert f'key="{chiave}"' in sorgente, chiave
            for classe in re.findall(r"^\.(ss-[a-z-]+)$", selettore):
                assert classe in sorgente, classe


def test_ogni_campo_sidebar_ha_una_spiegazione():
    sorgente = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
    usati = set(re.findall(r'aiuto_campo\("([a-z_]+)"', sorgente))
    assert usati == set(ut.AIUTI_CAMPI["Italiano"])
    script = (Path(__file__).resolve().parents[1] / "assets" / "editor_tour.js").read_text(encoding="utf-8")
    assert "__DATI_TOUR__" in script and "__FORZA_TOUR__" in script and "localStorage" in script
