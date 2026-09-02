"""Accesso, crediti e pagamenti per la versione commerciale di Scrittore Site."""
from __future__ import annotations

import os
import uuid
import json
from pathlib import Path
from typing import Any

import requests
import streamlit as st


COMMERCIAL_VERSION = "beta 3c"
# Alias mantenuto per compatibilità con l'app commerciale già predisposta.
COMMERCIAL_TEST_VERSION = COMMERCIAL_VERSION
DEMO_INITIAL_CREDITS = 50
# Griglia commerciale: un Test Prep approfondito fino a 60 sezioni usa normalmente
# 75 crediti (60 sezioni, indice, voto, controllo finale e metadati).
AI_REQUEST_CREDITS = 1
STANDARD_BOOK_CREDITS = 75
# Tariffario unico delle azioni IA. Un credito dei pacchetti principali vale
# circa €0,0667: le azioni leggere con GPT-5.4 mini restano a 1 credito,
# mentre ricerca web e revisioni GPT-5.4 usano una quota superiore in rapporto
# al costo API. Le azioni senza IA (lettura, export, CSV e modifica manuale)
# restano gratuite.
CREDIT_COSTS = {
    "scrittura_sezione": 1,
    "indice_ricerca_web": 2,
    "indice_generazione_editoriale": 3,
    "voto_indice": 1,
    "rigenera_indice": 3,
    "verifica_fatti_web": 2,
    "audit_fatti_capitolo": 2,
    "controllo_coerenza_iniziale": 10,
    "controllo_coerenza_blocco_modificato": 1,
    "report_sintattico": 1,
    "metadati_kdp": 1,
    "immagine_capitolo": 5,
    "ricette_dieci": 10,
    "copyright_web_rapido": 2,
    "copyright_lotto_screening_mini": 1,
    # Si applica soltanto se il lotto è segnalato e richiede il secondo
    # passaggio con GPT-5.4 completo + ricerca web.
    "copyright_lotto_revisione_gpt54": 2,
}
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

# Stime commerciali: un Test Prep approfondito usa normalmente 75 crediti
# (60 sezioni + 15 crediti per indice, voto, controllo finale e metadati).
PACKAGE_BOOK_ESTIMATES = {
    "prova_15": "15 crediti per provare le funzioni principali",
    "base_150": "Fino a 2 Test Prep completi",
    "creator_375": "Fino a 5 Test Prep completi",
    "studio_750": "Fino a 10 Test Prep completi",
    "professionale_1500": "Fino a 20 Test Prep completi",
}
PACKAGE_ESTIMATE_NOTE = (
    "Stima indicativa: un Test Prep approfondito considera 60 sezioni e 15 crediti "
    "per indice, voto, controllo coerenza e metadati (75 crediti totali). "
    "Il consumo effettivo dipende da lunghezza, rigenerazioni, immagini, "
    "verifiche online e funzioni avanzate utilizzate."
)

# Testo commerciale prudente: i crediti residui proteggono l'utente quando
# desidera rigenerare, verificare fatti o usare strumenti aggiuntivi.
PACKAGE_HOME_GUIDE = {
    "prova_15": {
        "ideal": "Ideale per: provare indice, editor e prime sezioni.",
        "estimate": "Stima prudente: indice e fino a 10–12 sezioni brevi.",
    },
    "base_150": {
        "ideal": "Ideale per: il primo manuale o progetto editoriale completo.",
        "estimate": "Stima prudente: 1 libro standard da circa 80 sezioni, con margine per controlli.",
    },
    "creator_375": {
        "ideal": "Ideale per: chi pubblica più guide, manuali o Test Prep.",
        "estimate": "Stima prudente: fino a 3 libri standard oppure fino a 5 Test Prep completi.",
    },
    "studio_750": {
        "ideal": "Ideale per: creator, docenti e progetti editoriali continuativi.",
        "estimate": "Stima prudente: fino a 7 libri standard oppure fino a 10 Test Prep completi.",
    },
    "professionale_1500": {
        "ideal": "Ideale per: professionisti, scuole e cataloghi di più libri.",
        "estimate": "Stima prudente: fino a 15 libri standard oppure fino a 20 Test Prep completi.",
    },
}

CONTACT_LABELS = {
    "Italiano": "CONTATTI",
    "English": "CONTACTS",
    "Español": "CONTACTOS",
    "Français": "CONTACTS",
    "Deutsch": "KONTAKTE",
    "Română": "CONTACTE",
    "Русский": "КОНТАКТЫ",
    "العربية": "تواصل معنا",
    "中文": "联系我们",
}

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

