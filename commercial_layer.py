"""Accesso, crediti e pagamenti per la versione commerciale di Scrittore Site."""
from __future__ import annotations

import os
import uuid
import json
from pathlib import Path
from typing import Any

import requests
import streamlit as st


COMMERCIAL_VERSION = "beta 3b"
# Alias mantenuto per compatibilità con l'app commerciale già predisposta.
COMMERCIAL_TEST_VERSION = COMMERCIAL_VERSION
DEMO_INITIAL_CREDITS = 50
# Griglia commerciale: un libro standard fino a 80 sezioni usa normalmente
# 95 crediti (80 sezioni, indice, voto, controllo finale e metadati).
AI_REQUEST_CREDITS = 1
STANDARD_BOOK_CREDITS = 95
# Elenco configurato esclusivamente nei Secrets di Streamlit, per esempio:
# ADMIN_EMAILS = "nome@dominio.it, secondo@dominio.it"
# Non inserire indirizzi amministratore direttamente nel codice pubblicato.

PACKAGES = {
    "prova_15": {
        "name": "Pacchetto Prova — 15 crediti",
        "credits": 15,
        "amount_cents": 100,
        "currency": "eur",
    },
    "base_150": {
        "name": "Pacchetto Base — 150 crediti",
        "credits": 150,
        "amount_cents": 1000,
        "currency": "eur",
    },
    "creator_375": {
        "name": "Pacchetto Creator — 375 crediti",
        "credits": 375,
        "amount_cents": 2500,
        "currency": "eur",
    },
    "studio_750": {
        "name": "Pacchetto Studio — 750 crediti",
        "credits": 750,
        "amount_cents": 5000,
        "currency": "eur",
    },
    "professionale_1500": {
        "name": "Pacchetto Professionale — 1.500 crediti",
        "credits": 1500,
        "amount_cents": 10000,
        "currency": "eur",
    },
}

# Compatibilità temporanea: permette di accreditare checkout già creati prima
# dell'aggiornamento, senza mostrarli né renderli acquistabili nell'app.
LEGACY_PACKAGES = {
    "prova_7": {"credits": 7},
    "base_100": {"credits": 100},
    "creator_260": {"credits": 260},
    "studio_530": {"credits": 530},
    "professionale_1050": {"credits": 1050},
}

# Stime commerciali: un libro standard usa normalmente 95 crediti
# (80 sezioni + 15 crediti per indice, voto e migliorie editoriali).
PACKAGE_BOOK_ESTIMATES = {
    "prova_15": "15 crediti per provare le funzioni principali",
    "base_150": "Fino a 1 libro standard + 55 crediti extra",
    "creator_375": "Fino a 3 libri standard + 90 crediti extra",
    "studio_750": "Fino a 7 libri standard + 85 crediti extra",
    "professionale_1500": "Fino a 15 libri standard + 75 crediti extra",
}
PACKAGE_ESTIMATE_NOTE = (
    "Stima indicativa: un libro standard considera 80 sezioni e circa 15 crediti "
    "per indice, voto e migliorie editoriali (95 crediti totali). "
    "Il consumo effettivo dipende da lunghezza, rigenerazioni, immagini, "
    "verifiche online e funzioni avanzate utilizzate."
)

