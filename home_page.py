"""Home pubblica "inchiostro e oro": stessa struttura dell'anteprima approvata.

Costruisce l'HTML della home (una sola stringa, senza righe vuote, così il
Markdown di Streamlit la lascia intatta). Grafica in assets/home_v2.css,
interazioni in assets/home_v2.js. I pulsanti di accesso sono link
(?azione=registrati / ?azione=accedi): lo script li collega ai pulsanti
nascosti di Streamlit, così si apre il modulo senza ricaricare la pagina.
"""

from __future__ import annotations

from html import escape
from typing import Any

from home_page_copy import HOME_V2_COPY

# Icone a tratto (niente emoji nella nuova home).
_ICONE = {
    "freccia": "<line x1='5' y1='12' x2='19' y2='12'></line><polyline points='13 6 19 12 13 18'></polyline>",
    "spunta": "<polyline points='20 6 9 17 4 12'></polyline>",
    "lente": "<circle cx='11' cy='11' r='7'></circle><line x1='21' y1='21' x2='16.6' y2='16.6'></line>",
    "memoria": "<path d='M12 3v18'></path><path d='M5 8h14'></path><path d='M5 16h14'></path>",
    "lucchetto": "<rect x='3' y='11' width='18' height='10' rx='2'></rect><path d='M7 11V7a5 5 0 0 1 10 0v4'></path>",
    "salva": "<path d='M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z'></path><polyline points='17 21 17 13 7 13 7 21'></polyline>",
    "globo": "<circle cx='12' cy='12' r='9'></circle><path d='M3 12h18'></path><path d='M12 3a14 14 0 0 1 0 18a14 14 0 0 1 0-18'></path>",
    "elenco": "<line x1='8' y1='6' x2='21' y2='6'></line><line x1='8' y1='12' x2='21' y2='12'></line><line x1='8' y1='18' x2='21' y2='18'></line><line x1='3' y1='6' x2='3.01' y2='6'></line><line x1='3' y1='12' x2='3.01' y2='12'></line><line x1='3' y1='18' x2='3.01' y2='18'></line>",
    "libro": "<path d='M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z'></path><path d='M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z'></path>",
    "aiuto": "<circle cx='12' cy='12' r='9'></circle><path d='M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3'></path><line x1='12' y1='17' x2='12.01' y2='17'></line>",
    "file": "<path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'></path><polyline points='14 2 14 8 20 8'></polyline>",
    "kdp": "<path d='M4 19.5A2.5 2.5 0 0 1 6.5 17H20'></path><path d='M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z'></path>",
    "scarica": "<path d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'></path><polyline points='7 10 12 15 17 10'></polyline><line x1='12' y1='15' x2='12' y2='3'></line>",
    "persone": "<path d='M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'></path><circle cx='9' cy='7' r='4'></circle><path d='M23 21v-2a4 4 0 0 0-3-3.87'></path><path d='M16 3.13a4 4 0 0 1 0 7.75'></path>",
    "instagram": "<rect x='3' y='3' width='18' height='18' rx='5'></rect><circle cx='12' cy='12' r='4'></circle><circle cx='17.5' cy='6.5' r='0.7' fill='currentColor' stroke='none'></circle>",
    "esterno": "<line x1='7' y1='17' x2='17' y2='7'></line><polyline points='7 7 17 7 17 17'></polyline>",
    "giu": "<polyline points='6 9 12 15 18 9'></polyline>",
    "sx": "<polyline points='15 18 9 12 15 6'></polyline>",
    "dx": "<polyline points='9 18 15 12 9 6'></polyline>",
    "pausa": "<rect x='6' y='5' width='4' height='14' rx='1' fill='currentColor' stroke='none'></rect><rect x='14' y='5' width='4' height='14' rx='1' fill='currentColor' stroke='none'></rect>",
    "play": "<polygon points='7 4 20 12 7 20 7 4' fill='currentColor' stroke='none'></polygon>",
    "piu": "<line x1='12' y1='5' x2='12' y2='19'></line><line x1='5' y1='12' x2='19' y2='12'></line>",
}