# Tutta la parte descrittiva della home usa contenuti nativi nella lingua
# selezionata. Non effettua traduzioni con l'AI e non consuma crediti.
HOME_BODY_COPY = {
    "Italiano": {
        "community": "La nostra Community", "version": "Versione app",
        "body": """<div class='ss-section'><h2>Dall'idea al libro, con controllo reale</h2><p class='ss-muted'>Compila la sidebar, crea un indice studiato, sviluppa il testo e decidi tu ogni modifica.</p></div><div class='ss-priority-grid'><div class='ss-priority'><div class='ss-priority-icon'>🧭</div><b>Progetto su misura</b><p>Brief, pubblico, genere, stile e obiettivo guidano ogni fase del libro.</p><span class='ss-priority-tag'>SIDEBAR GUIDATA</span></div><div class='ss-priority'><div class='ss-priority-icon'>🧠</div><b>Indice studiato</b><p>Ricerca preliminare, struttura professionale, voto editoriale e correzioni mirate.</p><span class='ss-priority-tag'>STRUTTURA</span></div><div class='ss-priority'><div class='ss-priority-icon'>✍️</div><b>Scrittura controllabile</b><p>Genera una sezione, un capitolo o tutto il libro; correggi soltanto ciò che desideri.</p><span class='ss-priority-tag'>TESTO</span></div><div class='ss-priority'><div class='ss-priority-icon'>🔍</div><b>Qualità e originalità</b><p>Controlli su coerenza, completezza, fonti e possibili somiglianze prima dell'esportazione.</p><span class='ss-priority-tag'>REVISIONE</span></div></div><div class='ss-section'><h2>Tutto il progetto resta recuperabile</h2><p class='ss-muted'>Salva manualmente la sessione, esporta un CSV completo e riprendi il lavoro quando vuoi.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 Importa ed esporta</b>CSV completo con sidebar, indice, testi, fonti e immagini associate.</div><div class='ss-benefit'><b>🔊 Anteprima e lettura vocale</b>Leggi, ascolta, metti in pausa e riprendi il manoscritto direttamente nel browser.</div><div class='ss-benefit'><b>📄 Word, PDF e KDP</b>Prepara il manoscritto per revisione, stampa o pubblicazione.</div></div><div class='ss-section'><h2>Domande frequenti</h2><p class='ss-muted'>Crediti solo per le elaborazioni IA; lettura, modifiche manuali, CSV ed export restano gratuiti. Il libro non viene mai pubblicato automaticamente.</p></div>""",
        "packages": "Pacchetti crediti chiari", "package_sub": "Scegli il pacchetto in base al tuo progetto. Le stime sono prudenti e includono margine per i controlli.", "credit_word": "crediti",
        "package_hints": ["Per provare le funzioni principali.", "Per un primo progetto completo.", "Per più guide o Test Prep.", "Per lavoro editoriale continuativo.", "Per cataloghi e uso professionale."],
    },
    "English": {
        "community": "Our Community", "version": "App version",
        "body": """<div class='ss-section'><h2>From idea to book, with real control</h2><p class='ss-muted'>Complete the sidebar, build a researched outline, develop the text, and decide every change yourself.</p></div><div class='ss-priority-grid'><div class='ss-priority'><div class='ss-priority-icon'>🧭</div><b>A tailored project</b><p>Your brief, audience, genre, style and goal guide every stage of the book.</p><span class='ss-priority-tag'>GUIDED SIDEBAR</span></div><div class='ss-priority'><div class='ss-priority-icon'>🧠</div><b>A researched outline</b><p>Preliminary research, professional structure, editorial scoring and targeted improvements.</p><span class='ss-priority-tag'>STRUCTURE</span></div><div class='ss-priority'><div class='ss-priority-icon'>✍️</div><b>Writing you control</b><p>Generate one section, a chapter or the whole book; revise only what you choose.</p><span class='ss-priority-tag'>WRITING</span></div><div class='ss-priority'><div class='ss-priority-icon'>🔍</div><b>Quality and originality</b><p>Checks for consistency, completeness, sources and possible similarities before export.</p><span class='ss-priority-tag'>REVIEW</span></div></div><div class='ss-section'><h2>Your whole project remains recoverable</h2><p class='ss-muted'>Save your session manually, export a complete CSV file and resume work whenever you wish.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 Import and export</b>A complete CSV with sidebar, outline, text, sources and linked images.</div><div class='ss-benefit'><b>🔊 Preview and voice reader</b>Read, listen, pause and resume the manuscript directly in your browser.</div><div class='ss-benefit'><b>📄 Word, PDF and KDP</b>Prepare your manuscript for editing, printing or publishing.</div></div><div class='ss-section'><h2>Frequently asked questions</h2><p class='ss-muted'>Credits are used only for AI work; reading, manual edits, CSV and export remain free. Your book is never published automatically.</p></div>""",
        "packages": "Clear credit packages", "package_sub": "Choose a package for your project. Estimates are conservative and include room for checks.", "credit_word": "credits",
        "package_hints": ["To try the main features.", "For a first complete project.", "For several guides or Test Prep books.", "For ongoing editorial work.", "For catalogs and professional use."],
    },
    "Español": {
        "community": "Nuestra Comunidad", "version": "Versión de la app",
        "body": """<div class='ss-section'><h2>De la idea al libro, con control real</h2><p class='ss-muted'>Completa la barra lateral, crea un índice documentado, desarrolla el texto y decide cada cambio.</p></div><div class='ss-priority-grid'><div class='ss-priority'><div class='ss-priority-icon'>🧭</div><b>Proyecto a medida</b><p>El briefing, público, género, estilo y objetivo guían cada fase del libro.</p><span class='ss-priority-tag'>BARRA GUIADA</span></div><div class='ss-priority'><div class='ss-priority-icon'>🧠</div><b>Índice estudiado</b><p>Investigación previa, estructura profesional, evaluación editorial y mejoras específicas.</p><span class='ss-priority-tag'>ESTRUCTURA</span></div><div class='ss-priority'><div class='ss-priority-icon'>✍️</div><b>Escritura controlable</b><p>Genera una sección, un capítulo o todo el libro; revisa solo lo que elijas.</p><span class='ss-priority-tag'>TEXTO</span></div><div class='ss-priority'><div class='ss-priority-icon'>🔍</div><b>Calidad y originalidad</b><p>Controles de coherencia, integridad, fuentes y posibles similitudes antes de exportar.</p><span class='ss-priority-tag'>REVISIÓN</span></div></div><div class='ss-section'><h2>Todo tu proyecto se puede recuperar</h2><p class='ss-muted'>Guarda la sesión manualmente, exporta un CSV completo y retoma el trabajo cuando quieras.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 Importar y exportar</b>CSV completo con barra lateral, índice, textos, fuentes e imágenes vinculadas.</div><div class='ss-benefit'><b>🔊 Vista previa y lector de voz</b>Lee, escucha, pausa y reanuda el manuscrito en el navegador.</div><div class='ss-benefit'><b>📄 Word, PDF y KDP</b>Prepara el manuscrito para revisión, impresión o publicación.</div></div><div class='ss-section'><h2>Preguntas frecuentes</h2><p class='ss-muted'>Los créditos solo se usan para elaboraciones con IA; lectura, edición manual, CSV y exportación son gratis. El libro nunca se publica automáticamente.</p></div>""",
        "packages": "Paquetes de créditos claros", "package_sub": "Elige un paquete según tu proyecto. Las estimaciones son prudentes e incluyen margen para controles.", "credit_word": "créditos",
        "package_hints": ["Para probar las funciones principales.", "Para un primer proyecto completo.", "Para varias guías o Test Prep.", "Para trabajo editorial continuo.", "Para catálogos y uso profesional."],
    },
    "Français": {
        "community": "Notre communauté", "version": "Version de l’application",
        "body": """<div class='ss-section'><h2>De l’idée au livre, avec un vrai contrôle</h2><p class='ss-muted'>Remplissez la barre latérale, créez un plan documenté, développez le texte et décidez de chaque modification.</p></div><div class='ss-priority-grid'><div class='ss-priority'><div class='ss-priority-icon'>🧭</div><b>Projet sur mesure</b><p>Le brief, le public, le genre, le style et l’objectif guident chaque étape.</p><span class='ss-priority-tag'>BARRE GUIDÉE</span></div><div class='ss-priority'><div class='ss-priority-icon'>🧠</div><b>Plan étudié</b><p>Recherche préalable, structure professionnelle, évaluation éditoriale et améliorations ciblées.</p><span class='ss-priority-tag'>STRUCTURE</span></div><div class='ss-priority'><div class='ss-priority-icon'>✍️</div><b>Rédaction maîtrisée</b><p>Générez une section, un chapitre ou tout le livre; modifiez seulement ce que vous choisissez.</p><span class='ss-priority-tag'>TEXTE</span></div><div class='ss-priority'><div class='ss-priority-icon'>🔍</div><b>Qualité et originalité</b><p>Contrôles de cohérence, complétude, sources et similitudes possibles avant l’export.</p><span class='ss-priority-tag'>RÉVISION</span></div></div><div class='ss-section'><h2>Votre projet reste récupérable</h2><p class='ss-muted'>Sauvegardez la session manuellement, exportez un CSV complet et reprenez le travail quand vous le souhaitez.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 Importer et exporter</b>CSV complet avec barre latérale, plan, textes, sources et images liées.</div><div class='ss-benefit'><b>🔊 Aperçu et lecteur vocal</b>Lisez, écoutez, mettez en pause et reprenez le manuscrit dans le navigateur.</div><div class='ss-benefit'><b>📄 Word, PDF et KDP</b>Préparez le manuscrit pour révision, impression ou publication.</div></div><div class='ss-section'><h2>Questions fréquentes</h2><p class='ss-muted'>Les crédits servent seulement aux travaux IA; lecture, modifications manuelles, CSV et export restent gratuits. Le livre n’est jamais publié automatiquement.</p></div>""",
        "packages": "Forfaits de crédits clairs", "package_sub": "Choisissez un forfait selon votre projet. Les estimations sont prudentes et incluent une marge pour les contrôles.", "credit_word": "crédits",
        "package_hints": ["Pour essayer les fonctions principales.", "Pour un premier projet complet.", "Pour plusieurs guides ou Test Prep.", "Pour un travail éditorial continu.", "Pour catalogues et usage professionnel."],
    },
    "Deutsch": {
        "community": "Unsere Community", "version": "App-Version",
        "body": """<div class='ss-section'><h2>Von der Idee zum Buch – mit echter Kontrolle</h2><p class='ss-muted'>Füllen Sie die Seitenleiste aus, erstellen Sie eine recherchierte Gliederung und entscheiden Sie über jede Änderung.</p></div><div class='ss-priority-grid'><div class='ss-priority'><div class='ss-priority-icon'>🧭</div><b>Maßgeschneidertes Projekt</b><p>Briefing, Zielgruppe, Genre, Stil und Ziel steuern jede Phase des Buchs.</p><span class='ss-priority-tag'>GEFÜHRTE SIDEBAR</span></div><div class='ss-priority'><div class='ss-priority-icon'>🧠</div><b>Durchdachte Gliederung</b><p>Vorabrecherche, professionelle Struktur, Bewertung und gezielte Verbesserungen.</p><span class='ss-priority-tag'>STRUKTUR</span></div><div class='ss-priority'><div class='ss-priority-icon'>✍️</div><b>Kontrollierbares Schreiben</b><p>Erstellen Sie einen Abschnitt, ein Kapitel oder das ganze Buch und ändern Sie nur Gewünschtes.</p><span class='ss-priority-tag'>TEXT</span></div><div class='ss-priority'><div class='ss-priority-icon'>🔍</div><b>Qualität und Originalität</b><p>Prüfungen auf Kohärenz, Vollständigkeit, Quellen und mögliche Ähnlichkeiten vor dem Export.</p><span class='ss-priority-tag'>PRÜFUNG</span></div></div><div class='ss-section'><h2>Ihr Projekt bleibt wiederherstellbar</h2><p class='ss-muted'>Speichern Sie die Sitzung manuell, exportieren Sie eine vollständige CSV-Datei und setzen Sie später fort.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 Import und Export</b>Vollständige CSV mit Sidebar, Gliederung, Texten, Quellen und Bildern.</div><div class='ss-benefit'><b>🔊 Vorschau und Sprachleser</b>Lesen, hören, pausieren und fortsetzen direkt im Browser.</div><div class='ss-benefit'><b>📄 Word, PDF und KDP</b>Bereiten Sie das Manuskript für Überarbeitung, Druck oder Veröffentlichung vor.</div></div><div class='ss-section'><h2>Häufige Fragen</h2><p class='ss-muted'>Credits gelten nur für KI-Verarbeitungen; Lesen, manuelle Änderungen, CSV und Export bleiben kostenlos. Das Buch wird nie automatisch veröffentlicht.</p></div>""",
        "packages": "Klare Credit-Pakete", "package_sub": "Wählen Sie ein Paket für Ihr Projekt. Die Schätzungen sind vorsichtig und enthalten Spielraum für Prüfungen.", "credit_word": "Credits",
        "package_hints": ["Zum Testen der Hauptfunktionen.", "Für ein erstes vollständiges Projekt.", "Für mehrere Ratgeber oder Test Prep.", "Für laufende Redaktionsarbeit.", "Für Kataloge und professionelle Nutzung."],
    },
    "Română": {
        "community": "Comunitatea noastră", "version": "Versiunea aplicației",
        "body": """<div class='ss-section'><h2>De la idee la carte, cu control real</h2><p class='ss-muted'>Completează bara laterală, creează un cuprins documentat, dezvoltă textul și decide fiecare modificare.</p></div><div class='ss-priority-grid'><div class='ss-priority'><div class='ss-priority-icon'>🧭</div><b>Proiect personalizat</b><p>Brief-ul, publicul, genul, stilul și obiectivul ghidează fiecare etapă.</p><span class='ss-priority-tag'>BARĂ GHIDATĂ</span></div><div class='ss-priority'><div class='ss-priority-icon'>🧠</div><b>Cuprins studiat</b><p>Cercetare preliminară, structură profesională, evaluare editorială și îmbunătățiri țintite.</p><span class='ss-priority-tag'>STRUCTURĂ</span></div><div class='ss-priority'><div class='ss-priority-icon'>✍️</div><b>Scriere controlabilă</b><p>Generează o secțiune, un capitol sau întreaga carte și modifică doar ce alegi.</p><span class='ss-priority-tag'>TEXT</span></div><div class='ss-priority'><div class='ss-priority-icon'>🔍</div><b>Calitate și originalitate</b><p>Verificări de coerență, completitudine, surse și similitudini înainte de export.</p><span class='ss-priority-tag'>REVIZUIRE</span></div></div><div class='ss-section'><h2>Proiectul tău rămâne recuperabil</h2><p class='ss-muted'>Salvează manual sesiunea, exportă un CSV complet și reia lucrul oricând.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 Import și export</b>CSV complet cu bara laterală, cuprins, texte, surse și imagini.</div><div class='ss-benefit'><b>🔊 Previziualizare și cititor vocal</b>Citește, ascultă, întrerupe și reia manuscrisul în browser.</div><div class='ss-benefit'><b>📄 Word, PDF și KDP</b>Pregătește manuscrisul pentru revizie, tipar sau publicare.</div></div><div class='ss-section'><h2>Întrebări frecvente</h2><p class='ss-muted'>Creditele sunt folosite doar pentru prelucrări IA; citirea, modificările manuale, CSV și exportul rămân gratuite. Cartea nu se publică automat.</p></div>""",
        "packages": "Pachete de credite clare", "package_sub": "Alege pachetul pentru proiectul tău. Estimările sunt prudente și includ spațiu pentru verificări.", "credit_word": "credite",
        "package_hints": ["Pentru a testa funcțiile principale.", "Pentru un prim proiect complet.", "Pentru mai multe ghiduri sau Test Prep.", "Pentru activitate editorială continuă.", "Pentru cataloage și utilizare profesională."],
    },
    "Русский": {
        "community": "Наше сообщество", "version": "Версия приложения",
        "body": """<div class='ss-section'><h2>От идеи до книги — с реальным контролем</h2><p class='ss-muted'>Заполните боковую панель, создайте продуманный план, развивайте текст и решайте каждое изменение.</p></div><div class='ss-priority-grid'><div class='ss-priority'><div class='ss-priority-icon'>🧭</div><b>Индивидуальный проект</b><p>Бриф, аудитория, жанр, стиль и цель направляют каждый этап книги.</p><span class='ss-priority-tag'>ПАНЕЛЬ</span></div><div class='ss-priority'><div class='ss-priority-icon'>🧠</div><b>Продуманный план</b><p>Предварительное исследование, профессиональная структура и целевые улучшения.</p><span class='ss-priority-tag'>СТРУКТУРА</span></div><div class='ss-priority'><div class='ss-priority-icon'>✍️</div><b>Управляемый текст</b><p>Создавайте раздел, главу или всю книгу и изменяйте только выбранное.</p><span class='ss-priority-tag'>ТЕКСТ</span></div><div class='ss-priority'><div class='ss-priority-icon'>🔍</div><b>Качество и оригинальность</b><p>Проверки связности, полноты, источников и возможных совпадений перед экспортом.</p><span class='ss-priority-tag'>ПРОВЕРКА</span></div></div><div class='ss-section'><h2>Проект можно восстановить</h2><p class='ss-muted'>Сохраняйте сессию вручную, экспортируйте полный CSV и продолжайте работу в любое время.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 Импорт и экспорт</b>Полный CSV с панелью, планом, текстами, источниками и изображениями.</div><div class='ss-benefit'><b>🔊 Предпросмотр и чтение вслух</b>Читайте, слушайте, ставьте на паузу и продолжайте в браузере.</div><div class='ss-benefit'><b>📄 Word, PDF и KDP</b>Подготовьте рукопись к редактированию, печати или публикации.</div></div><div class='ss-section'><h2>Частые вопросы</h2><p class='ss-muted'>Кредиты используются только для ИИ; чтение, ручное редактирование, CSV и экспорт бесплатны. Книга никогда не публикуется автоматически.</p></div>""",
        "packages": "Понятные пакеты кредитов", "package_sub": "Выберите пакет для своего проекта. Оценки осторожны и включают запас на проверки.", "credit_word": "кредитов",
        "package_hints": ["Чтобы попробовать основные функции.", "Для первого полного проекта.", "Для нескольких руководств или Test Prep.", "Для постоянной редакционной работы.", "Для каталогов и профессионального использования."],
    },
    "العربية": {
        "community": "مجتمعنا", "version": "إصدار التطبيق",
        "body": """<div class='ss-section'><h2>من الفكرة إلى الكتاب، بتحكم حقيقي</h2><p class='ss-muted'>أكمل الشريط الجانبي، أنشئ فهرساً مدروساً، طوّر النص وقرر كل تعديل بنفسك.</p></div><div class='ss-priority-grid'><div class='ss-priority'><div class='ss-priority-icon'>🧭</div><b>مشروع مخصص</b><p>الملخص والجمهور والنوع والأسلوب والهدف توجه كل مرحلة من الكتاب.</p><span class='ss-priority-tag'>شريط موجه</span></div><div class='ss-priority'><div class='ss-priority-icon'>🧠</div><b>فهرس مدروس</b><p>بحث أولي وبنية احترافية وتقييم تحريري وتحسينات موجهة.</p><span class='ss-priority-tag'>البنية</span></div><div class='ss-priority'><div class='ss-priority-icon'>✍️</div><b>كتابة قابلة للتحكم</b><p>أنشئ قسماً أو فصلاً أو الكتاب كاملاً وعدّل فقط ما تختاره.</p><span class='ss-priority-tag'>النص</span></div><div class='ss-priority'><div class='ss-priority-icon'>🔍</div><b>الجودة والأصالة</b><p>فحوص للاتساق والاكتمال والمصادر والتشابهات المحتملة قبل التصدير.</p><span class='ss-priority-tag'>مراجعة</span></div></div><div class='ss-section'><h2>يمكن استعادة مشروعك دائماً</h2><p class='ss-muted'>احفظ الجلسة يدوياً وصدّر ملف CSV كاملاً واستأنف العمل متى شئت.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 استيراد وتصدير</b>CSV كامل للشريط الجانبي والفهرس والنصوص والمصادر والصور.</div><div class='ss-benefit'><b>🔊 معاينة وقارئ صوتي</b>اقرأ واستمع وأوقف واستأنف المخطوطة في المتصفح.</div><div class='ss-benefit'><b>📄 Word وPDF وKDP</b>جهّز المخطوطة للمراجعة أو الطباعة أو النشر.</div></div><div class='ss-section'><h2>أسئلة شائعة</h2><p class='ss-muted'>تُستخدم الأرصدة فقط لمعالجة الذكاء الاصطناعي؛ القراءة والتعديل اليدوي وCSV والتصدير مجانية. لا يُنشر الكتاب تلقائياً أبداً.</p></div>""",
        "packages": "باقات أرصدة واضحة", "package_sub": "اختر الباقة المناسبة لمشروعك. التقديرات حذرة وتشمل هامشاً للفحوص.", "credit_word": "رصيداً",
        "package_hints": ["لتجربة الوظائف الرئيسية.", "لأول مشروع كامل.", "لأدلة أو Test Prep متعددة.", "لعمل تحريري مستمر.", "للكتالوجات والاستخدام الاحترافي."],
    },
    "中文": {
        "community": "我们的社区", "version": "应用版本",
        "body": """<div class='ss-section'><h2>从想法到图书，始终掌控</h2><p class='ss-muted'>填写侧边栏，创建经过研究的目录，发展文本，并由你决定每一项修改。</p></div><div class='ss-priority-grid'><div class='ss-priority'><div class='ss-priority-icon'>🧭</div><b>量身定制的项目</b><p>简介、读者、类型、风格和目标指导图书的每一步。</p><span class='ss-priority-tag'>引导侧边栏</span></div><div class='ss-priority'><div class='ss-priority-icon'>🧠</div><b>经过研究的目录</b><p>前期研究、专业结构、编辑评分和有针对性的改进。</p><span class='ss-priority-tag'>结构</span></div><div class='ss-priority'><div class='ss-priority-icon'>✍️</div><b>可控写作</b><p>生成一个小节、一章或整本书，只修改你选择的部分。</p><span class='ss-priority-tag'>文本</span></div><div class='ss-priority'><div class='ss-priority-icon'>🔍</div><b>质量与原创性</b><p>导出前检查连贯性、完整性、来源和可能的相似性。</p><span class='ss-priority-tag'>审校</span></div></div><div class='ss-section'><h2>你的项目始终可恢复</h2><p class='ss-muted'>手动保存会话，导出完整 CSV，并可随时继续工作。</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 导入和导出</b>完整 CSV，包含侧边栏、目录、文本、来源和关联图片。</div><div class='ss-benefit'><b>🔊 预览与语音阅读器</b>直接在浏览器中阅读、聆听、暂停和继续书稿。</div><div class='ss-benefit'><b>📄 Word、PDF 和 KDP</b>为编辑、印刷或出版准备书稿。</div></div><div class='ss-section'><h2>常见问题</h2><p class='ss-muted'>积分仅用于 AI 处理；阅读、手动编辑、CSV 和导出免费。图书绝不会自动发布。</p></div>""",
        "packages": "清晰的积分套餐", "package_sub": "根据你的项目选择套餐。估算较为谨慎，并包含检查余量。", "credit_word": "积分",
        "package_hints": ["试用主要功能。", "完成第一个完整项目。", "制作多本指南或 Test Prep。", "持续进行编辑工作。", "目录与专业用途。"],
    },
}

