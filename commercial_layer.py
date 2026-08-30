"""Accesso, crediti e pagamenti per la versione commerciale di Scrittore Site."""
from __future__ import annotations

import os
import uuid
from typing import Any

import requests
import streamlit as st


COMMERCIAL_VERSION = "commercial-01"
# Alias mantenuto per compatibilità con l'app commerciale già predisposta.
COMMERCIAL_TEST_VERSION = COMMERCIAL_VERSION
DEMO_INITIAL_CREDITS = 50
AI_REQUEST_CREDITS = 1
# Elenco configurato esclusivamente nei Secrets di Streamlit, per esempio:
# ADMIN_EMAILS = "nome@dominio.it, secondo@dominio.it"
# Non inserire indirizzi amministratore direttamente nel codice pubblicato.

PACKAGES = {
    "prova_7": {
        "name": "Pacchetto Prova — 7 crediti",
        "credits": 7,
        "amount_cents": 100,
        "currency": "eur",
    },
    "base_100": {
        "name": "Pacchetto Base — 100 crediti",
        "credits": 100,
        "amount_cents": 1000,
        "currency": "eur",
    },
    "creator_260": {
        "name": "Pacchetto Creator — 260 crediti",
        "credits": 260,
        "amount_cents": 2500,
        "currency": "eur",
    },
    "studio_530": {
        "name": "Pacchetto Studio — 530 crediti",
        "credits": 530,
        "amount_cents": 5000,
        "currency": "eur",
    },
    "professionale_1050": {
        "name": "Pacchetto Professionale — 1.050 crediti",
        "credits": 1050,
        "amount_cents": 10000,
        "currency": "eur",
    },
}


class CommercialCreditError(RuntimeError):
    """L'operazione IA non può iniziare perché il saldo è insufficiente."""


def _secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
    except Exception:
        value = default
    return str(value or os.getenv(name, default)).strip()


def _mode() -> str:
    return _secret("COMMERCIAL_MODE", "live").lower()


def _supabase_ready() -> bool:
    return bool(_secret("SUPABASE_URL") and _secret("SUPABASE_ANON_KEY") and _secret("SUPABASE_SERVICE_ROLE_KEY"))


def _stripe_ready() -> bool:
    return bool(_secret("STRIPE_SECRET_KEY") and _secret("APP_BASE_URL"))


def _payments_enabled() -> bool:
    return _secret("PAYMENTS_ENABLED", "false").lower() == "true"


def _admin_emails() -> set[str]:
    """Restituisce gli indirizzi amministratore definiti nei Secrets dell'app."""
    return {
        email.strip().lower()
        for email in _secret("ADMIN_EMAILS").replace(";", ",").split(",")
        if email.strip()
    }


def _is_admin(user: dict[str, Any] | None = None) -> bool:
    """Un amministratore è riconosciuto solo da un indirizzo presente nei Secrets."""
    current_user = user or st.session_state.get("commercial_user_context") or st.session_state.get("commercial_user") or {}
    return str(current_user.get("email", "")).strip().lower() in _admin_emails()


