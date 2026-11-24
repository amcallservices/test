"""La nuova home si costruisce in tutte le 9 lingue, con le stesse sezioni."""
from home_page import build_home_html
from home_page_copy import HOME_V2_COPY
import commercial_layer as c


def _dati(lingua):
    A = c.HOME_AI_ENGINES_COPY[lingua]
    return {
        "nav": c.HOME_NAVIGATION[lingua], "community": c.HOME_BODY_COPY[lingua]["community"],
        "store": c.HOME_STORE_LABELS[lingua], "menu": c.HOME_MENU_LABELS[lingua], "etichetta_lingua": "Lingua",
        "sigla": c.HOME_LANGUAGE_CODES[lingua],
        "lingue": [(n, s, f"?lang={s}") for n, s in c.HOME_LANGUAGE_CODES.items()],
        "link_registrati": "?azione=registrati", "link_accedi": "?azione=accedi",
        "kicker": c.HOME_NUOVA_COPY[lingua]["kicker"], "titolo": "T<br><em>L</em>",
        "sottotitolo": "s", "inizia": "i", "accedi": "a", "libro": c.HOME_INTERACTIVE_BOOK[lingua],
        "fiducia": c.HOME_TRUST_STRIP[lingua], "slide": c.HOME_SLIDES[lingua]["slide"],
        "prec": "p", "succ": "n", "vantaggi": c.HOME_ADVANTAGE_CARDS[lingua],
        "cervelli": {"titolo": A[0], "pro_nome": A[2], "pro_testo": A[3], "pro_costo": A[4],
                     "eco_nome": A[5], "eco_testo": A[6], "eco_costo": A[7], "nota": ""},
        "pacchetti": [{"nome": "Creator", "prezzo": "25 €", "crediti": "375", "pro": 4, "eco": 13, "consigliato": True}],
        "consigliato": "x", "nota_stime": "n", "faq_titolo": "FAQ", "faq": [("q", "a")],
        "guide_titolo": "g", "guide_testo": "g", "guide": [("it", "s", "app/static/x.pdf", "x.pdf")],
        "finale_titolo": "f", "finale_testo": "f", "versione": "v",
    }


def test_tutte_le_lingue_hanno_gli_stessi_testi():
    chiavi = set(HOME_V2_COPY["Italiano"])
    assert set(HOME_V2_COPY) == set(c.HOME_COPY)
    for lingua, testi in HOME_V2_COPY.items():
        assert set(testi) == chiavi, lingua
        assert len(testi["step_subs"]) == 5 and len(testi["slide_h3"]) == 5
        assert len(testi["funz"]) == 6 and len(testi["vant_punti"]) == 5


def test_home_costruita_in_ogni_lingua():
    for lingua in c.HOME_COPY:
        html = build_home_html(lingua, _dati(lingua))
        assert "\n" not in html  # niente righe: il Markdown di Streamlit non la tocca
        for ancora in ("ss-percorso", "ss-funzioni", "ss-vantaggi", "ss-cervelli", "ss-crediti", "ss-faq", "ss-guide"):
            assert f"id='{ancora}'" in html, (lingua, ancora)
        assert "instagram.com/scrittore.site" in html and "liberamente.site" in html and "selfpublishingitalia.site" in html
        assert html.count("class='ss2-slide") == 5
        assert ("dir='rtl'" in html) == (lingua == "العربية")