def _icona(nome: str, classe: str = "", larghezza: str = "2") -> str:
    return (f"<svg class='ss2-ico {classe}' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='{larghezza}'"
            f" stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'>{_ICONE[nome]}</svg>")


def _e(testo: Any) -> str:
    """Testo semplice nell'HTML (i titoli con <em> o <br> passano da _h)."""
    return escape(str(testo), quote=True)


def _h(testo: Any) -> str:
    """Testo che può contenere solo i nostri tag <em>/<br>."""
    return str(testo)


def build_home_html(lingua: str, d: dict[str, Any]) -> str:
    """HTML completo della home. `d` raccoglie i testi già tradotti altrove."""
    T = HOME_V2_COPY[lingua]
    rtl = lingua == "العربية"
    direzione = "rtl" if rtl else "ltr"
    link_reg, link_acc = d["link_registrati"], d["link_accedi"]
    N = d["nav"]

    # ---------- Menu ----------
    voci = "".join(
        f"<a class='ss2-nav-link' href='#{ancora}'>{_e(etichetta)}</a>"
        for ancora, etichetta in zip(("ss-percorso", "ss-funzioni", "ss-vantaggi", "ss-cervelli", "ss-crediti", "ss-faq", "ss-guide"), N[:7])
    )
    voci += (
        f"<a class='ss2-nav-link ss2-nav-ico' href='https://www.instagram.com/scrittore.site/' target='_blank' rel='noopener noreferrer'>{_icona('instagram')}{_e(N[7])}</a>"
        f"<a class='ss2-nav-link ss2-nav-ico' href='https://selfpublishingitalia.site/' target='_blank' rel='noopener noreferrer'>{_icona('persone')}{_e(d['community'])}</a>"
        f"<a class='ss2-nav-store' href='https://liberamente.site/' target='_blank' rel='noopener noreferrer'>{_icona('esterno', larghezza='2.2')}{_e(d['store'])}</a>"
    )
    lingue = "".join(
        f"<a href='{_e(url)}' target='_self' hreflang='{sigla.lower()}' class='ss2-lingua{' attiva' if nome == lingua else ''}'>"
        f"<span>{_e(nome)}</span><small>{sigla}</small></a>"
        for nome, sigla, url in d["lingue"]
    )
    menu_lingue = (
        f"<details class='ss2-lingue'><summary aria-label='{_e(d['etichetta_lingua'])}: {_e(lingua)}'>{_icona('globo')}"
        f"<b>{d['sigla']}</b>{_icona('giu', larghezza='2.6')}</summary><div class='ss2-lingue-elenco'>{lingue}</div></details>"
    )
    logo = (
        "<a class='ss2-logo' href='#ss-top'><img src='app/static/scrittore-site-logo-112.png' alt='' width='42' height='42'>"
        "<span>Scrittore Site</span></a>"
    )
    header = (
        f"<header class='ss2-header'><div class='ss2-wrap ss2-header-riga'>{logo}"
        f"<nav class='ss2-nav' aria-label='{_e(d['menu'])}'>{voci}{menu_lingue}</nav>"
        f"<details class='ss2-menu-mobile'><summary>{_e(d['menu'])}{_icona('giu', larghezza='2.6')}</summary>"
        f"<nav aria-label='{_e(d['menu'])}'>{voci}</nav></details>"
        f"<div class='ss2-lingue-mobile'>{menu_lingue}</div></div></header>"
    )

    # ---------- Prima schermata ----------
    B = d["libro"]
    voci_indice = list(B["items"])
    indice_libro = "".join(
        f"<div class='ss2-libro-voce{' attuale' if n == 0 else ''}'><span>{_e(voce)}</span>"
        + (f"<span class='ss2-libro-stato'>{_e(T['in_scrittura'])}</span>" if n == 0 else "")
        + "</div>"
        for n, voce in enumerate(voci_indice)
    )
    righe = "".join(f"<i class='ss2-riga ss2-w{n + 1}'></i>" for n in range(4))
    hero = (
        f"<section id='ss-top' class='ss2-wrap ss2-hero'>"
        f"<div class='ss2-hero-testo'>"
        f"<span class='ss2-kicker ss2-sale'><i></i>{_e(d['kicker'])}</span>"
        f"<h1 class='ss2-h1 ss2-sale ss2-r2'>{_h(d['titolo'])}</h1>"
        f"<p class='ss2-lead ss2-sale ss2-r3'>{_e(d['sottotitolo'])}</p>"
        f"<div class='ss2-azioni ss2-sale ss2-r4'>"
        f"<a class='ss2-btn-oro ss2-btn-grande' href='{_e(link_reg)}' target='_self' data-azione='registrati'>{_e(d['inizia'])}{_icona('freccia', larghezza='2.4')}</a>"
        f"<a class='ss2-btn-vuoto ss2-btn-grande' href='{_e(link_acc)}' target='_self' data-azione='accedi'>{_e(d['accedi'])}</a></div>"
        f"<div class='ss2-rassicura'><span>{_icona('spunta', larghezza='2.4')}{_e(T['nocard'])}</span>"
        f"<span>{_icona('spunta', larghezza='2.4')}{_e(T['stripe'])}</span></div></div>"
        f"<div class='ss2-hero-visuale'><div class='ss2-alone' aria-hidden='true'></div>"
        f"<div class='ss2-libro' role='img' aria-label='{_e(B['chapter'])}: {_e(B['chapter_title'])}'>"
        f"<div class='ss2-pag ss2-pag-sx'><span class='ss2-occhiello'>{_e(B['chapter'])}</span>"
        f"<span class='ss2-libro-titolo'>{_e(B['chapter_title'])}</span><span class='ss2-filetto'></span>{righe}"
        f"<span class='ss2-riga-cursore'><i class='ss2-riga ss2-w5'></i><b class='ss2-cursore'></b></span>"
        f"<span class='ss2-numero-pagina'>— 1 —</span></div>"
        f"<div class='ss2-pag ss2-pag-dx'><span class='ss2-occhiello'>{_e(B['index'])}</span>{indice_libro}"
        f"<div class='ss2-libro-barra'><div><i></i></div><span>{_e(T['scrittura_corso'])}</span></div></div></div>"
        f"<div class='ss2-chip ss2-chip-a ss2-galleggia'>{_icona('lente')}{_e(T['chip_fonti'])}</div>"
        f"<div class='ss2-chip ss2-chip-b ss2-galleggia2'>{_icona('memoria', 'ss2-oro')}{_e(T['chip_memoria'])}</div>"
        f"</div></section>"
    )
    fiducia_icone = ("", "lucchetto", "salva", "globo")
    fiducia = "".join(
        (f"<span><b class='ss2-cinquanta'>50</b>{_e(voce.replace('50', '', 1).strip())}</span>" if n == 0 and voce.startswith("50")
         else f"<span>{_icona(fiducia_icone[n] or 'spunta', 'ss2-oro')}{_e(voce)}</span>")
        for n, voce in enumerate(d["fiducia"])
    )
    striscia = f"<section class='ss2-striscia'><div class='ss2-wrap ss2-striscia-griglia'>{fiducia}</div></section>"

    # ---------- Percorso: slide ----------
    slide_titoli = d["slide"]
    passi = "".join(
        f"<button type='button' class='ss2-passo{' attivo' if n == 0 else ''}' data-slide='{n}' aria-current='{'step' if n == 0 else 'false'}'>"
        f"<span class='ss2-passo-num'>{n + 1:02d}</span><span class='ss2-passo-testo'><b>{_e(titolo)}</b>"
        f"<small>{_e(T['step_subs'][n])}</small></span></button>"
        for n, (titolo, _testo) in enumerate(slide_titoli)
    )
    chip_campi = "".join(f"<span class='ss2-tag'>{_e(c)}</span>" for c in T["campi"])
    fonti = "".join(
        f"<div class='ss2-riga-box'><span>{_e(nome)}</span><b class='{'ss2-verde' if n < 2 else 'ss2-oro-testo'}'>"
        f"{_e(T['alta'] if n < 2 else T['media'])}</b></div>"
        for n, nome in enumerate(T["fonti"])
    )
    indice_slide = "".join(f"<span>{_e(v)}</span>" for v in voci_indice)
    modi = "".join(f"<span class='{'attivo' if n == 0 else ''}'>{_e(m)}</span>" for n, m in enumerate(T["modi"]))
    controlli = "".join(
        f"<div class='ss2-riga-box'><span>{_e(c)}</span><b class='{'ss2-oro-testo' if n == 1 else 'ss2-verde'}'>"
        f"{_e(T['da_rivedere'] if n == 1 else T['superato'])}</b></div>"
        for n, c in enumerate(T["controlli"])
    )
    export = "".join(
        f"<div class='ss2-file'>{_icona(ico, colore, '1.8')}<b>{nome}</b><span>{_e(sotto)}</span></div>"
        for ico, colore, nome, sotto in (("file", "ss2-blu", "Word", T["export"][0]), ("file", "ss2-oro", "PDF", T["export"][1]),
                                         ("kdp", "ss2-verde", "Amazon KDP", T["export"][2]))
    )
    visuali = (
        f"<div class='ss2-chat'><div class='ss2-bolla ss2-bolla-ai'>{_e(T['chat'][0])}</div>"
        f"<div class='ss2-bolla ss2-bolla-tu'>{_e(T['chat'][1])}</div><div class='ss2-bolla ss2-bolla-ai'>{_e(T['chat'][2])}</div></div>"
        f"<div class='ss2-tags'>{chip_campi}</div>",
        f"<div class='ss2-due'><div class='ss2-colonna'>{fonti}</div><div class='ss2-carta'><span class='ss2-occhiello'>{_e(B['index'])}</span>{indice_slide}</div></div>"
        f"<p class='ss2-nota'>{_e(T['s2_nota'])}</p>",
        f"<div class='ss2-modi'>{modi}</div><div class='ss2-carta ss2-carta-scrive'><span class='ss2-libro-titolo'>{_e(B['chapter_title'])}</span>"
        f"<i class='ss2-riga ss2-w1'></i><i class='ss2-riga ss2-w2'></i><i class='ss2-riga ss2-w3'></i></div>"
        f"<p class='ss2-nota'>{_e(T['s3_nota'])}</p>",
        f"<div class='ss2-colonna ss2-stretta'>{controlli}</div><p class='ss2-nota'>{_e(T['s4_nota'])}</p>",
        f"<div class='ss2-files'>{export}</div>"
        f"<a class='ss2-btn-oro ss2-nota-btn' href='{_e(link_reg)}' target='_self' data-azione='registrati'>{_e(T['inizia_libro'])}</a>",
    )
    slides = "".join(
        f"<div class='ss2-slide{' attiva' if n == 0 else ''}' data-slide='{n}' aria-hidden='{'false' if n == 0 else 'true'}'>"
        f"<span class='ss2-etichetta-oro'>{n + 1:02d} · {_e(T['step_subs'][n])}</span>"
        f"<h3 class='ss2-h3'>{_e(T['slide_h3'][n])}</h3>{visuali[n]}</div>"
        for n in range(5)
    )
    percorso = (
        f"<section id='ss-percorso' class='ss2-wrap ss2-sezione ss2-percorso' data-percorso>"
        f"<div class='ss2-testa ss2-testa-riga'><div class='ss2-testa-testo'><span class='ss2-etichetta'>{_e(N[0])}</span>"
        f"<h2 class='ss2-h2'>{_h(T['percorso_titolo'])}</h2></div>"
        f"<div class='ss2-comandi'>"
        f"<button type='button' class='ss2-tondo' data-comando='prec' aria-label='{_e(d['prec'])}'>{_icona('sx', larghezza='2.2')}</button>"
        f"<button type='button' class='ss2-tondo ss2-play' data-comando='play' aria-label='{_e(T['pausa'])}' data-pausa='{_e(T['pausa'])}' data-riproduci='{_e(T['riproduci'])}'>"
        f"{_icona('pausa', 'ss2-ico-pausa')}{_icona('play', 'ss2-ico-play')}</button>"
        f"<button type='button' class='ss2-tondo ss2-tondo-oro' data-comando='succ' aria-label='{_e(d['succ'])}'>{_icona('dx', larghezza='2.4')}</button>"
        f"</div></div>"
        f"<div class='ss2-percorso-griglia'><div class='ss2-passi'>{passi}<div class='ss2-avanzamento'><i></i></div></div>"
        f"<div class='ss2-palco'><div class='ss2-alone-blu' aria-hidden='true'></div>{slides}</div></div></section>"
    )

    # ---------- Funzioni ----------
    funz_icone = (("lente", "ss2-blu"), ("elenco", "ss2-oro"), ("libro", "ss2-verde"), ("globo", "ss2-blu"), ("salva", "ss2-oro"), ("aiuto", "ss2-verde"))
    funzioni = "".join(
        f"<div class='ss2-card ss2-solleva'><span class='ss2-icona-box {colore}'>{_icona(ico, '', '1.8')}</span>"
        f"<b>{_e(titolo)}</b><span>{_e(testo)}</span></div>"
        for (ico, colore), (titolo, testo) in zip(funz_icone, T["funz"])
    )
    sezione_funzioni = (
        f"<section id='ss-funzioni' class='ss2-wrap ss2-sezione'><div class='ss2-testa'><span class='ss2-etichetta'>{_e(N[1])}</span>"
        f"<h2 class='ss2-h2'>{_h(T['funz_titolo'])}</h2></div><div class='ss2-griglia-3'>{funzioni}</div></section>"
    )

    # ---------- Vantaggi ----------
    vantaggi = d["vantaggi"]
    tabs = "".join(
        f"<button type='button' role='tab' class='ss2-pill{' attivo' if n == 0 else ''}' data-vantaggio='{n}' aria-selected='{'true' if n == 0 else 'false'}'>{_e(titolo)}</button>"
        for n, (_i, titolo, _t) in enumerate(vantaggi)
    )
    pannelli = "".join(
        f"<div role='tabpanel' class='ss2-pannello{' attivo' if n == 0 else ''}' data-vantaggio='{n}'>"
        f"<div class='ss2-pannello-testo'><span class='ss2-numero-grande'>{n + 1:02d}</span><h3 class='ss2-h3 ss2-h3-grande'>{_e(titolo)}</h3><p>{_e(testo)}</p></div>"
        f"<ul class='ss2-punti'>" + "".join(f"<li>{_icona('spunta', 'ss2-verde', '2.4')}{_e(p)}</li>" for p in T["vant_punti"][n]) + "</ul></div>"
        for n, (_i, titolo, testo) in enumerate(vantaggi)
    )
    sezione_vantaggi = (
        f"<section id='ss-vantaggi' class='ss2-wrap ss2-sezione'><div class='ss2-testa'><span class='ss2-etichetta'>{_e(N[2])}</span>"
        f"<h2 class='ss2-h2'>{_h(T['vant_titolo'])}</h2></div>"
        f"<div class='ss2-vantaggi'><div class='ss2-pills' role='tablist'>{tabs}</div><div class='ss2-pannelli'>{pannelli}</div></div></section>"
    )

    # ---------- Due cervelli + crediti ----------
    A = d["cervelli"]
    cervello_html = (
        f"<div class='ss2-cervello-pannello' data-mostra='eco'><div><b class='ss2-h3 ss2-h3-grande'>{_e(A['eco_nome'])}</b><span>{_e(A['eco_testo'])}</span></div>"
        f"<div class='ss2-cervello-numero'><span>1 : 3</span><small>{_e(A['eco_costo'])}</small></div></div>"
        f"<div class='ss2-cervello-pannello' data-mostra='pro'><div><b class='ss2-h3 ss2-h3-grande'>{_e(A['pro_nome'])}</b><span>{_e(A['pro_testo'])}</span></div>"
        f"<div class='ss2-cervello-numero'><span>1 : 1</span><small>{_e(A['pro_costo'])}</small></div></div>"
    )
    scelta = (
        f"<div class='ss2-scelta' role='radiogroup' aria-label='{_e(A['titolo'])}'>"
        f"<button type='button' role='radio' class='ss2-scelta-btn' data-cervello='eco' aria-checked='true'>{_e(A['eco_nome'])}</button>"
        f"<button type='button' role='radio' class='ss2-scelta-btn' data-cervello='pro' aria-checked='false'>{_e(A['pro_nome'])}</button></div>"
    )
    pacchetti = ""
    for n, p in enumerate(d["pacchetti"]):
        def libri(x: int) -> str:
            return T["libro_circa"] if x == 1 else T["libri_circa"]
        badge = f"<span class='ss2-badge'>{_e(d['consigliato'])}</span>" if p["consigliato"] else ""
        nota = p.get("nota", "")
        if nota:
            stima_eco = stima_pro = _e(nota)
            stime = f"<span class='ss2-stima ss2-stima-nota'>{_e(nota)}</span>"
        else:
            stima_eco = f"≈ {p['eco']} {_e(libri(p['eco']))}"
            stima_pro = f"≈ {p['pro']} {_e(libri(p['pro']))}"
            stime = (
                f"<span class='ss2-stima' data-mostra='eco'><b>≈ {p['eco']}</b>{_e(libri(p['eco']))}</span>"
                f"<span class='ss2-stima' data-mostra='pro'><b>≈ {p['pro']}</b>{_e(libri(p['pro']))}</span>"
            )
        pacchetti += (
            f"<button type='button' class='ss2-pacchetto ss2-solleva{' scelto' if p['consigliato'] else ''}' aria-pressed='{'true' if p['consigliato'] else 'false'}'"
            f" data-nome='{_e(p['nome'])}' data-prezzo='{_e(p['prezzo'])}' data-crediti='{_e(p['crediti'])}'"
            f" data-eco='{stima_eco}' data-pro='{stima_pro}'>"
            f"<span class='ss2-pacchetto-testa'><b>{_e(p['nome'])}</b>{badge}</span>"
            f"<span class='ss2-prezzo'>{_e(p['prezzo'])}</span><span class='ss2-crediti'>{_e(p['crediti'])} {_e(T['crediti'])}</span>"
            f"<span class='ss2-separatore'></span>{stime}</button>"
        )
    scelto = next((p for p in d["pacchetti"] if p["consigliato"]), d["pacchetti"][0])
    riepilogo = (
        f"<div class='ss2-riepilogo'><span>{_e(T['hai_scelto'])} <b data-riepilogo='nome'>{_e(scelto['nome'])}</b> · "
        f"<span data-riepilogo='crediti'>{_e(scelto['crediti'])}</span> {_e(T['crediti'])} · "
        f"<span data-riepilogo='stima' data-mostra-testo>≈ {scelto['eco']} {_e(T['libri_circa'])}</span></span>"
        f"<a class='ss2-btn-oro' href='{_e(link_reg)}' target='_self' data-azione='registrati'>{_e(T['acquista'])} "
        f"<span data-riepilogo='nome'>{_e(scelto['nome'])}</span> · <span data-riepilogo='prezzo'>{_e(scelto['prezzo'])}</span></a></div>"
    )
    sezione_cervelli = (
        f"<section id='ss-cervelli' class='ss2-fascia'><div class='ss2-wrap ss2-sezione ss2-sezione-fascia'>"
        f"<div class='ss2-testa ss2-testa-riga'><div class='ss2-testa-testo'><span class='ss2-etichetta'>{_e(N[3])}</span>"
        f"<h2 class='ss2-h2'>{_h(T['cerv_titolo'])}</h2></div>{scelta}</div>"
        f"<div class='ss2-cervello'>{cervello_html}</div>"
        f"<p class='ss2-nota-piccola'>{_e(A['nota'])}</p>"
        f"<div id='ss-crediti' class='ss2-testa ss2-testa-crediti'><span class='ss2-etichetta'>{_e(N[4])}</span>"
        f"<h2 class='ss2-h2'>{_e(T['cred_titolo'])}</h2><p class='ss2-lead-piccolo'>{_e(T['cred_sub'])} "
        f"<b class='ss2-oro-testo' data-mostra='eco'>{_e(A['eco_nome'])}</b><b class='ss2-oro-testo' data-mostra='pro'>{_e(A['pro_nome'])}</b>.</p></div>"
        f"<div class='ss2-griglia-4{' ss2-griglia-5' if len(d['pacchetti']) > 4 else ''}'>{pacchetti}</div>{riepilogo}"
        f"<p class='ss2-nota-piccola'>{_e(d['nota_stime'])}</p></div></section>"
    )

    # ---------- FAQ ----------
    faq = "".join(
        f"<div class='ss2-faq{' aperta' if n == 0 else ''}'><button type='button' class='ss2-faq-domanda' aria-expanded='{'true' if n == 0 else 'false'}'>"
        f"<span>{_e(domanda)}</span><span class='ss2-faq-segno'>{_icona('piu', 'ss2-oro', '2.4')}</span></button>"
        f"<div class='ss2-faq-risposta'><p>{_e(risposta)}</p></div></div>"
        for n, (domanda, risposta) in enumerate(d["faq"])
    )
    sezione_faq = (
        f"<section id='ss-faq' class='ss2-wrap ss2-sezione ss2-stretta-sezione'><div class='ss2-testa'><span class='ss2-etichetta'>FAQ</span>"
        f"<h2 class='ss2-h2'>{_e(d['faq_titolo'])}</h2></div><div class='ss2-faq-elenco'>{faq}</div></section>"
    )

    # ---------- Guide e community ----------
    guide = ""
    for etichetta, sotto, link, nome_file in d["guide"]:
        if link:
            guide += (f"<a class='ss2-card ss2-solleva ss2-card-link ss-guida-pdf' href='{_e(link)}' download='{_e(nome_file)}' target='_blank' rel='noopener'>"
                      f"{_icona('scarica', 'ss2-oro', '1.8')}<b>{_e(etichetta)}</b><span>{_e(sotto)}</span></a>")
    guide += (f"<a class='ss2-card ss2-solleva ss2-card-link' href='https://selfpublishingitalia.site/' target='_blank' rel='noopener noreferrer'>"
              f"{_icona('persone', 'ss2-blu', '1.8')}<b>{_e(d['community'])}</b><span>{_e(T['community_sub'])}</span></a>")
    sezione_guide = (
        f"<section id='ss-guide' class='ss2-wrap ss2-sezione'><div class='ss2-testa'><span class='ss2-etichetta'>{_e(N[6])}</span>"
        f"<h2 class='ss2-h2'>{_e(d['guide_titolo'])}</h2><p class='ss2-lead-piccolo'>{_e(d['guide_testo'])}</p></div>"
        f"<div class='ss2-griglia-3'>{guide}</div></section>"
    )

    # ---------- Invito finale e piè di pagina ----------
    finale = (
        f"<section class='ss2-wrap'><div class='ss2-finale'><h2>{_h(d['finale_titolo'])}</h2><p>{_e(d['finale_testo'])}</p>"
        f"<a class='ss2-btn-scuro' href='{_e(link_reg)}' target='_self' data-azione='registrati'>{_e(d['inizia'])}</a></div></section>"
    )
    piede = (
        f"<footer class='ss2-piede'><div class='ss2-wrap ss2-piede-riga'><span class='ss2-piede-nome'>Scrittore Site</span>"
        f"<a href='https://selfpublishingitalia.site/' target='_blank' rel='noopener noreferrer'>{_e(d['community'])}</a>"
        f"<a href='https://www.instagram.com/scrittore.site/' target='_blank' rel='noopener noreferrer'>{_e(N[7])}</a>"
        f"<a href='https://liberamente.site/' target='_blank' rel='noopener noreferrer'>{_e(d['store'])}</a>"
        f"<span class='ss2-piede-dx'>{_e(T['stripe'])} · {_e(d['versione'])}</span></div></footer>"
    )

    corpo = header + hero + striscia + percorso + sezione_funzioni + sezione_vantaggi + sezione_cervelli + sezione_faq + sezione_guide + finale + piede
    return f"<div class='ss2' dir='{direzione}' lang='{d['sigla'].lower()}'><div class='ss2-progresso' aria-hidden='true'></div>{corpo}</div>"