HOME_PACKAGE_NAMES = {
    "Italiano": ("Prova", "Base", "Creator", "Studio", "Professionale"),
    "English": ("Try", "Base", "Creator", "Studio", "Professional"),
    "Español": ("Prueba", "Base", "Creator", "Studio", "Profesional"),
    "Français": ("Essai", "Base", "Creator", "Studio", "Professionnel"),
    "Deutsch": ("Test", "Basis", "Creator", "Studio", "Professionell"),
    "Română": ("Probă", "Bază", "Creator", "Studio", "Profesional"),
    "Русский": ("Пробный", "Базовый", "Creator", "Studio", "Профессиональный"),
    "العربية": ("تجربة", "أساسي", "Creator", "Studio", "احترافي"),
    "中文": ("试用", "基础", "创作者", "工作室", "专业版"),
}

# FAQ complete della home. Non viene tradotta al volo: ogni lingua ha testi
# curati e coerenti con le funzioni effettivamente disponibili nel software.
HOME_FAQ_COPY = {
    "Italiano": ("Domande frequenti", "Le informazioni essenziali prima di iniziare.", [
        ("Come funzionano i crediti?", "I crediti servono solo per elaborazioni IA: indice, scrittura, rigenerazioni e controlli. Prima di un'azione a consumo vedi il preventivo. Se i crediti terminano, il lavoro già creato resta leggibile, modificabile ed esportabile."),
        ("I miei dati e il mio libro sono privati?", "Ogni account mantiene separati crediti e progetto. Il manoscritto non viene pubblicato automaticamente. Usa una password personale e conserva un CSV dei progetti importanti."),
        ("Come salvo, recupero o trasferisco un progetto?", "Premi SALVA SESSIONE per conservarlo nel tuo account. Dopo un nuovo accesso l'editor parte pulito: premi RIAGGIORNA ALL'ULTIMA STESURA solo quando vuoi riaprire il progetto. Il CSV conserva sidebar, indice, testi, fonti e immagini per backup o trasferimento."),
        ("A cosa servono Word e PDF e come ricevo assistenza?", "Il CSV ripristina il progetto modificabile; Word serve per la revisione editoriale e PDF per lettura, stampa o condivisione. Per assistenza usa CONTATTI nella sidebar oppure entra nella Community."),
    ]),
    "English": ("Frequently asked questions", "Essential information before you start.", [
        ("How do credits work?", "Credits are used only for AI work: outline creation, writing, rewrites and checks. You see an estimate before a paid action. If credits run out, existing work remains readable, editable and exportable."),
        ("Are my data and book private?", "Each account keeps credits and projects separate. Your manuscript is never published automatically. Use a personal password and keep a CSV copy of important projects."),
        ("How do I save, restore or move a project?", "Select SAVE SESSION to store it in your account. After a new login the editor starts empty: select REFRESH TO THE LATEST DRAFT only when you want to reopen it. CSV keeps the sidebar, outline, text, sources and images for backup or transfer."),
        ("What are Word and PDF for, and how do I get help?", "CSV restores the editable project; Word is for editorial revision and PDF for reading, printing or sharing. For help, use CONTACTS in the sidebar or join the Community."),
    ]),
    "Español": ("Preguntas frecuentes", "Información esencial antes de empezar.", [
        ("¿Cómo funcionan los créditos?", "Los créditos se usan solo para tareas de IA: índice, redacción, regeneraciones y controles. Verás una estimación antes de cada acción de pago. Si se terminan, el trabajo creado sigue siendo legible, editable y exportable."),
        ("¿Mis datos y mi libro son privados?", "Cada cuenta mantiene separados los créditos y los proyectos. El manuscrito nunca se publica automáticamente. Usa una contraseña personal y conserva un CSV de los proyectos importantes."),
        ("¿Cómo guardo, recupero o traslado un proyecto?", "Pulsa GUARDAR SESIÓN para conservarlo en tu cuenta. Tras un nuevo acceso el editor empieza vacío: pulsa ACTUALIZAR AL ÚLTIMO BORRADOR solo cuando quieras reabrirlo. El CSV guarda barra lateral, índice, textos, fuentes e imágenes."),
        ("¿Para qué sirven Word y PDF y cómo recibo ayuda?", "El CSV restaura el proyecto editable; Word sirve para revisión editorial y PDF para leer, imprimir o compartir. Para ayuda, usa CONTACTOS en la barra lateral o entra en la Comunidad."),
    ]),
    "Français": ("Questions fréquentes", "Les informations essentielles avant de commencer.", [
        ("Comment fonctionnent les crédits ?", "Les crédits sont utilisés seulement pour l'IA : plan, rédaction, réécritures et contrôles. Une estimation est affichée avant toute action payante. Si les crédits sont épuisés, le travail créé reste lisible, modifiable et exportable."),
        ("Mes données et mon livre sont-ils privés ?", "Chaque compte conserve séparément ses crédits et ses projets. Le manuscrit n'est jamais publié automatiquement. Utilisez un mot de passe personnel et gardez une copie CSV des projets importants."),
        ("Comment sauvegarder, restaurer ou déplacer un projet ?", "Choisissez SAUVEGARDER LA SESSION pour le conserver dans votre compte. Après une nouvelle connexion, l'éditeur démarre vide : choisissez ACTUALISER LA DERNIÈRE VERSION seulement pour le rouvrir. Le CSV contient la barre latérale, le plan, les textes, sources et images."),
        ("À quoi servent Word et PDF, et comment obtenir de l'aide ?", "Le CSV restaure le projet modifiable ; Word sert à la révision éditoriale et PDF à la lecture, l'impression ou au partage. Pour obtenir de l'aide, utilisez CONTACTS dans la barre latérale ou rejoignez la Community."),
    ]),
    "Deutsch": ("Häufige Fragen", "Die wichtigsten Informationen vor dem Start.", [
        ("Wie funktionieren Credits?", "Credits werden nur für KI-Arbeit genutzt: Inhaltsverzeichnis, Schreiben, Überarbeitungen und Prüfungen. Vor jeder kostenpflichtigen Aktion sehen Sie eine Schätzung. Bei fehlenden Credits bleibt vorhandene Arbeit lesbar, bearbeitbar und exportierbar."),
        ("Sind meine Daten und mein Buch privat?", "Jedes Konto hält Credits und Projekte getrennt. Das Manuskript wird nie automatisch veröffentlicht. Verwenden Sie ein persönliches Passwort und bewahren Sie eine CSV-Kopie wichtiger Projekte auf."),
        ("Wie speichere, stelle ich wieder her oder übertrage ein Projekt?", "Wählen Sie SITZUNG SPEICHERN, um es im Konto abzulegen. Nach einer neuen Anmeldung startet der Editor leer: wählen Sie LETZTEN ENTWURF LADEN nur zum erneuten Öffnen. CSV enthält Seitenleiste, Inhaltsverzeichnis, Texte, Quellen und Bilder."),
        ("Wofür sind Word und PDF gedacht und wie erhalte ich Hilfe?", "CSV stellt das bearbeitbare Projekt wieder her; Word dient der redaktionellen Überarbeitung und PDF dem Lesen, Drucken oder Teilen. Hilfe erhalten Sie über KONTAKTE in der Seitenleiste oder die Community."),
    ]),
    "Română": ("Întrebări frecvente", "Informațiile esențiale înainte de începere.", [
        ("Cum funcționează creditele?", "Creditele sunt folosite doar pentru IA: cuprins, redactare, rescrieri și verificări. Vezi o estimare înainte de fiecare acțiune cu plată. Dacă se termină, lucrarea creată rămâne lizibilă, editabilă și exportabilă."),
        ("Datele și cartea mea sunt private?", "Fiecare cont păstrează separat creditele și proiectele. Manuscrisul nu este publicat automat. Folosește o parolă personală și păstrează un CSV al proiectelor importante."),
        ("Cum salvez, restaurez sau mut un proiect?", "Apasă SALVEAZĂ SESIUNEA pentru a-l păstra în cont. După o autentificare nouă, editorul pornește gol: apasă REÎNCARCĂ ULTIMA VERSIUNE doar pentru a-l redeschide. CSV păstrează bara laterală, cuprinsul, textele, sursele și imaginile."),
        ("La ce folosesc Word și PDF și cum primesc ajutor?", "CSV restaurează proiectul editabil; Word este pentru revizie editorială, iar PDF pentru citire, tipărire sau distribuire. Pentru ajutor, folosește CONTACTE din bara laterală sau Community."),
    ]),
    "Русский": ("Частые вопросы", "Основная информация перед началом работы.", [
        ("Как работают кредиты?", "Кредиты используются только для работы ИИ: плана, написания, переработки и проверок. Перед платным действием показывается расчёт. Когда кредиты закончатся, созданная работа останется доступной для чтения, редактирования и экспорта."),
        ("Мои данные и книга конфиденциальны?", "У каждого аккаунта отдельно хранятся кредиты и проекты. Рукопись никогда не публикуется автоматически. Используйте личный пароль и храните CSV-копии важных проектов."),
        ("Как сохранить, восстановить или перенести проект?", "Нажмите СОХРАНИТЬ СЕССИЮ, чтобы сохранить проект в аккаунте. После нового входа редактор пуст: нажимайте ЗАГРУЗИТЬ ПОСЛЕДНЮЮ ВЕРСИЮ, только когда хотите открыть проект. CSV содержит панель, план, тексты, источники и изображения."),
        ("Для чего нужны Word и PDF и как получить помощь?", "CSV восстанавливает редактируемый проект; Word служит для редакторской правки, PDF — для чтения, печати или отправки. Для помощи используйте КОНТАКТЫ на боковой панели или Community."),
    ]),
    "العربية": ("الأسئلة الشائعة", "المعلومات الأساسية قبل البدء.", [
        ("كيف تعمل الأرصدة؟", "تُستخدم الأرصدة فقط لعمليات الذكاء الاصطناعي: الفهرس والكتابة وإعادة الصياغة والفحوص. سترى تقديراً قبل كل عملية مدفوعة. عند نفاد الأرصدة يبقى العمل الذي أنشأته قابلاً للقراءة والتعديل والتصدير."),
        ("هل بياناتي وكتابي خاصان؟", "يحتفظ كل حساب بأرصدة ومشروعات منفصلة. لا تُنشر المخطوطة تلقائياً أبداً. استخدم كلمة مرور شخصية واحتفظ بنسخة CSV من المشروعات المهمة."),
        ("كيف أحفظ مشروعاً أو أستعيده أو أنقله؟", "اضغط حفظ الجلسة للاحتفاظ به في حسابك. بعد تسجيل دخول جديد يبدأ المحرر فارغاً: اضغط تحديث إلى آخر مسودة فقط عندما تريد فتحه. يحفظ CSV الشريط الجانبي والفهرس والنصوص والمصادر والصور."),
        ("ما فائدة Word وPDF وكيف أحصل على المساعدة؟", "يعيد CSV المشروع القابل للتعديل؛ Word للمراجعة التحريرية وPDF للقراءة أو الطباعة أو المشاركة. للمساعدة استخدم جهات الاتصال في الشريط الجانبي أو Community."),
    ]),
    "中文": ("常见问题", "开始前需要了解的关键信息。", [
        ("积分如何使用？", "积分仅用于 AI 操作：目录、写作、重写和检查。每次付费操作前都会显示预估。积分用完后，已有内容仍可阅读、编辑和导出。"),
        ("我的数据和图书是否私密？", "每个账户的积分和项目彼此独立。书稿绝不会被自动发布。请使用个人密码，并保留重要项目的 CSV 副本。"),
        ("如何保存、恢复或转移项目？", "选择保存会话即可保存在账户中。重新登录后编辑器为空：仅在需要重新打开项目时选择加载最新草稿。CSV 保存侧边栏、目录、文本、来源和图片。"),
        ("Word 和 PDF 有什么用途，如何获得帮助？", "CSV 可恢复可编辑项目；Word 用于编辑修订，PDF 用于阅读、打印或分享。需要帮助时，请使用侧边栏中的联系人或 Community。"),
    ]),
}