def _supabase_headers() -> dict[str, str]:
    key = _secret("SUPABASE_SERVICE_ROLE_KEY")
    return {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _supabase(method: str, path: str, *, payload: Any | None = None, params: dict | None = None) -> Any:
    url = f"{_secret('SUPABASE_URL').rstrip('/')}/{path.lstrip('/')}"
    response = requests.request(method, url, headers=_supabase_headers(), json=payload, params=params, timeout=20)
    if not response.ok:
        raise RuntimeError(f"Archivio commerciale non disponibile ({response.status_code}).")
    if not response.content:
        return None
    return response.json()


def _init_demo_account() -> dict[str, Any]:
    if "commercial_demo_user" not in st.session_state:
        st.session_state["commercial_demo_user"] = {
            "id": f"demo-{uuid.uuid4().hex}",
            "email": "demo@scrittore-site.local",
            "display_name": "Utente Demo",
        }
        st.session_state["commercial_demo_credits"] = DEMO_INITIAL_CREDITS
        st.session_state["commercial_demo_ledger"] = []
    return st.session_state["commercial_demo_user"]


def _supabase_login(email: str, password: str) -> dict[str, Any]:
    url = f"{_secret('SUPABASE_URL').rstrip('/')}/auth/v1/token"
    response = requests.post(
        url,
        headers={"apikey": _secret("SUPABASE_ANON_KEY"), "Content-Type": "application/json"},
        params={"grant_type": "password"},
        json={"email": email, "password": password},
        timeout=20,
    )
    if not response.ok:
        raise RuntimeError("Accesso non riuscito. Controlla email e password.")
    data = response.json()
    return {"access_token": data["access_token"], "id": data["user"]["id"], "email": data["user"].get("email", email)}


def _supabase_signup(email: str, password: str) -> None:
    url = f"{_secret('SUPABASE_URL').rstrip('/')}/auth/v1/signup"
    response = requests.post(
        url,
        headers={"apikey": _secret("SUPABASE_ANON_KEY"), "Content-Type": "application/json"},
        json={"email": email, "password": password},
        timeout=20,
    )
    if not response.ok:
        raise RuntimeError("Registrazione non riuscita. Usa una password più sicura o riprova.")


def _supabase_recover_password(email: str) -> None:
    """Invia il link di recupero password tramite il sistema sicuro di Supabase."""
    url = f"{_secret('SUPABASE_URL').rstrip('/')}/auth/v1/recover"
    payload = {"email": email.strip()}
    redirect_url = _secret("APP_BASE_URL")
    if redirect_url:
        payload["redirect_to"] = redirect_url.rstrip("/")
    response = requests.post(
        url,
        headers={"apikey": _secret("SUPABASE_ANON_KEY"), "Content-Type": "application/json"},
        json=payload,
        timeout=20,
    )
    if not response.ok:
        raise RuntimeError("Impossibile inviare il link di recupero. Riprova tra poco.")


def _landing_page() -> None:
    """Pagina di ingresso pubblica: compare prima dell'accesso."""
    st.markdown(
        """
        <style>
          .stApp, [data-testid="stAppViewContainer"] {background:linear-gradient(145deg,#f5fbff 0%,#eaf6ff 52%,#f4faff 100%) !important;
            color:#172b4d}
          .ss-hero {max-width:1080px; margin:1.3rem auto .65rem; padding:2.5rem 2rem;
            border-radius:28px; background:radial-gradient(circle at 12% 15%,#fbcfe8 0%,transparent 26%),
            radial-gradient(circle at 88% 88%,#bae6fd 0%,transparent 32%),linear-gradient(125deg,#fff 0%,#e0f2fe 100%);
            color:#12315c; text-align:center; border:1px solid #bae6fd; box-shadow:0 16px 38px rgba(14,116,144,.16)}
          .ss-hero h1 {font-size:clamp(4.3rem,9.2vw,7.2rem); margin:.18rem -.45rem .7rem; color:#0c4a6e; line-height:.94; letter-spacing:-.07em}
          .ss-hero p {font-size:1.2rem; max-width:700px; margin:0 auto; color:#173a63; font-weight:650}
          .ss-kicker {letter-spacing:.15em; text-transform:uppercase; font-weight:850; font-size:1rem; color:#0e7490}
          .ss-bonus {max-width:850px; margin:1rem auto 1.15rem; padding:.95rem 1.3rem; border-radius:999px;
            text-align:center; font-size:1.35rem; font-weight:850; color:#0c4a6e; background:#cffafe;
            border:2px solid #67e8f9; box-shadow:0 5px 16px rgba(8,145,178,.14)}
          .ss-section {max-width:1080px; margin:1.35rem auto .45rem; text-align:center}
          .ss-section h2 {font-size:2rem; margin-bottom:.16rem; color:#25104b}
          .ss-card {background:linear-gradient(145deg,#fff 0%,#faf7ff 100%); border:1px solid #e9d5ff;
            border-radius:16px; padding:1rem .9rem; min-height:112px; box-shadow:0 5px 14px rgba(88,28,135,.08)}
          .ss-card h3 {margin:0 0 .34rem; color:#6d28d9; font-size:1rem}
          .ss-card p {margin:0; font-size:.9rem; line-height:1.35}
          .ss-price {font-size:1.35rem; font-weight:800; color:#be185d; margin:.15rem 0}
          .ss-muted {color:#63506e; text-align:center; margin:.1rem auto .75rem; max-width:720px; font-size:.94rem}
          .ss-step {background:#fff7ed; border:1px solid #fed7aa; border-radius:14px; padding:1.15rem 1.05rem;
            min-height:150px; text-align:left; font-size:1rem; line-height:1.48}
          .ss-step strong {display:block; color:#c2410c; margin-bottom:.3rem; font-size:1.18rem}
          .ss-feature {background:#fff; border:1px solid #ddd6fe; border-radius:15px; padding:1rem;
            min-height:120px; box-shadow:0 4px 12px rgba(76,29,149,.07)}
          .ss-feature strong {display:block; color:#5b21b6; font-size:1rem; margin-bottom:.3rem}
          .ss-feature p {margin:0; color:#41324f; font-size:.9rem; line-height:1.38}
          .ss-proof {max-width:980px; margin:1.35rem auto; padding:1.15rem; border-radius:20px;
            background:linear-gradient(135deg,#111827,#243b6b); color:#e0f2fe;
            box-shadow:0 14px 30px rgba(15,23,42,.22)}
          .ss-proof-top {display:flex; gap:.45rem; align-items:center; padding:0 0 .8rem;
            border-bottom:1px solid rgba(255,255,255,.16); font-size:.9rem; color:#bae6fd}
          .ss-dot {width:10px; height:10px; border-radius:50%; background:#fb7185; display:inline-block}
          .ss-dot:nth-child(2) {background:#fbbf24}.ss-dot:nth-child(3) {background:#4ade80}
          .ss-proof-label {margin-left:auto; font-size:.72rem; border:1px solid rgba(125,211,252,.45); padding:.2rem .48rem; border-radius:99px}
          .ss-proof-grid {display:grid; grid-template-columns:29% 1fr; gap:1rem; padding-top:1rem; text-align:left}
          .ss-proof-index,.ss-proof-page {border-radius:13px; padding:1rem; background:rgba(255,255,255,.08)}
          .ss-proof-index b {display:block; color:#f9a8d4; margin-bottom:.55rem}
          .ss-proof-index span {display:block; padding:.32rem 0; border-bottom:1px solid rgba(255,255,255,.09); font-size:.84rem}
          .ss-proof-index .active {margin:.35rem -.35rem; padding:.42rem .35rem; background:rgba(45,212,191,.18); border-left:3px solid #5eead4; border-radius:5px; color:#fff}
          .ss-proof-toolbar {display:flex; gap:.42rem; align-items:center; margin-bottom:.8rem; flex-wrap:wrap}
          .ss-proof-pill {font-size:.72rem; padding:.28rem .55rem; border-radius:99px; background:rgba(125,211,252,.16); color:#bae6fd}
          .ss-proof-action {margin-left:auto; background:#db2777; color:#fff; border-radius:7px; padding:.38rem .62rem; font-size:.74rem; font-weight:800}
          .ss-proof-page small {color:#7dd3fc; font-weight:800}.ss-proof-page h3 {color:#fff; margin:.38rem 0 .5rem}
          .ss-proof-page p {margin:0; color:#dbeafe; font-size:.9rem; line-height:1.55}
          .ss-proof-lines {margin:.85rem 0}.ss-proof-lines i {display:block; height:7px; margin:.42rem 0; border-radius:9px; background:linear-gradient(90deg,rgba(255,255,255,.22),rgba(255,255,255,.05))}
          .ss-proof-lines i:nth-child(2) {width:91%}.ss-proof-lines i:nth-child(3) {width:77%}.ss-proof-lines i:nth-child(4) {width:84%}
          .ss-proof-progress {display:flex; align-items:center; gap:.65rem; color:#bbf7d0; font-size:.78rem; font-weight:700}
          .ss-proof-progress div {height:8px; border-radius:99px; background:rgba(255,255,255,.18); flex:1; overflow:hidden}.ss-proof-progress div span {display:block; width:64%; height:100%; background:linear-gradient(90deg,#2dd4bf,#60a5fa); border-radius:99px}
          .ss-credit-note {max-width:850px; margin:.7rem auto 1.3rem; padding:1rem 1.15rem; border-radius:14px;
            text-align:center; background:#ecfeff; color:#155e75; border:1px solid #a5f3fc; font-weight:650}
          .ss-trust {max-width:920px; margin:1.15rem auto 1.5rem; text-align:center; padding:1rem;
            border-radius:15px; background:#f0fdf4; color:#166534; border:1px solid #bbf7d0; font-weight:700}
          @media (max-width:760px) {.ss-hero h1 {font-size:4rem}.ss-proof-grid {grid-template-columns:1fr}.ss-proof-action {margin-left:0}}
          [data-testid="stMain"] .stButton button {min-height:3.45rem; border-radius:14px; font-size:1.12rem;
            font-weight:800; border:2px solid #6d28d9; background:linear-gradient(100deg,#6d28d9,#db2777) !important;
            border-color:#6d28d9 !important; color:#fff !important}
          /* Home pubblica: nasconde i comandi tecnici di Streamlit. */
          [data-testid="stHeader"] {background:transparent !important}
          [data-testid="stToolbar"], [data-testid="stToolbarActions"], [data-testid="stStatusWidget"],
          .stAppDeployButton, #MainMenu, footer, button[title="Manage app"], a[title="Manage app"],
          button[aria-label="Manage app"], a[aria-label="Manage app"] {display:none !important}
          [data-testid="stExpander"] {max-width:860px; margin:.5rem auto; background:#fff !important;
            border:1px solid #ddd6fe !important; border-radius:12px !important; overflow:hidden}
          [data-testid="stExpander"] details, [data-testid="stExpander"] summary,
          [data-testid="stExpander"] [data-testid="stExpanderDetails"] {background:#fff !important; color:#25104b !important}
          [data-testid="stExpander"] summary:hover {background:#faf5ff !important}
        </style>
        <div class="ss-hero">
          <div class="ss-kicker">AI di Antonino presenta</div>
          <h1>Scrittore Site</h1>
          <p>Crea libri strutturati con l'AI, mantieni il controllo e scaricali in Word o PDF.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='ss-bonus'>🎁 Registrati e avrai 50 crediti gratuiti per provarlo. Nessuna carta richiesta.</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        if st.button("🎁 Crea il tuo account gratuito", type="primary", use_container_width=True, key="landing_signup"):
            st.session_state["commercial_show_auth"] = True
            st.session_state["commercial_auth_hint"] = "signup"
            st.rerun()
    with right:
        if st.button("Accedi al tuo spazio", use_container_width=True, key="landing_login"):
            st.session_state["commercial_show_auth"] = True
            st.session_state["commercial_auth_hint"] = "login"
            st.rerun()

    st.markdown(
        """<div class='ss-proof'>
          <div class='ss-proof-top'><span class='ss-dot'></span><span class='ss-dot'></span><span class='ss-dot'></span>&nbsp; Area di scrittura <span class='ss-proof-label'>Esempio illustrativo</span></div>
          <div class='ss-proof-grid'>
            <div class='ss-proof-index'><b>IL TUO PROGETTO</b><span>Parte I · Fondamenti</span><span>Capitolo 1 · Le basi</span><span>1.1 Concetti chiave</span><span class='active'>1.2 Esempio pratico</span><span>Parte II · Applicazione</span></div>
            <div class='ss-proof-page'><div class='ss-proof-toolbar'><span class='ss-proof-pill'>Scrittura e Quiz</span><span class='ss-proof-pill'>Italiano</span><span class='ss-proof-action'>Rigenera con AI</span></div><small>CAPITOLO 1 · SEZIONE 1.2</small><h3>Dal progetto al manoscritto</h3><p>Genera una sezione, correggila con le tue indicazioni, aggiungi esempi e controlla la coerenza dell'intero libro prima di esportarlo.</p><div class='ss-proof-lines'><i></i><i></i><i></i><i></i></div><div class='ss-proof-progress'>Stesura del libro <div><span></span></div> 64%</div></div>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='ss-section'><h2>Cosa puoi creare</h2><p class='ss-muted'>Un unico strumento, adattato al tuo progetto editoriale.</p></div>", unsafe_allow_html=True)
    creator_cards = st.columns(3)
    for column, title, text in (
        (creator_cards[0], "Manuali e guide", "Manuali pratici, tecnici e divulgativi con procedure, esempi, checklist e approfondimenti."),
        (creator_cards[1], "Ricettari e contenuti pratici", "Ricette, esempi e materiali operativi organizzati in modo leggibile e coerente."),
        (creator_cards[2], "Narrativa, quiz e test prep", "Romanzi, libri di preparazione agli esami, quiz commentati e progetti multilingue."),
    ):
        with column:
            st.markdown(f"<div class='ss-card'><h3>{title}</h3><p>{text}</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='ss-section'><h2>Come funziona Scrittore Site</h2><p class='ss-muted'>Segui il percorso e mantieni il controllo su ogni scelta del tuo libro.</p></div>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    for column, title, text in (
        (s1, "1. Definisci il progetto", "Inserisci titolo, lingua, pubblico, genere, obiettivo e argomento. Puoi aggiungere istruzioni e approfondimenti importanti."),
        (s2, "2. Crea e migliora", "Genera l’indice, valuta la struttura e sviluppa le singole parti o l’intero libro. Puoi fermarti, controllare e rigenerare ciò che desideri."),
        (s3, "3. Controlla ed esporta", "Usa anteprima, controllo di coerenza e formattazione. Quando il risultato ti soddisfa, esporta il manoscritto in Word o PDF."),
    ):
        with column:
            st.markdown(f"<div class='ss-step'><strong>{title}</strong>{text}</div>", unsafe_allow_html=True)

    st.markdown("<div class='ss-section'><h2>Caratteristiche</h2><p class='ss-muted'>Strumenti pensati per accompagnarti dalla prima idea al manoscritto esportabile.</p></div>", unsafe_allow_html=True)
    feature_rows = [
        (
            ("Brief editoriale", "Titolo, autore, genere, stile, punto di vista, obiettivo, argomento, risultato e approfondimenti in un unico spazio."),
            ("Multilingue", "Crea progetti in nove lingue e usa un’interfaccia adattata alla lingua scelta."),
            ("Indice professionale", "Genera l’indice, assegna un voto alla struttura e rigeneralo seguendo i suggerimenti ricevuti."),
            ("Scrittura flessibile", "Scrivi una sezione, tutti i sottocapitoli di un capitolo o l’intero libro; puoi mettere in pausa il lavoro."),
        ),
        (
            ("Miglioramento mirato", "Rigenera o rielabora soltanto la parte da migliorare, con istruzioni precise e senza riscrivere tutto."),
            ("Quiz, esempi e ricette", "Aggiungi contenuti pratici quando sono utili al genere e al progetto editoriale."),
            ("Fonti e immagini", "Carica PDF o Word come riferimento e integra immagini scelte da te nel manoscritto."),
            ("Controllo ed esportazione", "Usa anteprima, formattazione, controllo di coerenza e download in formato Word o PDF."),
        ),
    ]
    for row in feature_rows:
        columns = st.columns(4)
        for column, (title, text) in zip(columns, row):
            with column:
                st.markdown(f"<div class='ss-feature'><strong>{title}</strong><p>{text}</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='ss-section'><h2>Crediti chiari, controllo totale</h2></div>", unsafe_allow_html=True)
    st.markdown("<div class='ss-credit-note'>Usi i crediti solo quando chiedi all'AI di generare o migliorare contenuti. Puoi leggere, modificare, controllare ed esportare il tuo lavoro quando vuoi.</div>", unsafe_allow_html=True)
    st.markdown("<div class='ss-trust'>Il libro resta sotto il tuo controllo: puoi fermare la scrittura, rivedere ogni sezione e decidere tu cosa esportare o pubblicare.</div>", unsafe_allow_html=True)

    st.markdown("<div class='ss-section'><h2>Pacchetti crediti</h2><p class='ss-muted'>Scegli solo ciò che ti serve.</p></div>", unsafe_allow_html=True)
    price_columns = st.columns(len(PACKAGES))
    for column, package in zip(price_columns, PACKAGES.values()):
        price = f"€ {package['amount_cents'] / 100:.2f}".replace(".", ",")
        with column:
            st.markdown(
                f"<div class='ss-card'><h3>{package['name'].replace('Pacchetto ', '')}</h3>"
                f"<div class='ss-price'>{price}</div><p>{package['credits']} crediti</p></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='ss-section'><h2>Domande frequenti</h2></div>", unsafe_allow_html=True)
    with st.expander("Posso iniziare senza esperienza editoriale?"):
        st.write("Sì. Scrittore Site guida la preparazione del brief e mantiene ordinati i passaggi di lavoro.")
    with st.expander("I crediti servono per cosa?"):
        st.write("I crediti permettono di usare le funzioni IA di progettazione, scrittura, revisione e miglioramento del libro.")
    with st.expander("Devo scrivere tutto il libro in una sola volta?"):
        st.write("No. Puoi generare e controllare una sezione alla volta oppure usare la scrittura completa. In ogni momento puoi fermarti e rivedere ciò che è stato prodotto.")
    with st.expander("Posso modificare indice e contenuti generati?"):
        st.write("Sì. L’indice e ogni sezione restano modificabili. Puoi migliorare una sola parte con le tue istruzioni, senza dover ricominciare l’intero libro.")
    with st.expander("Come faccio a ottenere un libro coerente?"):
        st.write("Il software usa il brief, l’indice e le sezioni già scritte come riferimento. Il controllo di coerenza individua inoltre le parti che richiedono revisione.")
    with st.expander("Posso usare più lingue?"):
        st.write("Sì. Seleziona la lingua del progetto prima di creare l’indice: Scrittore Site adatta l’interfaccia e la generazione alla lingua scelta.")
    with st.expander("Posso caricare materiale di riferimento?"):
        st.write("Sì. Puoi caricare documenti PDF o Word come fonti esterne, così le istruzioni e le informazioni importanti restano disponibili durante il lavoro.")
    with st.expander("Il libro viene pubblicato automaticamente?"):
        st.write("No. Scrittore Site prepara il manoscritto e i file di esportazione; la scelta finale, le revisioni e la pubblicazione restano sempre sotto il tuo controllo.")
    with st.expander("Posso esportare il mio lavoro?"):
        st.write("Sì. Al termine puoi esportare il manoscritto in Word o PDF.")


def _account_gate() -> dict[str, Any]:
    if _mode() == "demo":
        return _init_demo_account()

    if not _supabase_ready():
        st.error("Configurazione account non disponibile. Riprova più tardi.")
        st.stop()

    current = st.session_state.get("commercial_user")
    if current:
        return current

    st.title("Accedi a Scrittore Site")
    st.caption("Ogni account mantiene separati crediti e sessione di lavoro.")
    if st.button("← Torna alla home", key="commercial_back_to_home"):
        st.session_state.pop("commercial_show_auth", None)
        st.session_state.pop("commercial_auth_hint", None)
        st.rerun()
    if st.session_state.get("commercial_auth_hint") == "signup":
        st.info("Seleziona la scheda “Crea account” per registrarti.")
    access_tab, signup_tab = st.tabs(["Accedi", "Crea account"])
    with access_tab:
        email = st.text_input("Email", key="commercial_login_email")
        password = st.text_input("Password", type="password", key="commercial_login_password")
        if st.button("Accedi", type="primary", key="commercial_login"):
            try:
                st.session_state["commercial_user"] = _supabase_login(email, password)
                st.rerun()
            except Exception as error:
                st.error(str(error))
        with st.expander("Password dimenticata?"):
            st.caption("Inserisci la tua e-mail: riceverai un link sicuro per impostare una nuova password.")
            recovery_email = st.text_input("E-mail per il recupero", key="commercial_recovery_email")
            if st.button("Invia il link di recupero", key="commercial_recovery_button"):
                if not recovery_email.strip():
                    st.warning("Inserisci prima il tuo indirizzo e-mail.")
                else:
                    try:
                        _supabase_recover_password(recovery_email)
                        st.success("Se l'indirizzo è registrato, riceverai a breve il link di recupero.")
                    except Exception as error:
                        st.error(str(error))
    with signup_tab:
        email = st.text_input("Email", key="commercial_signup_email")
        password = st.text_input("Password", type="password", key="commercial_signup_password")
        if st.button("Crea account", key="commercial_signup"):
            try:
                _supabase_signup(email, password)
                st.success("Account creato. Controlla l'email di conferma, poi accedi.")
            except Exception as error:
                st.error(str(error))
    st.stop()


def _balance(user_id: str) -> int:
    if _is_admin():
        # Valore tecnico di compatibilità: la UI visualizza ∞ e gli addebiti sono ignorati.
        return 1_000_000_000
    if _mode() == "demo" or not _supabase_ready():
        return int(st.session_state.get("commercial_demo_credits", DEMO_INITIAL_CREDITS))
    profile = _supabase("GET", "rest/v1/writer_profiles", params={"select": "credits", "id": f"eq.{user_id}", "limit": "1"})
    if not profile:
        raise RuntimeError("Profilo crediti non trovato. Esegui prima lo script commercial_setup.sql.")
    return int(profile[0]["credits"])


def _demo_ledger(reason: str, delta: int, reference: str) -> None:
    ledger = st.session_state.setdefault("commercial_demo_ledger", [])
    ledger.append({"when": __import__("datetime").datetime.now().isoformat(timespec="seconds"), "reason": reason, "delta": delta, "reference": reference})


def charge_credits(reason: str = "ai_request", amount: int = AI_REQUEST_CREDITS) -> str:
    """Addebito atomico prima della chiamata IA. Restituisce il riferimento rimborsabile."""
    user = st.session_state["commercial_user_context"]
    reference = uuid.uuid4().hex
    if _is_admin(user):
        # Nessun movimento e nessun consumo: l'amministratore dispone di crediti illimitati.
        return reference
    if _mode() == "demo" or not _supabase_ready():
        balance = _balance(user["id"])
        if balance < amount:
            raise CommercialCreditError("Crediti insufficienti. Ricarica il saldo prima di avviare un'altra elaborazione.")
        st.session_state["commercial_demo_credits"] = balance - amount
        _demo_ledger(reason, -amount, reference)
        return reference

    result = _supabase("POST", "rest/v1/rpc/spend_credits", payload={"p_user_id": user["id"], "p_credits": amount, "p_reason": reason, "p_reference": reference})
    if result is not True:
        raise CommercialCreditError("Crediti insufficienti. Ricarica il saldo prima di avviare un'altra elaborazione.")
    return reference


def refund_credits(reference: str, reason: str = "ai_request_failed", amount: int = AI_REQUEST_CREDITS) -> None:
    user = st.session_state.get("commercial_user_context")
    if not user:
        return
    if _is_admin(user):
        return
    if _mode() == "demo" or not _supabase_ready():
        st.session_state["commercial_demo_credits"] = _balance(user["id"]) + amount
        _demo_ledger(reason, amount, reference)
        return
    _supabase("POST", "rest/v1/rpc/refund_credits", payload={"p_user_id": user["id"], "p_credits": amount, "p_reason": reason, "p_reference": reference})


def _grant_demo_credits(package: dict[str, Any]) -> None:
    st.session_state["commercial_demo_credits"] = _balance(st.session_state["commercial_user_context"]["id"]) + int(package["credits"])
    _demo_ledger("demo_topup", int(package["credits"]), uuid.uuid4().hex)


def _create_checkout(package_key: str) -> str:
    package = PACKAGES[package_key]
    user = st.session_state["commercial_user_context"]
    base_url = _secret("APP_BASE_URL").rstrip("/")
    payload = {
        "mode": "payment",
        "success_url": f"{base_url}/?checkout=success&session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{base_url}/?checkout=cancelled",
        "customer_email": user["email"],
        "metadata[user_id]": user["id"],
        "metadata[package_key]": package_key,
        "metadata[credits]": str(package["credits"]),
        "line_items[0][quantity]": "1",
        "line_items[0][price_data][currency]": package["currency"],
        "line_items[0][price_data][unit_amount]": str(package["amount_cents"]),
        "line_items[0][price_data][product_data][name]": f"Scrittore Site — {package['name']}",
    }
    response = requests.post("https://api.stripe.com/v1/checkout/sessions", auth=(_secret("STRIPE_SECRET_KEY"), ""), data=payload, timeout=20)
    if not response.ok:
        raise RuntimeError("Impossibile creare il pagamento. Riprova o contatta l'assistenza.")
    return response.json()["url"]


def _process_checkout_return() -> None:
    """Mostra l'esito del ritorno da Stripe; il webhook accredita i crediti."""
    if _mode() == "demo" or not (
        _payments_enabled() and _stripe_ready() and _supabase_ready()
    ):
        return
    try:
        outcome = st.query_params.get("checkout", "")
        session_id = st.query_params.get("session_id", "")
    except Exception:
        return
    if outcome == "cancelled":
        st.info("Pagamento annullato: nessun credito è stato addebitato.")
        return
    if outcome != "success" or not session_id:
        return

    try:
        response = requests.get(
            f"https://api.stripe.com/v1/checkout/sessions/{session_id}",
            auth=(_secret("STRIPE_SECRET_KEY"), ""),
            timeout=20,
        )
        if not response.ok:
            raise RuntimeError("Sessione di pagamento non verificabile.")
        checkout = response.json()
        user = st.session_state["commercial_user_context"]
        metadata = checkout.get("metadata", {})
        package_key = metadata.get("package_key", "")
        package = PACKAGES.get(package_key)
        if checkout.get("payment_status") != "paid" or not package or metadata.get("user_id") != user["id"]:
            raise RuntimeError("Il pagamento non corrisponde all'account o al pacchetto selezionato.")
        granted = _supabase(
            "POST",
            "rest/v1/rpc/grant_checkout_credits",
            payload={
                "p_session_id": session_id,
                "p_user_id": user["id"],
                "p_package_key": package_key,
                "p_credits": int(package["credits"]),
            },
        )
        if granted is True:
            st.success(f"Pagamento verificato: aggiunti {package['credits']} crediti.")
        else:
            st.info("Questo pagamento era già stato registrato.")
        st.query_params.clear()
    except Exception as error:
        st.error(f"Pagamento ricevuto ma non ancora accreditato: {error}")


def _commerce_sidebar() -> None:
    user = st.session_state["commercial_user_context"]
    is_admin = _is_admin(user)
    with st.sidebar:
        st.divider()
        st.markdown("### 💳 Crediti")
        if _mode() == "demo":
            st.caption("Modalità dimostrativa: saldo valido solo per questa sessione.")
        else:
            st.caption(f"Account: {user['email']}")
        if is_admin:
            st.metric("Saldo disponibile", "∞ crediti")
            st.success("Account amministratore: crediti illimitati attivi.")
        else:
            st.metric("Saldo disponibile", f"{_balance(user['id'])} crediti")

        with st.expander("Ricarica crediti", expanded=False):
            if is_admin:
                st.caption("Non sono necessari acquisti: questo account ha crediti illimitati.")
            elif _mode() == "demo":
                for key, package in PACKAGES.items():
                    if st.button(f"Aggiungi {package['credits']} crediti demo", key=f"demo_topup_{key}"):
                        _grant_demo_credits(package)
                        st.success("Crediti demo aggiunti.")
                        st.rerun()
            elif not is_admin and not _payments_enabled():
                st.caption("I pacchetti saranno disponibili dopo l'attivazione sicura dei pagamenti.")
            elif not is_admin:
                for key, package in PACKAGES.items():
                    label = f"{package['name']} — € {package['amount_cents'] / 100:.2f}".replace(".", ",")
                    if st.button(f"Acquista {label}", key=f"stripe_topup_{key}"):
                        try:
                            st.link_button("Apri pagamento sicuro", _create_checkout(key), type="primary")
                        except Exception as error:
                            st.error(str(error))

        if _mode() == "demo":
            with st.expander("Movimenti", expanded=False):
                movements = st.session_state.get("commercial_demo_ledger", [])[-12:]
                st.write(movements or "Nessun movimento ancora.")

        if _mode() != "demo" and st.button("Esci", key="commercial_logout", use_container_width=True):
            st.session_state.pop("commercial_user", None)
            st.session_state.pop("commercial_user_context", None)
            st.session_state.pop("commercial_show_auth", None)
            st.rerun()


def bootstrap_commercial_app() -> None:
    """Mostra la home pubblica, quindi accesso e area editor riservata."""
    if (
        _mode() != "demo"
        and not st.session_state.get("commercial_user")
        and not st.session_state.get("commercial_show_auth")
    ):
        _landing_page()
        st.stop()
    st.session_state["commercial_user_context"] = _account_gate()
    _process_checkout_return()
    _commerce_sidebar()


# Compatibilità con il nome già importato dal file dell'app commerciale.
bootstrap_commercial_test = bootstrap_commercial_app