# Testi della pagina pubblica nelle stesse nove lingue offerte dall'editor.
# Il cambio lingua qui modifica solo la home: non altera un eventuale libro dell'utente.
HOME_COPY = {
    "Italiano": {"presenta":"AI di Antonino presenta", "language":"Lingua", "headline":"Scrivi il tuo libro.<br>Con metodo, qualità e controllo.", "subtitle":"Dall’idea al manoscritto finito: struttura, scrivi ed esporta il tuo libro con l’AI, mantenendo sempre il controllo.", "bonus":"🎁 50 crediti gratuiti. Nessuna carta richiesta.", "start":"Inizia gratis con 50 crediti", "login":"Accedi", "b1":"Indice professionale", "b1t":"Struttura il tuo libro con capitoli e sottocapitoli chiari, completi e flessibili.", "b2":"Scrittura guidata", "b2t":"L’AI ti affianca capitolo dopo capitolo, mantenendo coerenza e qualità.", "b3":"Word e PDF", "b3t":"Esporta il tuo libro in Word e PDF, pronto per la revisione o la pubblicazione.", "create":"Cosa puoi creare", "create_sub":"Un unico strumento, adattato al tuo progetto editoriale.", "c1":"Guide e manuali", "c1t":"Spiega, insegna e condividi le tue competenze in modo chiaro e professionale.", "c2":"Ricettari", "c2t":"Raccogli e organizza le tue ricette con stile, indice e impaginazione ordinata.", "c3":"Romanzi, quiz e test prep", "c3t":"Crea storie coinvolgenti o materiali di studio efficaci e ben strutturati."},
    "English": {"presenta":"AI by Antonino presents", "language":"Language", "headline":"Write your book.<br>With method, quality and control.", "subtitle":"From idea to finished manuscript: plan, write and export your book with AI while always remaining in control.", "bonus":"🎁 50 free credits. No card required.", "start":"Start free with 50 credits", "login":"Log in", "b1":"Professional outline", "b1t":"Structure your book with clear, complete and flexible chapters and sections.", "b2":"Guided writing", "b2t":"AI supports you chapter by chapter to preserve consistency and quality.", "b3":"Word and PDF", "b3t":"Export your book in Word and PDF, ready for review or publishing.", "create":"What you can create", "create_sub":"One tool, adapted to your editorial project.", "c1":"Guides and manuals", "c1t":"Explain, teach and share your skills clearly and professionally.", "c2":"Cookbooks", "c2t":"Collect and organize your recipes with style, an outline and tidy layout.", "c3":"Novels, quizzes and test prep", "c3t":"Create engaging stories or effective, well-structured study material."},
    "Español": {"presenta":"La IA de Antonino presenta", "language":"Idioma", "headline":"Escribe tu libro.<br>Con método, calidad y control.", "subtitle":"De la idea al manuscrito final: estructura, escribe y exporta tu libro con IA manteniendo siempre el control.", "bonus":"🎁 50 créditos gratis. No se necesita tarjeta.", "start":"Empieza gratis con 50 créditos", "login":"Iniciar sesión", "b1":"Índice profesional", "b1t":"Estructura tu libro con capítulos y secciones claros, completos y flexibles.", "b2":"Escritura guiada", "b2t":"La IA te acompaña capítulo a capítulo para mantener coherencia y calidad.", "b3":"Word y PDF", "b3t":"Exporta tu libro en Word y PDF, listo para revisar o publicar.", "create":"Qué puedes crear", "create_sub":"Una sola herramienta adaptada a tu proyecto editorial.", "c1":"Guías y manuales", "c1t":"Explica, enseña y comparte tus conocimientos de forma clara y profesional.", "c2":"Recetarios", "c2t":"Reúne y organiza tus recetas con estilo, índice y maquetación ordenada.", "c3":"Novelas, cuestionarios y test prep", "c3t":"Crea historias atractivas o materiales de estudio eficaces y bien estructurados."},
    "Français": {"presenta":"L’IA d’Antonino présente", "language":"Langue", "headline":"Écrivez votre livre.<br>Avec méthode, qualité et contrôle.", "subtitle":"De l’idée au manuscrit final : structurez, écrivez et exportez votre livre avec l’IA, tout en gardant le contrôle.", "bonus":"🎁 50 crédits offerts. Aucune carte requise.", "start":"Commencer avec 50 crédits", "login":"Se connecter", "b1":"Plan professionnel", "b1t":"Structurez votre livre avec des chapitres et sections clairs, complets et flexibles.", "b2":"Rédaction guidée", "b2t":"L’IA vous accompagne chapitre après chapitre pour préserver cohérence et qualité.", "b3":"Word et PDF", "b3t":"Exportez votre livre en Word et PDF, prêt pour la relecture ou la publication.", "create":"Ce que vous pouvez créer", "create_sub":"Un seul outil adapté à votre projet éditorial.", "c1":"Guides et manuels", "c1t":"Expliquez, enseignez et partagez vos compétences clairement et professionnellement.", "c2":"Livres de recettes", "c2t":"Rassemblez et organisez vos recettes avec style, sommaire et mise en page soignée.", "c3":"Romans, quiz et test prep", "c3t":"Créez des histoires captivantes ou des supports d’étude efficaces et structurés."},
    "Deutsch": {"presenta":"Antoninos KI präsentiert", "language":"Sprache", "headline":"Schreiben Sie Ihr Buch.<br>Mit Methode, Qualität und Kontrolle.", "subtitle":"Von der Idee bis zum fertigen Manuskript: Planen, schreiben und exportieren Sie Ihr Buch mit KI und behalten Sie die Kontrolle.", "bonus":"🎁 50 kostenlose Credits. Keine Karte erforderlich.", "start":"Kostenlos mit 50 Credits starten", "login":"Anmelden", "b1":"Professionelle Gliederung", "b1t":"Strukturieren Sie Ihr Buch mit klaren, vollständigen und flexiblen Kapiteln und Abschnitten.", "b2":"Geführtes Schreiben", "b2t":"Die KI begleitet Sie Kapitel für Kapitel für Konsistenz und Qualität.", "b3":"Word und PDF", "b3t":"Exportieren Sie Ihr Buch als Word und PDF – bereit zur Überarbeitung oder Veröffentlichung.", "create":"Was Sie erstellen können", "create_sub":"Ein Werkzeug, angepasst an Ihr redaktionelles Projekt.", "c1":"Ratgeber und Handbücher", "c1t":"Erklären, lehren und teilen Sie Ihr Wissen klar und professionell.", "c2":"Kochbücher", "c2t":"Sammeln und organisieren Sie Rezepte mit Stil, Inhaltsverzeichnis und ordentlichem Layout.", "c3":"Romane, Quiz und Test Prep", "c3t":"Erstellen Sie fesselnde Geschichten oder wirksame, gut strukturierte Lernmaterialien."},
    "Română": {"presenta":"AI-ul lui Antonino prezintă", "language":"Limbă", "headline":"Scrie-ți cartea.<br>Cu metodă, calitate și control.", "subtitle":"De la idee la manuscrisul final: structurează, scrie și exportă cartea cu AI, păstrând mereu controlul.", "bonus":"🎁 50 de credite gratuite. Fără card.", "start":"Începe gratuit cu 50 de credite", "login":"Autentificare", "b1":"Cuprins profesional", "b1t":"Structurează cartea cu capitole și secțiuni clare, complete și flexibile.", "b2":"Scriere ghidată", "b2t":"AI-ul te însoțește capitol cu capitol pentru coerență și calitate.", "b3":"Word și PDF", "b3t":"Exportă cartea în Word și PDF, gata pentru revizuire sau publicare.", "create":"Ce poți crea", "create_sub":"Un singur instrument adaptat proiectului tău editorial.", "c1":"Ghiduri și manuale", "c1t":"Explică, predă și împărtășește competențele tale clar și profesionist.", "c2":"Cărți de rețete", "c2t":"Adună și organizează rețetele cu stil, cuprins și paginare ordonată.", "c3":"Romane, quiz-uri și test prep", "c3t":"Creează povești captivante sau materiale de studiu eficiente și bine structurate."},
    "Русский": {"presenta":"ИИ Антонино представляет", "language":"Язык", "headline":"Напишите свою книгу.<br>С методом, качеством и контролем.", "subtitle":"От идеи до готовой рукописи: планируйте, пишите и экспортируйте книгу с ИИ, сохраняя полный контроль.", "bonus":"🎁 50 бесплатных кредитов. Карта не нужна.", "start":"Начать с 50 кредитами", "login":"Войти", "b1":"Профессиональная структура", "b1t":"Стройте книгу из ясных, полных и гибких глав и разделов.", "b2":"Направляемое написание", "b2t":"ИИ помогает глава за главой сохранять связность и качество.", "b3":"Word и PDF", "b3t":"Экспортируйте книгу в Word и PDF для редактирования или публикации.", "create":"Что можно создать", "create_sub":"Один инструмент для вашего издательского проекта.", "c1":"Руководства и пособия", "c1t":"Объясняйте, обучайте и делитесь знаниями ясно и профессионально.", "c2":"Кулинарные книги", "c2t":"Собирайте и систематизируйте рецепты со стилем и удобной структурой.", "c3":"Романы, тесты и подготовка", "c3t":"Создавайте увлекательные истории и эффективные учебные материалы."},
    "العربية": {"presenta":"ذكاء أنطونينو الاصطناعي يقدّم", "language":"اللغة", "headline":"اكتب كتابك.<br>بمنهجية وجودة وتحكم.", "subtitle":"من الفكرة إلى المخطوطة النهائية: نظّم واكتب وصدّر كتابك بالذكاء الاصطناعي مع الحفاظ على التحكم الكامل.", "bonus":"🎁 50 رصيداً مجانياً. لا تحتاج إلى بطاقة.", "start":"ابدأ مجاناً مع 50 رصيداً", "login":"تسجيل الدخول", "b1":"فهرس احترافي", "b1t":"نظّم كتابك بفصول وأقسام واضحة وكاملة ومرنة.", "b2":"كتابة موجهة", "b2t":"يرافقك الذكاء الاصطناعي فصلاً بعد فصل للحفاظ على الاتساق والجودة.", "b3":"Word وPDF", "b3t":"صدّر كتابك بصيغة Word وPDF جاهزاً للمراجعة أو النشر.", "create":"ما الذي يمكنك إنشاؤه", "create_sub":"أداة واحدة تتكيف مع مشروعك التحريري.", "c1":"أدلة وكتيبات", "c1t":"اشرح وعلّم وشارك خبراتك بوضوح واحتراف.", "c2":"كتب وصفات", "c2t":"اجمع وصفاتك ونظّمها بأسلوب وفهرس وتنسيق مرتب.", "c3":"روايات واختبارات", "c3t":"أنشئ قصصاً ممتعة أو مواد دراسية فعالة ومنظمة."},
    "中文": {"presenta":"Antonino 的 AI 呈现", "language":"语言", "headline":"写下你的书。<br>兼顾方法、品质与掌控。", "subtitle":"从想法到完整书稿：借助 AI 规划、写作和导出，同时始终保持掌控。", "bonus":"🎁 50 个免费积分。无需银行卡。", "start":"免费开始，获赠 50 积分", "login":"登录", "b1":"专业目录", "b1t":"用清晰、完整且灵活的章节和小节组织你的书。", "b2":"引导式写作", "b2t":"AI 逐章协助你保持内容连贯与质量。", "b3":"Word 和 PDF", "b3t":"将图书导出为 Word 或 PDF，方便审阅或出版。", "create":"你可以创作什么", "create_sub":"一款适合你出版项目的工具。", "c1":"指南与手册", "c1t":"以清晰、专业的方式讲解、教学并分享你的专长。", "c2":"食谱书", "c2t":"用良好的风格、目录和版式收集并整理你的食谱。", "c3":"小说、测验与备考", "c3t":"创作引人入胜的故事或有效且结构完善的学习材料。"},
}