# Sezioni editoriali estese della home. Mantengono la presentazione completa
# anche dopo la localizzazione: demo, destinatari, percorso, esempi, strumenti
# e archivio vengono mostrati nella lingua selezionata.
HOME_RICH_COPY = {
    "Italiano": """<div class='ss-section'><h2>Da un'idea a un libro: un esempio concreto</h2><p class='ss-muted'>La sidebar diventa indice, poi un manoscritto modificabile: ogni passaggio resta visibile e sotto il tuo controllo.</p></div><div class='ss-proof'><div class='ss-proof-top'><b>Demo di un progetto editoriale</b><span class='ss-proof-label'>ESEMPIO</span></div><div class='ss-proof-grid'><div class='ss-proof-index'><b>1. SIDEBAR COMPILATA</b><span><strong>Titolo:</strong> Yoga per il benessere</span><span><strong>Genere:</strong> Meditazione / Mindfulness</span><span><strong>Obiettivo:</strong> creare una pratica quotidiana</span><span class='active'>2. INDICE: capitoli e sottocapitoli ordinati</span></div><div class='ss-proof-page'><small>3. MANOSCRITTO GENERATO E MODIFICABILE</small><h3>Creare una routine che dura</h3><p>Correggi, rigenera una sola parte, ascolta e verifica la coerenza prima dell'esportazione.</p><div class='ss-proof-lines'><i></i><i></i><i></i></div></div></div></div><div class='ss-section'><h2>Per chi è Scrittore Site</h2><p class='ss-muted'>Non serve esperienza tecnica: scegli il punto da cui vuoi partire.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>🌱 Autori esordienti</strong>Trasforma un'idea in una struttura ordinata e modificabile.</div><div class='ss-step'><strong>🛠️ Professionisti e formatori</strong>Organizza competenze e procedure in manuali, guide e percorsi didattici.</div><div class='ss-step'><strong>🎓 Docenti e Test Prep</strong>Crea teoria, quiz, simulazioni e soluzioni commentate mantenendo il controllo.</div></div><div class='ss-section'><h2>Come funziona</h2><p class='ss-muted'>Un percorso semplice, senza perdere il controllo editoriale.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>1. Definisci il progetto</strong>Titolo, lingua, pubblico, genere, obiettivo e approfondimenti.</div><div class='ss-step'><strong>2. Crea e migliora</strong>Genera l'indice, valutalo e sviluppa sezioni, capitoli o libro completo.</div><div class='ss-step'><strong>3. Controlla e salva</strong>Anteprima, lettore vocale, verifiche, salvataggio volontario e export.</div></div><div class='ss-section'><h2>Esempi di progetti</h2><p class='ss-muted'>Titolo, tono e contenuti restano sempre scelti da te.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>🧘 Benessere</b>Guide su yoga, mindfulness e abitudini quotidiane.</div><div class='ss-benefit'><b>🧪 Manuali tecnici</b>Procedure, esempi, controlli e avvertenze.</div><div class='ss-benefit'><b>📚 Test Prep</b>Teoria, quiz, simulazioni e soluzioni separate.</div><div class='ss-benefit'><b>✨ Narrativa</b>Personaggi, conflitto e conclusione coerente.</div></div><div class='ss-section'><h2>Tutte le funzioni, senza complessità</h2><p class='ss-muted'>Strumenti concreti per progettare, scrivere, revisionare, ascoltare e preparare il manoscritto.</p></div><div class='ss-priority-grid'><div class='ss-feature-group'><h3>🧭 Progetta</h3><p><strong>Brief, fonti e indice</strong><br>Sidebar guidata, dossier delle fonti e indice professionale con voto e rigenerazione.</p></div><div class='ss-feature-group'><h3>✍️ Scrivi e modifica</h3><p><strong>Sezione, capitolo o libro</strong><br>Rigenerazione mirata, quiz, ricette, Test Prep e ricerca/sostituzione globale.</p></div><div class='ss-feature-group'><h3>🔎 Controlla e pubblica</h3><p><strong>Qualità e originalità</strong><br>Coerenza, fatti, copyright, anteprima vocale, Word, PDF e formattazione KDP.</p></div></div><div class='ss-section'><h2>Importa / Esporta: il progetto è sempre nelle tue mani</h2><p class='ss-muted'>CSV salva e ripristina il progetto completo, mentre Word e PDF servono per revisione e lettura.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📥 Esporta CSV completo</b>Sidebar, indice, testi, fonti e immagini in una copia portabile.</div><div class='ss-benefit'><b>📤 Importa e riprendi</b>Riapri un CSV di Scrittore Site e controlla il risultato prima di salvare.</div><div class='ss-benefit'><b>💾 Salva quando vuoi</b>Il progetto viene conservato solo quando premi SALVA SESSIONE.</div></div><div class='ss-section'><h2>Crediti chiari, controllo totale</h2></div><div class='ss-credit-note'>I crediti vengono usati solo per le elaborazioni IA. Le funzioni gratuite includono lettura, modifiche manuali, CSV, Word e PDF.</div><div class='ss-trust'>Il libro non viene mai pubblicato automaticamente: decidi sempre tu cosa modificare, esportare o pubblicare.</div>""",
    "English": """<div class='ss-section'><h2>From an idea to a book: a real example</h2><p class='ss-muted'>The sidebar becomes an outline, then an editable manuscript: every step remains visible and under your control.</p></div><div class='ss-proof'><div class='ss-proof-top'><b>Editorial project demo</b><span class='ss-proof-label'>EXAMPLE</span></div><div class='ss-proof-grid'><div class='ss-proof-index'><b>1. COMPLETED SIDEBAR</b><span><strong>Title:</strong> Yoga for wellbeing</span><span><strong>Genre:</strong> Meditation / Mindfulness</span><span><strong>Goal:</strong> build a daily practice</span><span class='active'>2. OUTLINE: ordered chapters and sections</span></div><div class='ss-proof-page'><small>3. GENERATED, EDITABLE MANUSCRIPT</small><h3>Building a lasting routine</h3><p>Revise, rewrite one part, listen and check consistency before exporting.</p><div class='ss-proof-lines'><i></i><i></i><i></i></div></div></div></div><div class='ss-section'><h2>Who Scrittore Site is for</h2><p class='ss-muted'>No technical experience is required: choose your starting point.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>🌱 First-time authors</strong>Turn an idea into an organized, editable structure.</div><div class='ss-step'><strong>🛠️ Professionals and trainers</strong>Organize expertise and procedures into manuals, guides and learning paths.</div><div class='ss-step'><strong>🎓 Teachers and Test Prep creators</strong>Create theory, quizzes, simulations and explained answers while staying in control.</div></div><div class='ss-section'><h2>How it works</h2><p class='ss-muted'>A straightforward path without giving up editorial control.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>1. Define the project</strong>Title, language, audience, genre, goal and depth.</div><div class='ss-step'><strong>2. Create and improve</strong>Generate and assess the outline, then develop sections, chapters or the whole book.</div><div class='ss-step'><strong>3. Review and save</strong>Preview, voice reader, checks, voluntary saving and export.</div></div><div class='ss-section'><h2>Project examples</h2><p class='ss-muted'>You always choose the title, voice and content.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>🧘 Wellbeing</b>Guides about yoga, mindfulness and daily habits.</div><div class='ss-benefit'><b>🧪 Technical manuals</b>Procedures, examples, checks and warnings.</div><div class='ss-benefit'><b>📚 Test Prep</b>Theory, quizzes, simulations and separate answers.</div><div class='ss-benefit'><b>✨ Fiction</b>Characters, conflict and a coherent ending.</div></div><div class='ss-section'><h2>All the features, without complexity</h2><p class='ss-muted'>Practical tools to plan, write, revise, listen to and prepare a manuscript.</p></div><div class='ss-priority-grid'><div class='ss-feature-group'><h3>🧭 Plan</h3><p><strong>Brief, sources and outline</strong><br>Guided sidebar, source dossier and professional outline with score and rewrite.</p></div><div class='ss-feature-group'><h3>✍️ Write and edit</h3><p><strong>Section, chapter or book</strong><br>Targeted rewriting, quizzes, recipes, Test Prep and global search/replace.</p></div><div class='ss-feature-group'><h3>🔎 Review and publish</h3><p><strong>Quality and originality</strong><br>Consistency, facts, copyright, voice preview, Word, PDF and KDP formatting.</p></div></div><div class='ss-section'><h2>Import / Export: your project stays in your hands</h2><p class='ss-muted'>CSV saves and restores the complete project; Word and PDF are for revision and reading.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📥 Export a complete CSV</b>Sidebar, outline, text, sources and images in a portable copy.</div><div class='ss-benefit'><b>📤 Import and resume</b>Open a Scrittore Site CSV and review it before saving.</div><div class='ss-benefit'><b>💾 Save when you choose</b>The project is stored only when you select SAVE SESSION.</div></div><div class='ss-section'><h2>Clear credits, total control</h2></div><div class='ss-credit-note'>Credits are used only for AI work. Reading, manual edits, CSV, Word and PDF remain free.</div><div class='ss-trust'>Your book is never published automatically: you always decide what to revise, export or publish.</div>""",
}

