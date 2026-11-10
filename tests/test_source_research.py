import source_research as sr
import source_research_i18n as sri

RISPOSTA = """MAPPA CONCETTUALE INTERNA
Il sonno si divide in fasi; la regolarità conta più della durata assoluta.

SCHEDE FONTI
### FONTE
Titolo: Guida al sonno sano
URL: https://www.esempio.org/sonno?utm=1
Pertinenza: 9
Tema: igiene del sonno negli adulti
Fatti chiave:
- La regolarità degli orari stabilizza il ritmo circadiano
- La luce serale ritarda l'addormentamento
Utile per: routine serale, abitudini quotidiane

### FONTE 2
**Titolo:** Pagina debole
**URL:** https://debole.example.com/x
**Pertinenza:** 3/10
Tema: generico

### FONTE
Titolo: Studio sulla caffeina
URL: <https://studi.example.edu/caffeina>.
Pertinenza: 8
Tema: caffeina e sonno
Fatti chiave:
1. La caffeina agisce per diverse ore
Utile per: alimentazione e sonno

REGISTRO FONTI WEB
- vecchio | https://ignorata.example.com | x
"""


def test_leggi_schede_separa_mappa_e_schede():
    mappa, schede = sr.leggi_schede(RISPOSTA)
    assert mappa.startswith("Il sonno si divide")
    assert "https://" not in mappa
    assert [s["pertinenza"] for s in schede] == [9, 3, 8]
    assert schede[0]["fatti"][1].startswith("La luce serale")
    assert schede[2]["url"] == "https://studi.example.edu/caffeina"
    assert all("ignorata" not in s["url"] for s in schede)


def test_unisci_schede_elimina_doppioni_e_deboli():
    _, schede = sr.leggi_schede(RISPOSTA)
    doppione = dict(schede[0], url="http://esempio.org/sonno/", pertinenza=7)
    unite = sr.unisci_schede(schede, [doppione], massimo=12)
    assert [s["pertinenza"] for s in unite] == [9, 8]
    assert len(sr.unisci_schede(schede, massimo=1)) == 1


def test_registro_compatibile_e_json():
    _, schede = sr.leggi_schede(RISPOSTA)
    registro = sr.registro_da_schede(schede[:1])
    assert registro.startswith("- Guida al sonno sano | https://www.esempio.org/sonno?utm=1 | 9/10")
    assert sr.schede_da_json(sr.schede_in_json(schede)) == schede
    assert sr.schede_da_json("non json") == []


def test_schede_per_sezione_sceglie_le_pertinenti_senza_url():
    _, schede = sr.leggi_schede(RISPOSTA)
    testo = sr.schede_per_sezione(schede, "Capitolo 3 La caffeina e il sonno", "alimentazione")
    assert testo.splitlines()[0] == "- caffeina e sonno"
    assert "http" not in testo
    # Nessuna corrispondenza: le due fonti più autorevoli.
    generico = sr.schede_per_sezione(schede, "Zzzz", "")
    assert "igiene del sonno" in generico


def test_abbina_schede_ai_capitoli():
    _, schede = sr.leggi_schede(RISPOSTA)
    capitoli = ["Capitolo 1 Routine serale", "Capitolo 2 Caffeina e alimentazione"]
    abbinamenti = sr.abbina_schede_ai_capitoli(schede, capitoli)
    assert abbinamenti["https://www.esempio.org/sonno?utm=1"][0] == "Capitolo 1 Routine serale"
    assert abbinamenti["https://studi.example.edu/caffeina"][0] == "Capitolo 2 Caffeina e alimentazione"


def test_domande_dalla_sidebar_saggio_e_romanzo():
    saggio = sr.domande_ricerca("Dormire bene", "Self-Help", "Come migliorare il sonno", "dormire 8 ore",
                                "- includere la caffeina\n- esempi di turnisti")
    assert len(saggio) == 9
    assert any("statistiche" in d for d in saggio)
    assert saggio[-1].endswith("esempi di turnisti")
    romanzo = sr.domande_ricerca("La nave", "Thriller / Noir", "Un delitto a Genova nel 1950", "tensione")
    assert any("Ambientazione" in d for d in romanzo)
    gruppi = sr.dividi_domande(saggio, 3)
    assert len(gruppi) == 3 and sum(map(len, gruppi)) == len(saggio)
    prompt = sr.prompt_ricerca_fonti(domande=gruppi[0], massimo_schede=6, titolo="T", genere="G",
                                     trama="A", obiettivo="O", lingua="Italiano", approfondimenti="")
    assert "SCHEDE FONTI" in prompt and "### FONTE" in prompt and gruppi[0][0] in prompt


def test_domande_scoperte_e_livelli():
    _, schede = sr.leggi_schede(RISPOSTA)
    scoperte = sr.domande_scoperte(["Effetti della caffeina sul sonno", "Storia dei treni a vapore"], schede)
    assert scoperte == ["Storia dei treni a vapore"]
    assert sr.normalizza_livello("APPROFONDITA") == "approfondita"
    assert sr.normalizza_livello("boh") == "standard"


def test_testi_in_tutte_le_lingue():
    lingue = ["Italiano", "English", "Español", "Français", "Deutsch", "Română", "Русский", "العربية", "中文"]
    chiavi = set(sri.TESTI["Italiano"])
    for lingua in lingue:
        assert set(sri.TESTI[lingua]) == chiavi, lingua
        assert "3" in sri.testo("expander", lingua, n=3)