class CommercialCreditError(RuntimeError):
    """L'operazione IA non può iniziare perché il saldo è insufficiente."""


def mostra_crediti_esauriti() -> None:
    """Avviso chiaro in pagina: interrompe l'azione senza alterare il manoscritto."""
    st.session_state["commercial_credit_limit"] = True
    st.error("Crediti terminati")
    st.write(
        "Il tuo libro resta disponibile: puoi leggerlo, modificarlo manualmente "
        "ed esportare le parti già create. Per usare di nuovo le funzioni IA, "
        "ricarica i crediti."
    )
    if st.button("💳 Vai a Ricarica crediti", key="commercial_go_to_topup", type="primary"):
        st.session_state["commercial_open_topup"] = True
        st.rerun()


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
    payload = {"email": email.strip(), "password": password}
    app_url = _secret("APP_BASE_URL").rstrip("/")
    if app_url:
        payload["email_redirect_to"] = app_url
    response = requests.post(
        url,
        headers={"apikey": _secret("SUPABASE_ANON_KEY"), "Content-Type": "application/json"},
        json=payload,
        timeout=20,
    )
    if not response.ok:
        # Messaggi utili senza rivelare a terzi se una mail è già registrata.
        try:
            detail = json.dumps(response.json()).lower()
        except ValueError:
            detail = response.text.lower()
        if response.status_code == 429 or "rate limit" in detail:
            raise RuntimeError(
                "Invio email temporaneamente bloccato da Supabase: attendi circa "
                "un'ora prima di riprovare. Per gli utenti reali configura un SMTP personale."
            )
        if "weak_password" in detail or "weak password" in detail:
            raise RuntimeError("La password non rispetta i requisiti minimi di Supabase. Usa almeno 6 caratteri.")
        raise RuntimeError(
            "Non è stato possibile creare l'account. Se questa email è già "
            "registrata, usa Accedi oppure Password dimenticata; altrimenti "
            "riprova tra qualche minuto."
        )