HOME_RICH_COPY.update({
    "Español": """<div class='ss-section'><h2>De una idea a un libro: un ejemplo real</h2><p class='ss-muted'>La barra lateral se convierte en índice y después en un manuscrito editable: cada paso está visible y bajo tu control.</p></div><div class='ss-proof'><div class='ss-proof-top'><b>Demo de proyecto editorial</b><span class='ss-proof-label'>EJEMPLO</span></div><div class='ss-proof-grid'><div class='ss-proof-index'><b>1. BARRA LATERAL COMPLETADA</b><span><strong>Título:</strong> Yoga para el bienestar</span><span><strong>Género:</strong> Meditación / Mindfulness</span><span class='active'>2. ÍNDICE: capítulos y secciones ordenados</span></div><div class='ss-proof-page'><small>3. MANUSCRITO EDITABLE</small><h3>Crear una rutina duradera</h3><p>Corrige, regenera una parte, escucha y verifica antes de exportar.</p><div class='ss-proof-lines'><i></i><i></i><i></i></div></div></div></div><div class='ss-section'><h2>Para quién es Scrittore Site</h2><p class='ss-muted'>No necesitas experiencia técnica.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>🌱 Autores principiantes</strong>Convierte una idea en una estructura editable.</div><div class='ss-step'><strong>🛠️ Profesionales y formadores</strong>Organiza conocimientos y procedimientos en guías y manuales.</div><div class='ss-step'><strong>🎓 Docentes y Test Prep</strong>Crea teoría, cuestionarios, simulaciones y soluciones.</div></div><div class='ss-section'><h2>Cómo funciona</h2><p class='ss-muted'>Define el proyecto, crea y mejora el contenido, después revísalo, guárdalo y expórtalo.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>1. Define</strong>Título, idioma, público, género y objetivo.</div><div class='ss-step'><strong>2. Crea</strong>Índice, secciones, capítulos o libro completo.</div><div class='ss-step'><strong>3. Controla</strong>Vista previa, lector de voz, verificaciones y exportación.</div></div><div class='ss-section'><h2>Ejemplos y herramientas</h2><p class='ss-muted'>Bienestar, manuales técnicos, Test Prep y narrativa. Incluye fuentes, índice, escritura, controles de coherencia y originalidad, búsqueda global, voz, Word, PDF y KDP.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 Importar y exportar</b>CSV completo con barra lateral, índice, textos, fuentes e imágenes.</div><div class='ss-benefit'><b>💾 Guardado voluntario</b>El proyecto se guarda solo al pulsar GUARDAR SESIÓN.</div><div class='ss-benefit'><b>📄 Word, PDF y KDP</b>Prepara el manuscrito para revisión, lectura, impresión o publicación.</div></div><div class='ss-credit-note'>Los créditos se usan solo para acciones de IA. Lectura, cambios manuales, CSV, Word y PDF son gratuitos.</div><div class='ss-trust'>Tu libro nunca se publica automáticamente: tú decides qué modificar, exportar o publicar.</div>""",
    "Français": """<div class='ss-section'><h2>De l'idée au livre : un exemple concret</h2><p class='ss-muted'>La barre latérale devient un plan, puis un manuscrit modifiable : chaque étape reste visible et sous votre contrôle.</p></div><div class='ss-proof'><div class='ss-proof-top'><b>Démo d'un projet éditorial</b><span class='ss-proof-label'>EXEMPLE</span></div><div class='ss-proof-grid'><div class='ss-proof-index'><b>1. BARRE LATÉRALE REMPLIE</b><span><strong>Titre :</strong> Yoga pour le bien-être</span><span><strong>Genre :</strong> Méditation / Mindfulness</span><span class='active'>2. PLAN : chapitres et sections ordonnés</span></div><div class='ss-proof-page'><small>3. MANUSCRIT MODIFIABLE</small><h3>Créer une routine durable</h3><p>Corrigez, réécrivez une partie, écoutez et vérifiez avant l'export.</p><div class='ss-proof-lines'><i></i><i></i><i></i></div></div></div></div><div class='ss-section'><h2>À qui s'adresse Scrittore Site</h2><p class='ss-muted'>Aucune expérience technique n'est nécessaire.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>🌱 Nouveaux auteurs</strong>Transformez une idée en structure modifiable.</div><div class='ss-step'><strong>🛠️ Professionnels et formateurs</strong>Organisez compétences et procédures en guides et manuels.</div><div class='ss-step'><strong>🎓 Enseignants et Test Prep</strong>Créez théorie, quiz, simulations et corrigés.</div></div><div class='ss-section'><h2>Comment cela fonctionne</h2><p class='ss-muted'>Définissez le projet, créez et améliorez le contenu, puis contrôlez, sauvegardez et exportez.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>1. Définir</strong>Titre, langue, public, genre et objectif.</div><div class='ss-step'><strong>2. Créer</strong>Plan, sections, chapitres ou livre complet.</div><div class='ss-step'><strong>3. Contrôler</strong>Aperçu, lecteur vocal, vérifications et export.</div></div><div class='ss-section'><h2>Exemples et outils</h2><p class='ss-muted'>Bien-être, manuels techniques, Test Prep et fiction. Sources, plan, rédaction, cohérence, originalité, recherche globale, voix, Word, PDF et KDP.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 Importer et exporter</b>CSV complet avec barre latérale, plan, textes, sources et images.</div><div class='ss-benefit'><b>💾 Sauvegarde volontaire</b>Le projet est enregistré seulement avec SAUVEGARDER LA SESSION.</div><div class='ss-benefit'><b>📄 Word, PDF et KDP</b>Préparez le manuscrit pour relecture, lecture, impression ou publication.</div></div><div class='ss-credit-note'>Les crédits servent seulement aux actions IA. Lecture, modifications manuelles, CSV, Word et PDF sont gratuits.</div><div class='ss-trust'>Votre livre n'est jamais publié automatiquement : vous décidez quoi modifier, exporter ou publier.</div>""",
    "Deutsch": """<div class='ss-section'><h2>Von der Idee zum Buch: ein konkretes Beispiel</h2><p class='ss-muted'>Die Seitenleiste wird zur Gliederung und dann zum bearbeitbaren Manuskript: jeder Schritt bleibt sichtbar und unter Ihrer Kontrolle.</p></div><div class='ss-proof'><div class='ss-proof-top'><b>Demo eines redaktionellen Projekts</b><span class='ss-proof-label'>BEISPIEL</span></div><div class='ss-proof-grid'><div class='ss-proof-index'><b>1. AUSGEFÜLLTE SEITENLEISTE</b><span><strong>Titel:</strong> Yoga für Wohlbefinden</span><span><strong>Genre:</strong> Meditation / Achtsamkeit</span><span class='active'>2. GLIEDERUNG: geordnete Kapitel und Abschnitte</span></div><div class='ss-proof-page'><small>3. BEARBEITBARES MANUSKRIPT</small><h3>Eine dauerhafte Routine schaffen</h3><p>Korrigieren, einen Teil neu schreiben, anhören und vor dem Export prüfen.</p><div class='ss-proof-lines'><i></i><i></i><i></i></div></div></div></div><div class='ss-section'><h2>Für wen ist Scrittore Site</h2><p class='ss-muted'>Technische Erfahrung ist nicht erforderlich.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>🌱 Neue Autoren</strong>Verwandeln Sie eine Idee in eine bearbeitbare Struktur.</div><div class='ss-step'><strong>🛠️ Fachleute und Trainer</strong>Ordnen Sie Wissen und Verfahren in Leitfäden und Handbüchern.</div><div class='ss-step'><strong>🎓 Lehrende und Test Prep</strong>Erstellen Sie Theorie, Quiz, Simulationen und Lösungen.</div></div><div class='ss-section'><h2>So funktioniert es</h2><p class='ss-muted'>Projekt definieren, Inhalte erstellen und verbessern, dann prüfen, speichern und exportieren.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>1. Definieren</strong>Titel, Sprache, Zielgruppe, Genre und Ziel.</div><div class='ss-step'><strong>2. Erstellen</strong>Gliederung, Abschnitte, Kapitel oder ganzes Buch.</div><div class='ss-step'><strong>3. Prüfen</strong>Vorschau, Sprachleser, Kontrollen und Export.</div></div><div class='ss-section'><h2>Beispiele und Werkzeuge</h2><p class='ss-muted'>Wellbeing, technische Handbücher, Test Prep und Belletristik. Quellen, Gliederung, Schreiben, Konsistenz, Originalität, globale Suche, Stimme, Word, PDF und KDP.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 Import und Export</b>Vollständiges CSV mit Seitenleiste, Gliederung, Texten, Quellen und Bildern.</div><div class='ss-benefit'><b>💾 Freiwillig speichern</b>Das Projekt wird nur mit SITZUNG SPEICHERN abgelegt.</div><div class='ss-benefit'><b>📄 Word, PDF und KDP</b>Bereiten Sie das Manuskript für Überarbeitung, Lesen, Druck oder Veröffentlichung vor.</div></div><div class='ss-credit-note'>Credits gelten nur für KI-Aktionen. Lesen, manuelle Änderungen, CSV, Word und PDF sind kostenlos.</div><div class='ss-trust'>Ihr Buch wird nie automatisch veröffentlicht: Sie entscheiden über Änderung, Export oder Veröffentlichung.</div>""",
    "Română": """<div class='ss-section'><h2>De la idee la carte: un exemplu concret</h2><p class='ss-muted'>Bara laterală devine cuprins, apoi manuscris editabil: fiecare pas rămâne vizibil și sub controlul tău.</p></div><div class='ss-proof'><div class='ss-proof-top'><b>Demonstrație de proiect editorial</b><span class='ss-proof-label'>EXEMPLU</span></div><div class='ss-proof-grid'><div class='ss-proof-index'><b>1. BARĂ LATERALĂ COMPLETATĂ</b><span><strong>Titlu:</strong> Yoga pentru bunăstare</span><span><strong>Gen:</strong> Meditație / Mindfulness</span><span class='active'>2. CUPRINS: capitole și secțiuni ordonate</span></div><div class='ss-proof-page'><small>3. MANUSCRIS EDITABIL</small><h3>O rutină care durează</h3><p>Corectează, rescrie o parte, ascultă și verifică înainte de export.</p><div class='ss-proof-lines'><i></i><i></i><i></i></div></div></div></div><div class='ss-section'><h2>Pentru cine este Scrittore Site</h2><p class='ss-muted'>Nu ai nevoie de experiență tehnică.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>🌱 Autori începători</strong>Transformă o idee într-o structură editabilă.</div><div class='ss-step'><strong>🛠️ Profesioniști și formatori</strong>Organizează cunoștințe și proceduri în ghiduri și manuale.</div><div class='ss-step'><strong>🎓 Profesori și Test Prep</strong>Creează teorie, quiz-uri, simulări și soluții.</div></div><div class='ss-section'><h2>Cum funcționează</h2><p class='ss-muted'>Definește proiectul, creează și îmbunătățește conținutul, apoi verifică, salvează și exportă.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>1. Definește</strong>Titlu, limbă, public, gen și obiectiv.</div><div class='ss-step'><strong>2. Creează</strong>Cuprins, secțiuni, capitole sau carte completă.</div><div class='ss-step'><strong>3. Verifică</strong>Previzualizare, cititor vocal, controale și export.</div></div><div class='ss-section'><h2>Exemple și instrumente</h2><p class='ss-muted'>Bunăstare, manuale tehnice, Test Prep și ficțiune. Surse, cuprins, scriere, coerență, originalitate, căutare globală, voce, Word, PDF și KDP.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 Import și export</b>CSV complet cu bară laterală, cuprins, texte, surse și imagini.</div><div class='ss-benefit'><b>💾 Salvare voluntară</b>Proiectul se salvează doar cu SALVEAZĂ SESIUNEA.</div><div class='ss-benefit'><b>📄 Word, PDF și KDP</b>Pregătește manuscrisul pentru revizie, citire, tipărire sau publicare.</div></div><div class='ss-credit-note'>Creditele sunt folosite doar pentru acțiuni IA. Citirea, modificările manuale, CSV, Word și PDF sunt gratuite.</div><div class='ss-trust'>Cartea nu se publică automat: tu decizi ce modifici, exporți sau publici.</div>""",
})

HOME_RICH_COPY.update({
    "Русский": """<div class='ss-section'><h2>От идеи к книге: реальный пример</h2><p class='ss-muted'>Боковая панель превращается в план, а затем в редактируемую рукопись: каждый этап виден и остаётся под вашим контролем.</p></div><div class='ss-proof'><div class='ss-proof-top'><b>Демо редакционного проекта</b><span class='ss-proof-label'>ПРИМЕР</span></div><div class='ss-proof-grid'><div class='ss-proof-index'><b>1. ЗАПОЛНЕННАЯ ПАНЕЛЬ</b><span><strong>Название:</strong> Йога для благополучия</span><span><strong>Жанр:</strong> Медитация / Mindfulness</span><span class='active'>2. ПЛАН: главы и разделы упорядочены</span></div><div class='ss-proof-page'><small>3. РЕДАКТИРУЕМАЯ РУКОПИСЬ</small><h3>Создание устойчивой практики</h3><p>Исправляйте, переписывайте часть текста, слушайте и проверяйте до экспорта.</p><div class='ss-proof-lines'><i></i><i></i><i></i></div></div></div></div><div class='ss-section'><h2>Для кого Scrittore Site</h2><p class='ss-muted'>Технический опыт не требуется.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>🌱 Начинающие авторы</strong>Превращайте идею в редактируемую структуру.</div><div class='ss-step'><strong>🛠️ Специалисты и преподаватели</strong>Организуйте знания и процедуры в руководства и пособия.</div><div class='ss-step'><strong>🎓 Преподаватели и Test Prep</strong>Создавайте теорию, тесты, симуляции и решения.</div></div><div class='ss-section'><h2>Как это работает</h2><p class='ss-muted'>Определите проект, создайте и улучшите содержание, затем проверьте, сохраните и экспортируйте.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>1. Определите</strong>Название, язык, аудиторию, жанр и цель.</div><div class='ss-step'><strong>2. Создайте</strong>План, разделы, главы или всю книгу.</div><div class='ss-step'><strong>3. Проверьте</strong>Предпросмотр, голосовое чтение, проверки и экспорт.</div></div><div class='ss-section'><h2>Примеры и инструменты</h2><p class='ss-muted'>Благополучие, технические руководства, Test Prep и художественная литература. Источники, план, написание, связность, оригинальность, глобальный поиск, голос, Word, PDF и KDP.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 Импорт и экспорт</b>Полный CSV с панелью, планом, текстами, источниками и изображениями.</div><div class='ss-benefit'><b>💾 Сохранение по выбору</b>Проект сохраняется только после нажатия СОХРАНИТЬ СЕССИЮ.</div><div class='ss-benefit'><b>📄 Word, PDF и KDP</b>Подготовьте рукопись к правке, чтению, печати или публикации.</div></div><div class='ss-credit-note'>Кредиты используются только для действий ИИ. Чтение, ручная правка, CSV, Word и PDF бесплатны.</div><div class='ss-trust'>Книга никогда не публикуется автоматически: вы сами решаете, что изменить, экспортировать или опубликовать.</div>""",
    "العربية": """<div class='ss-section'><h2>من الفكرة إلى الكتاب: مثال واقعي</h2><p class='ss-muted'>يتحول الشريط الجانبي إلى فهرس ثم إلى مخطوطة قابلة للتعديل: كل خطوة مرئية وتبقى تحت تحكمك.</p></div><div class='ss-proof'><div class='ss-proof-top'><b>عرض مشروع تحريري</b><span class='ss-proof-label'>مثال</span></div><div class='ss-proof-grid'><div class='ss-proof-index'><b>1. الشريط الجانبي مكتمل</b><span><strong>العنوان:</strong> اليوغا للعافية</span><span><strong>النوع:</strong> التأمل / اليقظة</span><span class='active'>2. الفهرس: فصول وأقسام مرتبة</span></div><div class='ss-proof-page'><small>3. مخطوطة قابلة للتعديل</small><h3>إنشاء ممارسة مستمرة</h3><p>صحح وأعد كتابة جزء واستمع وتحقق قبل التصدير.</p><div class='ss-proof-lines'><i></i><i></i><i></i></div></div></div></div><div class='ss-section'><h2>لمن يناسب Scrittore Site</h2><p class='ss-muted'>لا تحتاج إلى خبرة تقنية.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>🌱 مؤلفون مبتدئون</strong>حوّل الفكرة إلى بنية قابلة للتعديل.</div><div class='ss-step'><strong>🛠️ مهنيون ومدربون</strong>نظّم الخبرات والإجراءات في أدلة وكتيبات.</div><div class='ss-step'><strong>🎓 معلمون وTest Prep</strong>أنشئ نظرية واختبارات ومحاكاة وحلولاً.</div></div><div class='ss-section'><h2>كيف يعمل</h2><p class='ss-muted'>حدد المشروع وأنشئ المحتوى وحسّنه، ثم راجعه واحفظه وصدّره.</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>1. حدّد</strong>العنوان واللغة والجمهور والنوع والهدف.</div><div class='ss-step'><strong>2. أنشئ</strong>الفهرس أو الأقسام أو الفصول أو الكتاب كاملاً.</div><div class='ss-step'><strong>3. تحقّق</strong>المعاينة والقارئ الصوتي والفحوص والتصدير.</div></div><div class='ss-section'><h2>أمثلة وأدوات</h2><p class='ss-muted'>العافية والكتيبات التقنية وTest Prep والسرد. مصادر وفهرس وكتابة واتساق وأصالة وبحث شامل وصوت وWord وPDF وKDP.</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 استيراد وتصدير</b>CSV كامل للشريط والفهرس والنصوص والمصادر والصور.</div><div class='ss-benefit'><b>💾 حفظ اختياري</b>لا يُحفظ المشروع إلا عند الضغط على حفظ الجلسة.</div><div class='ss-benefit'><b>📄 Word وPDF وKDP</b>جهّز المخطوطة للمراجعة أو القراءة أو الطباعة أو النشر.</div></div><div class='ss-credit-note'>تُستخدم الأرصدة فقط لإجراءات الذكاء الاصطناعي. القراءة والتعديل اليدوي وCSV وWord وPDF مجانية.</div><div class='ss-trust'>لا يُنشر كتابك تلقائياً أبداً: أنت تقرر ما تعدله أو تصدره أو تنشره.</div>""",
    "中文": """<div class='ss-section'><h2>从想法到图书：一个真实示例</h2><p class='ss-muted'>侧边栏会变成目录，再变成可编辑书稿：每一步都清晰可见，并始终由你掌控。</p></div><div class='ss-proof'><div class='ss-proof-top'><b>编辑项目演示</b><span class='ss-proof-label'>示例</span></div><div class='ss-proof-grid'><div class='ss-proof-index'><b>1. 已填写侧边栏</b><span><strong>标题：</strong>瑜伽与身心健康</span><span><strong>类型：</strong>冥想 / 正念</span><span class='active'>2. 目录：章节与小节已整理</span></div><div class='ss-proof-page'><small>3. 可编辑书稿</small><h3>建立可持续的习惯</h3><p>修改、重写某一部分、聆听并在导出前检查。</p><div class='ss-proof-lines'><i></i><i></i><i></i></div></div></div></div><div class='ss-section'><h2>Scrittore Site 适合谁</h2><p class='ss-muted'>无需技术经验。</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>🌱 新作者</strong>将想法转化为可编辑的结构。</div><div class='ss-step'><strong>🛠️ 专业人士和培训师</strong>将知识和流程整理成指南和手册。</div><div class='ss-step'><strong>🎓 教师和 Test Prep 创作者</strong>创建理论、测验、模拟和答案。</div></div><div class='ss-section'><h2>如何使用</h2><p class='ss-muted'>定义项目，创建并改进内容，然后检查、保存和导出。</p></div><div class='ss-priority-grid'><div class='ss-step'><strong>1. 定义</strong>标题、语言、读者、类型和目标。</div><div class='ss-step'><strong>2. 创建</strong>目录、小节、章节或整本书。</div><div class='ss-step'><strong>3. 检查</strong>预览、语音阅读、检查和导出。</div></div><div class='ss-section'><h2>示例与工具</h2><p class='ss-muted'>健康、技术手册、Test Prep 和小说。包含来源、目录、写作、连贯性、原创性、全局搜索、语音、Word、PDF 和 KDP。</p></div><div class='ss-benefits'><div class='ss-benefit'><b>📦 导入和导出</b>包含侧边栏、目录、文本、来源和图片的完整 CSV。</div><div class='ss-benefit'><b>💾 自主保存</b>仅在选择保存会话时才保存项目。</div><div class='ss-benefit'><b>📄 Word、PDF 和 KDP</b>为编辑、阅读、打印或出版准备书稿。</div></div><div class='ss-credit-note'>积分仅用于 AI 操作。阅读、手动编辑、CSV、Word 和 PDF 均免费。</div><div class='ss-trust'>图书绝不会自动发布：由你决定修改、导出或发布什么。</div>""",
})


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


def carica_progetto_automatico() -> dict[str, Any]:
    """Recupera l'ultima bozza dell'account senza interrompere l'editor se la tabella non è ancora configurata."""
    user = st.session_state.get("commercial_user_context") or {}
    if _mode() == "demo" or not _supabase_ready() or not user.get("id"):
        return {}
    try:
        righe = _supabase(
            "GET",
            "rest/v1/writer_project_autosaves",
            params={
                "select": "snapshot,updated_at",
                "user_id": f"eq.{user['id']}",
                "limit": "1",
            },
        )
        if not righe:
            return {}
        snapshot = righe[0].get("snapshot")
        if isinstance(snapshot, dict):
            snapshot["_autosave_updated_at"] = righe[0].get("updated_at", "")
            return snapshot
    except Exception:
        # La funzione resta compatibile con installazioni che non hanno ancora
        # eseguito la migrazione del salvataggio automatico.
        return {}
    return {}


def salva_progetto_automatico(snapshot: dict[str, Any]) -> bool:
    """Salva l'ultima bozza dell'account mediante upsert, senza crediti né chiamate IA."""
    user = st.session_state.get("commercial_user_context") or {}
    if _mode() == "demo" or not _supabase_ready() or not user.get("id"):
        return False
    try:
        url = f"{_secret('SUPABASE_URL').rstrip('/')}/rest/v1/writer_project_autosaves"
        headers = {
            **_supabase_headers(),
            "Prefer": "resolution=merge-duplicates,return=minimal",
        }
        response = requests.post(
            url,
            headers=headers,
            params={"on_conflict": "user_id"},
            json={"user_id": user["id"], "snapshot": snapshot},
            timeout=20,
        )
        return bool(response.ok)
    except Exception:
        return False


def elimina_progetto_automatico() -> None:
    """Rimuove il salvataggio cloud dell'utente quando sceglie esplicitamente di azzerare il progetto."""
    user = st.session_state.get("commercial_user_context") or {}
    if _mode() == "demo" or not _supabase_ready() or not user.get("id"):
        return
    try:
        _supabase(
            "DELETE",
            "rest/v1/writer_project_autosaves",
            params={"user_id": f"eq.{user['id']}"},
        )
    except Exception:
        pass


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