def _supabase_resend_confirmation(email: str) -> None:
    """Reinvia la conferma senza rivelare se l'indirizzo è registrato."""
    url = f"{_secret('SUPABASE_URL').rstrip('/')}/auth/v1/resend"
    payload = {"type": "signup", "email": email.strip()}
    app_url = _secret("APP_BASE_URL").rstrip("/")
    if app_url:
        payload["email_redirect_to"] = app_url
    response = requests.post(
        url,
        headers={"apikey": _secret("SUPABASE_ANON_KEY"), "Content-Type": "application/json"},
        json=payload,
        timeout=20,
    )
    if not response.ok:
        raise RuntimeError("Impossibile reinviare la conferma. Attendi un minuto e riprova.")


def _supabase_recover_password(email: str) -> None:
    """Invia il link di recupero password tramite il sistema sicuro di Supabase."""
    url = f"{_secret('SUPABASE_URL').rstrip('/')}/auth/v1/recover"
    payload = {"email": email.strip()}
    redirect_url = _secret("APP_BASE_URL")
    if redirect_url:
        payload["redirect_to"] = f"{redirect_url.rstrip('/')}?auth=recovery"
    response = requests.post(
        url,
        headers={"apikey": _secret("SUPABASE_ANON_KEY"), "Content-Type": "application/json"},
        json=payload,
        timeout=20,
    )
    if not response.ok:
        raise RuntimeError("Impossibile inviare il link di recupero. Riprova tra poco.")