def _apri_progetto_pulito_dopo_accesso() -> None:
    """Prepara un editor vuoto dopo un nuovo accesso.

    L'ultima stesura resta nel cloud, ma non viene mostrata né letta finché
    l'utente non preme esplicitamente “RIAGGIORNA ALL'ULTIMA STESURA”.
    """
    for chiave in list(st.session_state.keys()):
        if not chiave.startswith("commercial_"):
            del st.session_state[chiave]
    # Un reset di una sessione precedente non deve impedire il ripristino
    # manuale dell'utente dopo un nuovo accesso.
    st.session_state.pop("commercial_project_reset_requested", None)
    st.session_state["commercial_editor_avvio_pulito"] = True


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
          .ss-community-button {display:flex; align-items:center; justify-content:center; min-height:3.35rem; width:100%;
            margin-top:.75rem; padding:.7rem 1rem; box-sizing:border-box; border-radius:11px; background:#cf3345;
            color:#fff !important; font-size:1.08rem; font-weight:800; text-decoration:none !important;
            box-shadow:0 6px 14px rgba(207,51,69,.22); transition:background .18s ease, transform .18s ease}
          .ss-community-button:hover {background:#ad2435; color:#fff !important; transform:translateY(-1px)}
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
          .ss-priority-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px;margin:1.1rem 0 2.25rem}
          .ss-priority {position:relative;overflow:hidden;background:linear-gradient(145deg,#ffffff,#f2f8fd);border:1px solid #c8ddeb;border-radius:16px;padding:1.25rem 1.12rem;min-height:210px;box-shadow:0 10px 24px rgba(20,77,120,.08)}
          .ss-priority::after {content:'';position:absolute;width:105px;height:105px;border-radius:50%;right:-33px;bottom:-45px;background:rgba(22,137,232,.10)}
          .ss-priority-icon {font-size:1.72rem;margin-bottom:.75rem}.ss-priority b {display:block;color:#102a43;font-size:1.12rem;margin-bottom:.45rem}.ss-priority p {position:relative;z-index:1;margin:0;color:#486581;line-height:1.43;font-size:.93rem}
          .ss-priority-tag {display:inline-block;margin-top:.72rem;padding:.22rem .48rem;border-radius:99px;background:#e0f2fe;color:#1269ae;font-weight:800;font-size:.7rem}
          .ss-feature-group {background:rgba(255,255,255,.64);border:1px solid #d9e5f0;border-radius:14px;padding:1.1rem 1.05rem;height:100%}
          .ss-feature-group h3 {margin:0 0 .42rem;color:#1269ae;font-size:1.06rem}.ss-feature-group p {margin:.42rem 0;color:#486581;font-size:.9rem;line-height:1.38}
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
          @media (max-width:960px) {.ss-priority-grid{grid-template-columns:1fr 1fr}.ss-priority{min-height:0}}
          @media (max-width:760px) {section.main > div.block-container {padding:1rem 1rem 2.5rem !important}.ss-hero-copy {padding:1.5rem .4rem}.ss-title {font-size:4rem}.ss-proof-grid {grid-template-columns:1fr}.ss-proof-action {margin-left:0}.ss-benefits {grid-template-columns:1fr}.ss-benefit {border-right:0;border-bottom:1px solid #d9e5f0}.ss-benefit:last-child {border-bottom:0}.ss-creator {min-height:120px}.ss-language-wrap {margin:0}.ss-priority-grid{grid-template-columns:1fr}}
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
    C = HOME_BODY_COPY[home_language]
    direzione_home = "rtl" if home_language == "العربية" else "ltr"

    hero_copy, hero_visual = st.columns([0.42, 0.58], gap="large")
    with hero_copy:
        st.markdown(
            f"""<div class='ss-hero-copy'>
              <div class='ss-kicker'>{H['presenta']}</div>
              <div class='ss-version'>{C['version']}: {COMMERCIAL_VERSION}</div>
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
        st.markdown(
            f"<a class='ss-community-button' href='https://community-fdjf.vercel.app/' target='_blank' rel='noopener noreferrer'>{C['community']}</a>",
            unsafe_allow_html=True,
        )
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

    # Il corpo della home è localizzato integralmente, inclusi funzioni,
    # salvataggio, import/export, crediti e FAQ. La scelta lingua non cambia
    # né il libro né i dati dell'account.
    st.markdown(f"<div dir='{direzione_home}'>{C['body']}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div dir='{direzione_home}'>{HOME_RICH_COPY[home_language]}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='ss-section'><h2>{C['packages']}</h2><p class='ss-muted'>{C['package_sub']}</p></div>",
        unsafe_allow_html=True,
    )
    price_columns = st.columns(len(PACKAGES))
    nomi_pacchetti = HOME_PACKAGE_NAMES[home_language]
    for posizione, (column, (_, package)) in enumerate(zip(price_columns, PACKAGES.items())):
        price = f"€ {package['amount_cents'] / 100:.2f}".replace(".", ",")
        with column:
            st.markdown(
                f"<div class='ss-card'><h3>{nomi_pacchetti[posizione]}</h3>"
                f"<div class='ss-price'>{price}</div><p>{package['credits']} {C['credit_word']}</p>"
                f"<p>{C['package_hints'][posizione]}</p></div>",
                unsafe_allow_html=True,
            )

    faq_title, faq_subtitle, faq_items = HOME_FAQ_COPY[home_language]
    st.markdown(
        f"<div class='ss-section' dir='{direzione_home}'><h2>{faq_title}</h2>"
        f"<p class='ss-muted'>{faq_subtitle}</p></div>",
        unsafe_allow_html=True,
    )
    for posizione, (domanda, risposta) in enumerate(faq_items):
        with st.expander(domanda, expanded=False):
            st.write(risposta)
    return

    st.markdown("<div class='ss-section'><h2>Da un’idea a un libro: un esempio concreto</h2><p class='ss-muted'>La stessa idea passa dalla sidebar all’indice, poi diventa un manoscritto controllabile e modificabile.</p></div>", unsafe_allow_html=True)
    st.markdown(
        """<div class='ss-proof'>
          <div class='ss-proof-top'><span class='ss-dot'></span><span class='ss-dot'></span><span class='ss-dot'></span>
          <b>Demo di un progetto editoriale</b><span class='ss-proof-label'>ESEMPIO</span></div>
          <div class='ss-proof-grid'>
            <div class='ss-proof-index'><b>1. SIDEBAR COMPILATA</b>
              <span><strong>Titolo:</strong> Yoga per il benessere</span>
              <span><strong>Genere:</strong> Meditazione / Mindfulness</span>
              <span><strong>Obiettivo:</strong> creare una pratica quotidiana</span>
              <span class='active'>Lunghezza: Standard KDP</span>
              <span><strong>2. INDICE:</strong> capitoli e sottocapitoli ordinati</span>
            </div>
            <div class='ss-proof-page'>
              <div class='ss-proof-toolbar'><span class='ss-proof-pill'>Anteprima</span><span class='ss-proof-pill'>Capitolo 2</span><span class='ss-proof-action'>Testo in lettura</span></div>
              <small>3. MANOSCRITTO GENERATO E MODIFICABILE</small><h3>Creare una routine che dura</h3>
              <p>Il testo nasce dall’indice e dal brief. Puoi correggerlo, rigenerare soltanto una parte, ascoltarlo e verificare la coerenza prima dell’esportazione.</p>
              <div class='ss-proof-lines'><i></i><i></i><i></i><i></i></div>
              <div class='ss-proof-progress'><span>Sezioni completate</span><div><span></span></div><span>64%</span></div>
            </div>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div class='ss-section'><h2>Il tuo studio editoriale, in un unico spazio</h2>
        <p class='ss-muted'>Dall'idea alla bozza esportabile: ogni fase è guidata, modificabile e sotto il tuo controllo.</p></div>
        <div class='ss-priority-grid'>
          <div class='ss-priority'><div class='ss-priority-icon'>✍️</div><b>Scrivi il libro completo</b>
          <p>Genera prefazione, capitoli, sottocapitoli e ringraziamenti, oppure lavora su una singola sezione quando preferisci.</p><span class='ss-priority-tag'>IL CUORE DEL SOFTWARE</span></div>
          <div class='ss-priority'><div class='ss-priority-icon'>🧠</div><b>Indice studiato e verificato</b>
          <p>Ricerca preliminare delle fonti, indice professionale, voto editoriale e rigenerazione guidata dai miglioramenti suggeriti.</p><span class='ss-priority-tag'>STRUTTURA PIÙ SOLIDA</span></div>
          <div class='ss-priority'><div class='ss-priority-icon'>🔍</div><b>Qualità sotto controllo</b>
          <p>Controlli su coerenza, completezza, ripetizioni, finali tronchi e dati aggiornabili prima dell'esportazione.</p><span class='ss-priority-tag'>REVISIONE GUIDATA</span></div>
          <div class='ss-priority'><div class='ss-priority-icon'>💾</div><b>Il lavoro resta tuo</b>
          <p>Salva la sessione nel tuo account oppure scarica un archivio CSV completo: sidebar, indice, testi, fonti e immagini restano recuperabili.</p><span class='ss-priority-tag'>ARCHIVIO PORTABILE</span></div>
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

    st.markdown("<div class='ss-section'><h2>Per chi è Scrittore Site</h2><p class='ss-muted'>Non serve esperienza tecnica: scegli il punto da cui vuoi partire.</p></div>", unsafe_allow_html=True)
    pubblico_a, pubblico_b, pubblico_c = st.columns(3)
    for colonna, titolo, testo in (
        (pubblico_a, "🌱 Autori esordienti", "Hai un'idea ma non sai come trasformarla in una struttura ordinata? La sidebar e l'indice guidato ti accompagnano passo dopo passo."),
        (pubblico_b, "🛠️ Professionisti e formatori", "Trasforma competenze, procedure e materiali di lavoro in manuali pratici, guide, saggi e percorsi didattici."),
        (pubblico_c, "🎓 Docenti e creator di Test Prep", "Crea quiz, simulazioni, soluzioni commentate e materiali per preparazione esami mantenendo il controllo sul contenuto."),
    ):
        with colonna:
            st.markdown(f"<div class='ss-step'><strong>{titolo}</strong>{testo}</div>", unsafe_allow_html=True)

    st.markdown("<div class='ss-section'><h2>Come funziona Scrittore Site</h2><p class='ss-muted'>Segui il percorso e mantieni il controllo su ogni scelta del tuo libro.</p></div>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    for column, title, text in (
        (s1, "1. Definisci il progetto", "Inserisci titolo, lingua, pubblico, genere, obiettivo e argomento. Puoi aggiungere istruzioni e approfondimenti importanti."),
        (s2, "2. Crea e migliora", "Genera l’indice, valuta la struttura e sviluppa le singole parti o l’intero libro. Puoi fermarti, controllare e rigenerare ciò che desideri."),
        (s3, "3. Controlla, salva ed esporta", "Usa anteprima, lettore vocale e controllo di coerenza. Salva la sessione, crea una copia CSV completa oppure esporta il manoscritto in Word o PDF."),
    ):
        with column:
            st.markdown(f"<div class='ss-step'><strong>{title}</strong>{text}</div>", unsafe_allow_html=True)

    st.markdown("<div class='ss-section'><h2>Esempi di progetti che puoi realizzare</h2><p class='ss-muted'>Sono esempi di utilizzo: il titolo, il tono e i contenuti restano sempre scelti da te.</p></div>", unsafe_allow_html=True)
    esempi = st.columns(4)
    for colonna, icona, titolo, testo in (
        (esempi[0], "🧘", "Guida al benessere", "Un percorso pratico su yoga, mindfulness o abitudini quotidiane, con esercizi e limiti chiari."),
        (esempi[1], "🧪", "Manuale tecnico", "Procedure, controlli, esempi e avvertenze per software, processi professionali o competenze operative."),
        (esempi[2], "📚", "Test Prep", "Preparazione strutturata con teoria, quiz, simulazioni svolgibili e soluzioni commentate separate."),
        (esempi[3], "✨", "Narrativa", "Romanzi e racconti con personaggi, conflitto, svolte e conclusione coerente con il genere scelto."),
    ):
        with colonna:
            st.markdown(f"<div class='ss-card'><h3>{icona} {titolo}</h3><p>{testo}</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='ss-section'><h2>Tutte le funzioni, senza complessità</h2><p class='ss-muted'>Strumenti concreti per progettare, scrivere, correggere, ascoltare e preparare il tuo manoscritto.</p></div>", unsafe_allow_html=True)
    gruppo_progetto, gruppo_scrittura, gruppo_controllo = st.columns(3)
    with gruppo_progetto:
        st.markdown("""<div class='ss-feature-group'><h3>🧭 Progetta</h3>
        <p><strong>Brief editoriale completo</strong><br>Titolo, autore, genere, stile, punto di vista, obiettivo e approfondimenti.</p>
        <p><strong>9 lingue disponibili</strong><br>Interfaccia e progetto adattati alla lingua scelta.</p>
        <p><strong>Fonti esterne</strong><br>Carica PDF o Word: il software crea un dossier interno per indice e stesura.</p>
        <p><strong>Indice professionale</strong><br>Ricerca, generazione, voto e rigenerazione guidata.</p></div>""", unsafe_allow_html=True)
    with gruppo_scrittura:
        st.markdown("""<div class='ss-feature-group'><h3>✍️ Scrivi e modifica</h3>
        <p><strong>Sezione, capitolo o libro completo</strong><br>Scegli tu quanto delegare all'AI e metti in pausa quando vuoi.</p>
        <p><strong>Rigenerazione mirata</strong><br>Migliora soltanto la parte necessaria con istruzioni personali.</p>
        <p><strong>Quiz, esempi, ricette e Test Prep</strong><br>Contenuti pratici calibrati sul genere del libro.</p>
        <p><strong>Ricerca e sostituzione globale</strong><br>Uniforma nomi, termini e formulazioni in tutte le sezioni.</p></div>""", unsafe_allow_html=True)
    with gruppo_controllo:
        st.markdown("""<div class='ss-feature-group'><h3>🔎 Controlla e pubblica</h3>
        <p><strong>Controllo del manoscritto</strong><br>Coerenza, ripetizioni, completezza, lunghezza e qualità editoriale.</p>
        <p><strong>Verifica dei fatti</strong><br>Controllo mirato dei dati aggiornabili quando serve.</p>
        <p><strong>Anteprima e lettore vocale</strong><br>Ascolta il libro con voce, velocità, pausa, avanzamento e passaggio in lettura evidenziato.</p>
        <p><strong>Word, PDF e KDP</strong><br>Esporta il manoscritto e prepara la formattazione editoriale.</p>
        <p><strong>Archivio CSV completo</strong><br>Esporta o importa sidebar, indice, sezioni, fonti e immagini per riprendere un progetto quando vuoi.</p></div>""", unsafe_allow_html=True)

    st.markdown("<div class='ss-section'><h2>Importa / Esporta: il progetto è sempre nelle tue mani</h2><p class='ss-muted'>Oltre ai file Word e PDF, puoi creare una copia completa e portabile del lavoro editoriale.</p></div>", unsafe_allow_html=True)
    archivio_a, archivio_b, archivio_c = st.columns(3)
    for colonna, titolo, testo in (
        (archivio_a, "📥 Esporta progetto completo in CSV", "Con un solo download salvi sidebar, lingua, titolo, obiettivo, indice, prefazione, capitoli, sottocapitoli, ringraziamenti, fonti e immagini associate. È una fotografia del lavoro aperto in quel momento."),
        (archivio_b, "📤 Importa e riprendi", "Carica un CSV precedentemente esportato da Scrittore Site: il software ricostruisce nella pagina tutti i campi della sidebar, l’indice e le sezioni scritte. Puoi controllare il risultato prima di fare altro."),
        (archivio_c, "💾 Decidi tu quando salvare", "Dopo un’importazione, il progetto resta nella sessione finché non scegli “SALVA SESSIONE”. Solo allora viene aggiornato il tuo archivio personale; “RIAGGIORNA ALL’ULTIMA STESURA” resta sempre una scelta volontaria."),
    ):
        with colonna:
            st.markdown(f"<div class='ss-step'><strong>{titolo}</strong>{testo}</div>", unsafe_allow_html=True)
    st.markdown("<div class='ss-trust'>CSV serve a salvare e ripristinare il progetto editoriale completo. Word e PDF servono invece a leggere, revisionare, stampare o pubblicare il manoscritto.</div>", unsafe_allow_html=True)

    st.markdown("<div class='ss-section'><h2>Crediti chiari, controllo totale</h2></div>", unsafe_allow_html=True)
    st.markdown("<div class='ss-credit-note'>Un Test Prep approfondito fino a 60 sezioni usa normalmente 75 crediti: 60 sezioni, indice, voto dell’indice, controllo coerenza e metadati. Le funzioni avanzate consumano crediti aggiuntivi solo dopo il preventivo.</div>", unsafe_allow_html=True)
    st.markdown("<div class='ss-trust'>Il libro resta sotto il tuo controllo: puoi fermare la scrittura, rivedere ogni sezione e decidere tu cosa esportare o pubblicare.</div>", unsafe_allow_html=True)
    invito_a, invito_b = st.columns([1.35, 0.65])
    with invito_a:
        if st.button("✒️ Inizia Gratis con 50 crediti", type="primary", use_container_width=True, key="landing_signup_mid"):
            st.session_state["commercial_show_auth"] = True
            st.session_state["commercial_auth_hint"] = "signup"
            st.rerun()
    with invito_b:
        if st.button("Accedi", use_container_width=True, key="landing_login_mid"):
            st.session_state["commercial_show_auth"] = True
            st.session_state["commercial_auth_hint"] = "login"
            st.rerun()

    st.markdown("<div class='ss-section'><h2>Pacchetti crediti chiari</h2><p class='ss-muted'>Scegli il pacchetto in base a ciò che vuoi realizzare. Le stime sono prudenti e includono un margine per le funzioni di controllo.</p></div>", unsafe_allow_html=True)
    price_columns = st.columns(len(PACKAGES))
    for column, (package_key, package) in zip(price_columns, PACKAGES.items()):
        price = f"€ {package['amount_cents'] / 100:.2f}".replace(".", ",")
        guida = PACKAGE_HOME_GUIDE.get(package_key, {})
        with column:
            st.markdown(
                f"<div class='ss-card'><h3>{package['name'].replace('Pacchetto ', '')}</h3>"
                f"<div class='ss-price'>{price}</div><p>{package['credits']} crediti</p>"
                f"<p><strong>{guida.get('ideal', '')}</strong></p>"
                f"<p>{guida.get('estimate', PACKAGE_BOOK_ESTIMATES[package_key])}</p></div>",
                unsafe_allow_html=True,
            )
    st.caption(PACKAGE_ESTIMATE_NOTE)

    st.markdown("<div class='ss-section'><h2>Domande frequenti</h2><p class='ss-muted'>Le informazioni essenziali prima di iniziare.</p></div>", unsafe_allow_html=True)
    with st.expander("Come funzionano i crediti?"):
        st.write("I crediti servono solo per le elaborazioni IA: indice, scrittura, rigenerazioni, controlli e strumenti avanzati. Prima di ogni azione a consumo vedi il preventivo. Se terminano, il lavoro già creato resta leggibile, modificabile ed esportabile.")
    with st.expander("I miei dati e il mio libro sono privati?"):
        st.write("Ogni account mantiene separati crediti e progetto. Il manoscritto non viene pubblicato automaticamente e resta sempre sotto il tuo controllo. Per maggiore sicurezza, usa una password personale e conserva una copia CSV del progetto importante.")
    with st.expander("Come salvo e recupero una stesura?"):
        st.write("Durante il lavoro i dati restano nella pagina. Premi “SALVA SESSIONE” per conservarli nel tuo account. Dopo un nuovo accesso l’editor parte pulito: se vuoi riaprire il progetto salvato, premi “RIAGGIORNA ALL’ULTIMA STESURA”.")
    with st.expander("A cosa serve il CSV del progetto?"):
        st.write("Il CSV è una copia portabile completa: sidebar, indice, sezioni, fonti e immagini associate. Puoi esportarlo come backup e reimportarlo in Scrittore Site. Dopo l’importazione controlli il progetto e decidi tu se premere “SALVA SESSIONE” per aggiornarlo anche nel tuo account.")
    with st.expander("Qual è la differenza tra CSV, Word e PDF?"):
        st.write("CSV serve per salvare e ripristinare il progetto modificabile. Word serve per continuare la revisione editoriale. PDF serve per leggere, condividere, stampare o preparare una bozza per la pubblicazione.")
    with st.expander("Posso modificare o pubblicare il libro quando voglio?"):
        st.write("Sì. Indice e sezioni restano modificabili; puoi rigenerare soltanto le parti necessarie. Nessuna pubblicazione avviene in automatico: la decisione finale è sempre tua.")
    with st.expander("Come posso ricevere assistenza?"):
        st.write("Nella sidebar trovi il pulsante CONTATTI, che apre WhatsApp con un messaggio già predisposto. Puoi anche entrare nella Community per confrontarti con altri utenti.")



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
                utente = _supabase_login(email, password)
                _apri_progetto_pulito_dopo_accesso()
                st.session_state["commercial_user"] = utente
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


def _grant_admin_credits(target_email: str, amount: int, reason: str) -> tuple[str, int]:
    """Accredita crediti a un utente dal pannello protetto dell'amministratore."""
    email = str(target_email or "").strip().lower()
    if not email or "@" not in email:
        raise RuntimeError("Inserisci un indirizzo email valido.")
    if amount <= 0:
        raise RuntimeError("Inserisci un numero di crediti maggiore di zero.")
    if _mode() == "demo" or not _supabase_ready():
        raise RuntimeError("L'accredito manuale è disponibile solo nella modalità collegata a Supabase.")

    profili = _supabase(
        "GET",
        "rest/v1/writer_profiles",
        params={"select": "id,email,credits", "email": f"eq.{email}", "limit": "1"},
    )
    if not profili:
        raise RuntimeError("Nessun account trovato con questa email.")
    profilo = profili[0]
    riferimento = f"admin_manual_{uuid.uuid4().hex}"
    esito = _supabase(
        "POST",
        "rest/v1/rpc/refund_credits",
        payload={
            "p_user_id": profilo["id"],
            "p_credits": int(amount),
            "p_reason": f"admin_manual: {str(reason or 'accredito manuale').strip()[:120]}",
            "p_reference": riferimento,
        },
    )
    if esito is not True:
        raise RuntimeError("L'accredito non è stato completato. Riprova una sola volta.")
    nuovo_saldo = int(profilo["credits"]) + int(amount)
    return str(profilo["email"]), nuovo_saldo


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

        lingua_sidebar = st.session_state.get("editor_language", "Italiano")
        testo_contatti = CONTACT_LABELS.get(lingua_sidebar, CONTACT_LABELS["Italiano"])
        st.link_button(
            f"💬 {testo_contatti}",
            "https://wa.me/393282693777?text=Scrivo%20da%20Scrittore%20Site",
            use_container_width=True,
            help="WhatsApp",
        )

        if is_admin:
            with st.expander("🛡️ Amministrazione crediti", expanded=False):
                st.caption("Visibile solo agli account amministratore. Ogni accredito viene registrato nello storico dell'utente.")
                try:
                    profili_utenti = _supabase(
                        "GET",
                        "rest/v1/writer_profiles",
                        params={
                            "select": "email,credits,updated_at",
                            "order": "email.asc",
                            "limit": "1000",
                        },
                    ) or []
                except Exception as error:
                    profili_utenti = []
                    st.warning(f"Impossibile caricare l'elenco utenti: {error}")

                if profili_utenti:
                    st.caption(f"Utenti registrati: {len(profili_utenti)}")
                    st.dataframe(
                        [
                            {
                                "Email": profilo.get("email", ""),
                                "Crediti": int(profilo.get("credits", 0)),
                                "Ultimo aggiornamento": str(profilo.get("updated_at", ""))[:19].replace("T", " "),
                            }
                            for profilo in profili_utenti
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )
                    target_email = st.selectbox(
                        "Seleziona l'utente",
                        options=[""] + [str(profilo.get("email", "")) for profilo in profili_utenti],
                        format_func=lambda email: "— Seleziona un utente —" if not email else email,
                        key="commercial_admin_credit_email",
                    )
                else:
                    target_email = st.text_input(
                        "Email dell'utente",
                        key="commercial_admin_credit_email",
                        placeholder="utente@email.com",
                    )
                amount = st.number_input(
                    "Crediti da aggiungere",
                    min_value=1,
                    max_value=100_000,
                    value=50,
                    step=1,
                    key="commercial_admin_credit_amount",
                )
                reason = st.text_input(
                    "Nota per lo storico",
                    value="accredito manuale amministratore",
                    key="commercial_admin_credit_reason",
                )
                if st.button(
                    "➕ Aggiungi crediti all'utente",
                    type="primary",
                    use_container_width=True,
                    key="commercial_admin_grant_credits",
                ):
                    try:
                        email_confermata, nuovo_saldo = _grant_admin_credits(target_email, int(amount), reason)
                        st.success(f"Accreditati {int(amount)} crediti a {email_confermata}. Nuovo saldo: {nuovo_saldo} crediti.")
                    except Exception as error:
                        st.error(str(error))

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
            # Chiudendo l'account svuotiamo anche la memoria locale del libro.
            # Il salvataggio cloud non viene toccato e potrà essere richiamato
            # volontariamente dal pulsante di ripristino al prossimo accesso.
            for chiave in list(st.session_state.keys()):
                if not chiave.startswith("commercial_"):
                    del st.session_state[chiave]
            st.session_state.pop("commercial_user", None)
            st.session_state.pop("commercial_user_context", None)
            st.session_state.pop("commercial_show_auth", None)
            st.session_state.pop("commercial_project_reset_requested", None)
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