def _render_password_recovery() -> bool:
    """Mostra e completa il recupero password con controlli nativi Streamlit."""
    try:
        is_recovery = st.query_params.get("auth") == "recovery"
    except Exception:
        is_recovery = False
    if not is_recovery:
        return False

    # Il token_hash viene aggiunto al link dell'email di recupero. A differenza
    # dell'hash della URL, Streamlit può leggerlo in modo affidabile.
    try:
        recovery_token_hash = st.query_params.get("token_hash", "")
    except Exception:
        recovery_token_hash = ""

    supabase_url = _secret("SUPABASE_URL").rstrip("/")
    anon_key = _secret("SUPABASE_ANON_KEY")
    if not (supabase_url and anon_key):
        st.error("Reimpostazione password non disponibile. Riprova dalla pagina di accesso.")
        return True

    recovery_key = "commercial_recovery_access_token"
    access_token = st.session_state.get(recovery_key, "")
    if recovery_token_hash and not access_token:
        try:
            verification = requests.post(
                f"{supabase_url}/auth/v1/verify",
                headers={"apikey": anon_key, "Content-Type": "application/json"},
                json={"token_hash": recovery_token_hash, "type": "recovery"},
                timeout=20,
            )
            data = verification.json() if verification.content else {}
            access_token = data.get("access_token") or data.get("session", {}).get("access_token", "")
            if not verification.ok or not access_token:
                raise RuntimeError("invalid recovery token")
            st.session_state[recovery_key] = access_token

            # Il token serve una sola volta: lo conserviamo solo nella sessione
            # e lo togliamo dall'indirizzo prima di mostrare il form.
            st.query_params.clear()
            st.query_params["auth"] = "recovery"
            st.rerun()
        except Exception:
            st.error("Link non valido o scaduto. Richiedi un nuovo link e riprova.")
            if st.button("Torna all'accesso", key="commercial_invalid_recovery_back"):
                st.query_params.clear()
                st.session_state["commercial_show_auth"] = True
                st.rerun()
            return True

    if not access_token:
        st.error("Link non valido o scaduto. Richiedi un nuovo link e riprova.")
        if st.button("Torna all'accesso", key="commercial_missing_recovery_back"):
            st.query_params.clear()
            st.session_state["commercial_show_auth"] = True
            st.rerun()
        return True

    st.title("Imposta una nuova password")
    st.caption("Scegli una nuova password per il tuo account.")
    password = st.text_input("Nuova password", type="password", key="commercial_recovery_password")
    repeat_password = st.text_input("Ripeti la nuova password", type="password", key="commercial_recovery_password_repeat")
    if st.button("Salva nuova password", type="primary", key="commercial_save_recovery_password"):
        if password != repeat_password:
            st.error("Le due password non coincidono.")
        else:
            response = requests.put(
                f"{supabase_url}/auth/v1/user",
                headers={
                    "apikey": anon_key,
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json={"password": password},
                timeout=20,
            )
            if response.ok:
                st.session_state.pop(recovery_key, None)
                st.session_state["commercial_password_updated_notice"] = True
                st.session_state["commercial_show_auth"] = True
                st.query_params.clear()
                st.rerun()
            elif response.status_code == 422:
                st.error("La password non è accettata dal servizio di autenticazione. Prova una password diversa.")
            else:
                st.error("Non è stato possibile aggiornare la password. Richiedi un nuovo link e riprova.")
    return True


def _landing_page() -> None:
    """Pagina di ingresso pubblica: compare prima dell'accesso."""
    st.markdown(
        """
        <style>
          .stApp, [data-testid="stAppViewContainer"] {background:radial-gradient(circle at 8% 13%,rgba(147,197,253,.47),transparent 28%),radial-gradient(circle at 90% 8%,rgba(186,230,253,.62),transparent 30%),radial-gradient(circle at 76% 78%,rgba(219,234,254,.8),transparent 36%),linear-gradient(135deg,#edf7ff 0%,#f8fcff 47%,#e2f2ff 100%) !important; color:#102a43}
          section.main > div.block-container {max-width:1500px !important; padding:1.05rem 2.4rem 3.5rem !important}
          .ss-hero-copy {padding:4.15rem .7rem 1.5rem 1.3rem; color:#102a43}
          .ss-kicker {font-weight:800; font-size:1.03rem; color:#1689e8; margin-bottom:1.1rem; letter-spacing:.01em}
          .ss-version {display:inline-block; margin:0 0 .75rem; padding:.28rem .55rem; border-radius:99px;
            background:#eaf4fc; border:1px solid #bfdbf0; color:#486581; font-size:.72rem; font-weight:800}
          .ss-title {font-family:Georgia,serif; font-size:clamp(6.2rem,9.6vw,10.2rem); margin:0; color:#cf3345; line-height:.8; letter-spacing:-.09em; text-shadow:0 2px 0 rgba(255,255,255,.8)}
          .ss-title-line {width:68px; height:5px; background:#1689e8; border-radius:99px; margin:1.65rem 0}
          .ss-headline {font-family:Georgia,serif; font-size:clamp(2.2rem,3.45vw,3.55rem); font-weight:800; line-height:1.08; color:#102a43; margin:0 0 1.2rem; letter-spacing:-.035em}
          .ss-subtitle {font-size:1.17rem; max-width:555px; margin:0; color:#486581; line-height:1.58}
          .ss-bonus {display:inline-block; margin:1.3rem 0 .85rem; padding:.62rem .9rem; border-radius:9px;
            font-size:1rem; font-weight:850; color:#9a3412; background:#ffedd5; border:1px solid #fdba74}
          .ss-section {max-width:1080px; margin:1.35rem auto .45rem; text-align:center}
          .ss-section h2 {font-size:2rem; margin-bottom:.16rem; color:#102a43}
          .ss-card {background:#fff; border:1px solid #d9e5f0;
            border-radius:13px; padding:1.05rem .95rem; min-height:112px; box-shadow:none}
          .ss-card h3 {margin:0 0 .34rem; color:#1269ae; font-size:1rem}
          .ss-card p {margin:0; font-size:.9rem; line-height:1.35}
          .ss-price {font-size:1.35rem; font-weight:800; color:#1269ae; margin:.15rem 0}
          .ss-muted {color:#486581; text-align:center; margin:.1rem auto .75rem; max-width:720px; font-size:.94rem}
          .ss-step {background:#fff; border:1px solid #d9e5f0; border-radius:13px; padding:1.15rem 1.05rem;
            min-height:150px; text-align:left; font-size:1rem; line-height:1.48}
          .ss-step strong {display:block; color:#1269ae; margin-bottom:.3rem; font-size:1.18rem}
          .ss-feature {background:transparent; border:0; border-top:1px solid #cbd9e6; border-radius:0; padding:1rem .3rem;
            min-height:100px; box-shadow:none}
          .ss-feature strong {display:block; color:#102a43; font-size:1rem; margin-bottom:.3rem}
          .ss-feature p {margin:0; color:#486581; font-size:.9rem; line-height:1.38}
          .ss-language-wrap {max-width:1500px; margin:0 auto -2.3rem; display:flex; justify-content:flex-end}
          .ss-creator {display:flex; align-items:center; gap:1rem; min-height:145px; padding:1rem 1.15rem; background:#fff; border:1px solid #d9e5f0; border-radius:13px; box-shadow:0 8px 22px rgba(20,77,120,.055)}
          .ss-creator-icon {flex:0 0 92px; height:105px; display:flex; align-items:center; justify-content:center; color:#fff; font-size:2.6rem; border-radius:8px 16px 12px 8px; background:linear-gradient(145deg,#164c75,#0b263e); box-shadow:7px 7px 0 rgba(22,137,232,.15)}
          .ss-creator-icon.recipe {background:linear-gradient(145deg,#9c5b31,#e0a250)} .ss-creator-icon.story {background:linear-gradient(145deg,#0c1d31,#2c4d6f)}
          .ss-creator-copy {min-width:0}.ss-creator-copy b {display:block; color:#102a43; font-size:1.08rem; margin-bottom:.48rem}.ss-creator-copy p {margin:0; color:#486581; line-height:1.42; font-size:.94rem}.ss-creator-arrow {margin-left:auto; color:#1689e8; font-size:1.6rem}
          .ss-proof {margin:1.25rem .2rem 1.2rem .15rem; padding:1.35rem; border-radius:18px;
            background:linear-gradient(135deg,#071728 0%,#0b2642 58%,#133c62 100%); color:#e0f2fe;
            box-shadow:0 22px 46px rgba(15,23,42,.27); border:1px solid rgba(125,211,252,.16)}
          .ss-proof-top {display:flex; gap:.45rem; align-items:center; padding:0 0 .8rem;
            border-bottom:1px solid rgba(255,255,255,.16); font-size:.9rem; color:#bae6fd}
          .ss-dot {width:10px; height:10px; border-radius:50%; background:#fb7185; display:inline-block}
          .ss-dot:nth-child(2) {background:#fbbf24}.ss-dot:nth-child(3) {background:#4ade80}
          .ss-proof-label {margin-left:auto; font-size:.72rem; border:1px solid rgba(125,211,252,.45); padding:.2rem .48rem; border-radius:99px}
          .ss-proof-grid {display:grid; grid-template-columns:43% 1fr; gap:1.05rem; padding-top:1.1rem; text-align:left}
          .ss-proof-index,.ss-proof-page {border-radius:12px; padding:1.05rem; background:rgba(255,255,255,.075)}
          .ss-proof-index b {display:block; color:#f9a8d4; margin-bottom:.55rem}
          .ss-proof-index span {display:block; padding:.32rem 0; border-bottom:1px solid rgba(255,255,255,.09); font-size:.84rem}
          .ss-proof-index .active {margin:.35rem -.35rem; padding:.42rem .35rem; background:rgba(45,212,191,.18); border-left:3px solid #5eead4; border-radius:5px; color:#fff}
          .ss-proof-book {position:relative; min-height:385px; display:flex; align-items:center; justify-content:center; gap:0; padding:1rem .25rem; border-radius:12px; overflow:hidden; background:radial-gradient(circle at 18% 10%,rgba(125,211,252,.16),transparent 38%),linear-gradient(145deg,#102f4c,#071728); box-shadow:inset 0 0 35px rgba(0,0,0,.3)}
          .ss-book-page {position:relative; width:46%; height:78%; padding:1.55rem .5rem; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; color:#2d3748; background:linear-gradient(135deg,#fffdf6,#e8dfcf); box-shadow:0 9px 22px rgba(0,0,0,.36)}
          .ss-book-page small {color:#4a5568; font-family:Georgia,serif; font-size:.68rem; margin-bottom:1.4rem}.ss-book-page b {font:700 1.1rem/1.38 Georgia,serif; max-width:115px}
          .ss-book-left {border-radius:10px 2px 2px 18px; transform:perspective(440px) rotateY(13deg) rotateZ(-2deg)}
          .ss-book-right {border-radius:2px 10px 18px 2px; transform:perspective(440px) rotateY(-13deg) rotateZ(2deg)}
          .ss-book-page:after {content:''; position:absolute; left:18%; right:18%; bottom:20%; height:1px; background:#b9ad98; box-shadow:0 -15px 0 #cfc3ae,0 -30px 0 #cfc3ae,0 -45px 0 #cfc3ae}
          .ss-proof-toolbar {display:flex; gap:.42rem; align-items:center; margin-bottom:.8rem; flex-wrap:wrap}
          .ss-proof-pill {font-size:.72rem; padding:.28rem .55rem; border-radius:99px; background:rgba(125,211,252,.16); color:#bae6fd}
          .ss-proof-action {margin-left:auto; background:#f97316; color:#fff; border-radius:7px; padding:.38rem .62rem; font-size:.74rem; font-weight:800}
          .ss-proof-page small {color:#7dd3fc; font-weight:800}.ss-proof-page h3 {color:#fff; margin:.38rem 0 .5rem}
          .ss-proof-page p {margin:0; color:#dbeafe; font-size:.9rem; line-height:1.55}
          .ss-proof-lines {margin:.85rem 0}.ss-proof-lines i {display:block; height:7px; margin:.42rem 0; border-radius:9px; background:linear-gradient(90deg,rgba(255,255,255,.22),rgba(255,255,255,.05))}
          .ss-proof-lines i:nth-child(2) {width:91%}.ss-proof-lines i:nth-child(3) {width:77%}.ss-proof-lines i:nth-child(4) {width:84%}
          .ss-proof-progress {display:flex; align-items:center; gap:.65rem; color:#bbf7d0; font-size:.78rem; font-weight:700}
          .ss-proof-progress div {height:8px; border-radius:99px; background:rgba(255,255,255,.18); flex:1; overflow:hidden}.ss-proof-progress div span {display:block; width:64%; height:100%; background:linear-gradient(90deg,#2dd4bf,#60a5fa); border-radius:99px}
          .ss-credit-note {max-width:850px; margin:.7rem auto 1.3rem; padding:1rem 1.15rem; border-radius:13px;
            text-align:center; background:#eaf4fc; color:#174a73; border:1px solid #bfdbf0; font-weight:650}
          .ss-trust {max-width:920px; margin:1.15rem auto 1.5rem; text-align:center; padding:1rem;
            border-radius:13px; background:#fff; color:#174a73; border:1px solid #d9e5f0; font-weight:700}
          .ss-benefits {max-width:1160px; margin:.7rem auto 2.25rem; padding:.55rem .25rem; background:#fff; border:1px solid #d9e5f0; border-radius:14px; display:grid; grid-template-columns:repeat(3,1fr); box-shadow:0 10px 26px rgba(20,77,120,.07)}
          .ss-benefit {min-height:122px; padding:1.25rem 1.45rem; color:#486581; font-size:1.04rem; line-height:1.48; border-right:1px solid #d9e5f0}
          .ss-benefit:last-child {border-right:0}.ss-benefit b {display:block; color:#102a43; font-size:1.2rem; margin-bottom:.42rem}
          @media (max-width:760px) {section.main > div.block-container {padding:1rem 1rem 2.5rem !important}.ss-hero-copy {padding:1.5rem .4rem}.ss-title {font-size:4rem}.ss-proof-grid {grid-template-columns:1fr}.ss-proof-action {margin-left:0}.ss-benefits {grid-template-columns:1fr}.ss-benefit {border-right:0;border-bottom:1px solid #d9e5f0}.ss-benefit:last-child {border-bottom:0}.ss-creator {min-height:120px}.ss-language-wrap {margin:0}}
          [data-testid="stMain"] .stButton button {min-height:3.35rem; border-radius:11px; font-size:1.08rem;
            font-weight:800; border:1px solid #1689e8; background:#1689e8 !important;
            border-color:#1689e8 !important; color:#fff !important; box-shadow:0 6px 14px rgba(22,137,232,.18)}
          [data-testid="stMain"] .stButton button[kind="secondary"] {background:#fff !important; color:#1269ae !important; border-color:#8ec5ee !important; box-shadow:none}
          /* Home pubblica: nasconde i comandi tecnici di Streamlit. */
          [data-testid="stHeader"] {background:transparent !important}
          [data-testid="stToolbar"], [data-testid="stToolbarActions"], [data-testid="stStatusWidget"],
          .stAppDeployButton, #MainMenu, footer, button[title="Manage app"], a[title="Manage app"],
          button[aria-label="Manage app"], a[aria-label="Manage app"] {display:none !important}
          [data-testid="stExpander"] {max-width:860px; margin:.5rem auto; background:#fff !important;
            border:1px solid #d9e5f0 !important; border-radius:12px !important; overflow:hidden}
          [data-testid="stExpander"] details, [data-testid="stExpander"] summary,
          [data-testid="stExpander"] [data-testid="stExpanderDetails"] {background:#fff !important; color:#102a43 !important}
          [data-testid="stExpander"] summary:hover {background:#f5f9fd !important}
        </style>
        """,
        unsafe_allow_html=True,
    )

    language_spacer, language_picker = st.columns([0.82, 0.18])
    with language_picker:
        home_language = st.selectbox(
            "🌐",
            list(HOME_COPY.keys()),
            key="commercial_home_language",
            label_visibility="collapsed",
        )
    H = HOME_COPY[home_language]

    hero_copy, hero_visual = st.columns([0.42, 0.58], gap="large")
    with hero_copy:
        st.markdown(
            f"""<div class='ss-hero-copy'>
              <div class='ss-kicker'>{H['presenta']}</div>
              <div class='ss-version'>Versione app: {COMMERCIAL_VERSION}</div>
              <h1 class='ss-title' style='color:#cf3345 !important'>Scrittore Site</h1>
              <div class='ss-title-line'></div>
              <div class='ss-headline'>{H['headline']}</div>
              <p class='ss-subtitle'>{H['subtitle']}</p>
              <div class='ss-bonus'>{H['bonus']}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        cta_a, cta_b = st.columns([1.45, 0.85])
        with cta_a:
            if st.button(H['start'], type="primary", use_container_width=True, key="landing_signup"):
                st.session_state["commercial_show_auth"] = True
                st.session_state["commercial_auth_hint"] = "signup"
                st.rerun()
        with cta_b:
            if st.button(H['login'], use_container_width=True, key="landing_login"):
                st.session_state["commercial_show_auth"] = True
                st.session_state["commercial_auth_hint"] = "login"
                st.rerun()
    with hero_visual:
        base_dir = Path(__file__).resolve().parent
        preview_image = next(
            (candidate for candidate in (
                base_dir / "home-editor-preview.png",
                base_dir / "download.png",
                base_dir / "assets" / "home-editor-preview.png",
            ) if candidate.is_file()),
            None,
        )
        if preview_image:
            st.image(str(preview_image), use_container_width=True)
        else:
            # La pagina resta utilizzabile anche durante il primo deploy, prima
            # dell'upload dell'anteprima grafica nel repository.
            st.markdown(
                "<div class='ss-proof'><div class='ss-proof-top'>Anteprima dell'editor</div>"
                "<div class='ss-proof-grid'><div class='ss-proof-book'></div>"
                "<div class='ss-proof-page'><div class='ss-proof-toolbar'><span class='ss-proof-pill'>Struttura</span>"
                "<span class='ss-proof-pill'>Scrittura</span></div><div class='ss-proof-index'><b>INDICE</b>"
                "<span class='active'>1&nbsp;&nbsp; Il tuo libro</span><span>2&nbsp;&nbsp; Capitolo successivo</span></div>"
                "<h3>Scrivi con controllo</h3><div class='ss-proof-lines'><i></i><i></i><i></i></div></div></div></div>",
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""<div class='ss-benefits'>
          <div class='ss-benefit'><b>▤ &nbsp;{H['b1']}</b>{H['b1t']}</div>
          <div class='ss-benefit'><b>✎ &nbsp;{H['b2']}</b>{H['b2t']}</div>
          <div class='ss-benefit'><b>⇩ &nbsp;{H['b3']}</b>{H['b3t']}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown(f"<div class='ss-section'><h2>{H['create']}</h2><p class='ss-muted'>{H['create_sub']}</p></div>", unsafe_allow_html=True)
    creator_cards = st.columns(3)
    for column, icon_class, icon, title, text in (
        (creator_cards[0], "", "⚙", H['c1'], H['c1t']),
        (creator_cards[1], "recipe", "♨", H['c2'], H['c2t']),
        (creator_cards[2], "story", "✦", H['c3'], H['c3t']),
    ):
        with column:
            st.markdown(f"<div class='ss-creator'><div class='ss-creator-icon {icon_class}'>{icon}</div><div class='ss-creator-copy'><b>{title}</b><p>{text}</p></div><div class='ss-creator-arrow'>→</div></div>", unsafe_allow_html=True)

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
    st.markdown("<div class='ss-credit-note'>Un libro standard fino a 80 sezioni usa normalmente 95 crediti: 80 sezioni, indice, voto dell’indice, controllo coerenza e metadati. Le funzioni avanzate consumano crediti aggiuntivi solo dopo il preventivo.</div>", unsafe_allow_html=True)
    st.markdown("<div class='ss-trust'>Il libro resta sotto il tuo controllo: puoi fermare la scrittura, rivedere ogni sezione e decidere tu cosa esportare o pubblicare.</div>", unsafe_allow_html=True)

    st.markdown("<div class='ss-section'><h2>Pacchetti crediti</h2><p class='ss-muted'>Scegli solo ciò che ti serve.</p></div>", unsafe_allow_html=True)
    price_columns = st.columns(len(PACKAGES))
    for column, (package_key, package) in zip(price_columns, PACKAGES.items()):
        price = f"€ {package['amount_cents'] / 100:.2f}".replace(".", ",")
        with column:
            st.markdown(
                f"<div class='ss-card'><h3>{package['name'].replace('Pacchetto ', '')}</h3>"
                f"<div class='ss-price'>{price}</div><p>{package['credits']} crediti</p>"
                f"<p><strong>{PACKAGE_BOOK_ESTIMATES[package_key]}</strong></p></div>",
                unsafe_allow_html=True,
            )
    st.caption(PACKAGE_ESTIMATE_NOTE)

    st.markdown("<div class='ss-section'><h2>Domande frequenti</h2></div>", unsafe_allow_html=True)
    with st.expander("Posso iniziare senza esperienza editoriale?"):
        st.write("Sì. Scrittore Site guida la preparazione del brief e mantiene ordinati i passaggi di lavoro.")
    with st.expander("I crediti servono per cosa?"):
        st.write("I crediti permettono di usare le funzioni IA di progettazione, scrittura, revisione e miglioramento del libro. Ogni azione mostra il proprio preventivo prima di iniziare.")
    with st.expander("Quanti libri posso creare con un pacchetto?"):
        st.write("Le stime sui pacchetti fanno riferimento a un libro standard fino a 80 sezioni. Il consumo reale dipende dalla lunghezza dei testi e dall’uso di rigenerazioni, immagini, ricette, simulazioni Test Prep e verifiche online.")
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

    if _render_password_recovery():
        st.stop()

    if st.session_state.pop("commercial_password_updated_notice", False):
        st.success("Password aggiornata correttamente. Ora puoi accedere con quella nuova.")

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
                st.session_state["commercial_pending_confirmation_email"] = email.strip()
                st.success("Account creato. Controlla l'email di conferma, poi accedi.")
            except Exception as error:
                st.error(str(error))
        st.divider()
        st.caption("Non hai ricevuto l’email di conferma?")
        resend_email = st.text_input(
            "Email per reinviare la conferma",
            value=st.session_state.get("commercial_pending_confirmation_email", ""),
            key="commercial_resend_confirmation_email",
        )
        if st.button("Reinvia email di conferma", key="commercial_resend_confirmation"):
            if not resend_email.strip():
                st.warning("Inserisci prima il tuo indirizzo e-mail.")
            else:
                try:
                    _supabase_resend_confirmation(resend_email)
                    st.success("Se esiste una registrazione da confermare, riceverai a breve una nuova email.")
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
            st.session_state["commercial_credit_limit"] = True
            raise CommercialCreditError("Crediti insufficienti. Ricarica il saldo prima di avviare un'altra elaborazione.")
        st.session_state["commercial_demo_credits"] = balance - amount
        _demo_ledger(reason, -amount, reference)
        return reference

    result = _supabase("POST", "rest/v1/rpc/spend_credits", payload={"p_user_id": user["id"], "p_credits": amount, "p_reason": reason, "p_reference": reference})
    if result is not True:
        st.session_state["commercial_credit_limit"] = True
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
        package = PACKAGES.get(package_key) or LEGACY_PACKAGES.get(package_key)
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
            st.session_state["commercial_checkout_notice"] = (
                f"Pagamento verificato: aggiunti {package['credits']} crediti."
            )
        else:
            st.session_state["commercial_checkout_notice"] = (
                "Questo pagamento era già stato registrato: il saldo è aggiornato."
            )
        st.query_params.clear()
        # Riapre l'app in stato pulito dopo Stripe: il saldo nella sidebar
        # viene quindi riletto subito da Supabase, senza nuovo login.
        st.rerun()
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

        refresh_clicked = st.button(
            "🔄 AGGIORNA SALDO CREDITI",
            key="commercial_refresh_credits",
            use_container_width=True,
            type="primary",
            help="Usalo dopo un acquisto completato in un'altra scheda.",
        )
        if is_admin:
            st.metric("Saldo disponibile", "∞ crediti")
            st.success("Account amministratore: crediti illimitati attivi.")
        else:
            st.metric("Saldo disponibile", f"{_balance(user['id'])} crediti")
        if refresh_clicked:
            st.success("Saldo crediti aggiornato.")
        checkout_notice = st.session_state.pop("commercial_checkout_notice", "")
        if checkout_notice:
            st.success(checkout_notice)
        if not is_admin and _mode() != "demo":
            st.caption("Dopo un pagamento concluso in un'altra scheda, premi il pulsante azzurro qui sopra.")

        apri_ricarica = bool(st.session_state.pop("commercial_open_topup", False))
        with st.expander("Ricarica crediti", expanded=apri_ricarica):
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
    try:
        recovery_requested = st.query_params.get("auth") == "recovery"
    except Exception:
        recovery_requested = False
    if recovery_requested:
        st.session_state["commercial_show_auth"] = True
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
