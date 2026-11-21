"""Suggerimenti d'uso dell'editor, nelle 9 lingue dell'app.

Modulo puro (nessuna chiamata AI, nessun accesso a Streamlit):
- regole per i suggerimenti "al momento giusto";
- consigli da mostrare durante le attese;
- testi delle schede ancora vuote;
- spiegazioni (?) dei campi della sidebar;
- passi della visita guidata al primo accesso.
"""

from __future__ import annotations

LINGUE = ("Italiano", "English", "Español", "Français", "Deutsch", "Română", "Русский", "العربية", "中文")

# --------------------------------------------------------------------------
# 1. Suggerimenti al momento giusto
# --------------------------------------------------------------------------
SUGGERIMENTI = {
    "Italiano": {
        "salva": "💾 Hai modifiche non ancora salvate nel tuo account. Premi **SALVA SESSIONE** nella sidebar per non perderle.",
        "dopo_indice": "✍️ L'indice è pronto. Apri **2. Scrivi il libro**: puoi scrivere una sezione alla volta o usare **Scrivi tutto il libro**. Prima puoi ancora correggere l'indice a mano.",
        "fine_libro": "📖 Tutte le sezioni sono scritte. Prima di esportare guarda **3. Anteprima** e fai il controllo finale in **4. Importa / Esporta**.",
        "approfondita": "🌐 Per questo genere conviene la ricerca fonti **Approfondita** (sidebar, Fonti e ricerca): trova più dati verificabili prima dell'indice.",
        "personaggi": "🎭 Per un romanzo, compila la **scheda personaggi** nel Progetto del libro (scheda 1. Indice): la stesura terrà nomi, aspetto e voci coerenti.",
    },
    "English": {
        "salva": "💾 You have changes not yet saved to your account. Press **SAVE SESSION** in the sidebar so you don't lose them.",
        "dopo_indice": "✍️ The outline is ready. Open **2. Write the book**: write one section at a time or use **Write the whole book**. You can still edit the outline by hand first.",
        "fine_libro": "📖 All sections are written. Before exporting, check **3. Preview** and run the final check in **4. Import / Export**.",
        "approfondita": "🌐 For this genre, **In-depth** source research is worth it (sidebar, Sources and research): it finds more verifiable data before the outline.",
        "personaggi": "🎭 For a novel, fill in the **character sheet** in the Book plan (tab 1. Outline): writing will keep names, looks and voices consistent.",
    },
    "Español": {
        "salva": "💾 Tienes cambios aún no guardados en tu cuenta. Pulsa **GUARDAR SESIÓN** en la barra lateral para no perderlos.",
        "dopo_indice": "✍️ El índice está listo. Abre **2. Escribe el libro**: escribe una sección cada vez o usa **Escribir todo el libro**. Antes aún puedes corregir el índice a mano.",
        "fine_libro": "📖 Todas las secciones están escritas. Antes de exportar revisa **3. Vista previa** y haz el control final en **4. Importar / Exportar**.",
        "approfondita": "🌐 Para este género conviene la búsqueda de fuentes **En profundidad** (barra lateral, Fuentes y búsqueda): encuentra más datos verificables antes del índice.",
        "personaggi": "🎭 Para una novela, completa la **ficha de personajes** en el Proyecto del libro (pestaña 1. Índice): la redacción mantendrá nombres, aspecto y voces coherentes.",
    },
    "Français": {
        "salva": "💾 Vous avez des modifications non enregistrées dans votre compte. Appuyez sur **ENREGISTRER LA SESSION** dans la barre latérale pour ne pas les perdre.",
        "dopo_indice": "✍️ Le plan est prêt. Ouvrez **2. Écrire le livre** : rédigez une section à la fois ou utilisez **Écrire tout le livre**. Vous pouvez encore corriger le plan à la main avant.",
        "fine_libro": "📖 Toutes les sections sont écrites. Avant l’export, regardez **3. Aperçu** et lancez le contrôle final dans **4. Importer / Exporter**.",
        "approfondita": "🌐 Pour ce genre, la recherche de sources **Approfondie** est conseillée (barre latérale, Sources et recherche) : plus de données vérifiables avant le plan.",
        "personaggi": "🎭 Pour un roman, remplissez la **fiche personnages** dans le Projet du livre (onglet 1. Plan) : la rédaction gardera noms, apparences et voix cohérents.",
    },
    "Deutsch": {
        "salva": "💾 Sie haben Änderungen, die noch nicht in Ihrem Konto gespeichert sind. Drücken Sie **SITZUNG SPEICHERN** in der Seitenleiste, damit nichts verloren geht.",
        "dopo_indice": "✍️ Die Gliederung ist fertig. Öffnen Sie **2. Buch schreiben**: Abschnitt für Abschnitt oder mit **Ganzes Buch schreiben**. Vorher können Sie die Gliederung noch von Hand anpassen.",
        "fine_libro": "📖 Alle Abschnitte sind geschrieben. Prüfen Sie vor dem Export **3. Vorschau** und die Endkontrolle unter **4. Import / Export**.",
        "approfondita": "🌐 Für dieses Genre lohnt sich die **gründliche** Quellenrecherche (Seitenleiste, Quellen und Recherche): mehr überprüfbare Daten vor der Gliederung.",
        "personaggi": "🎭 Füllen Sie für einen Roman das **Figurenblatt** im Buchprojekt aus (Reiter 1. Gliederung): Namen, Aussehen und Stimmen bleiben stimmig.",
    },
    "Română": {
        "salva": "💾 Ai modificări încă nesalvate în cont. Apasă **SALVEAZĂ SESIUNEA** în bara laterală ca să nu le pierzi.",
        "dopo_indice": "✍️ Cuprinsul este gata. Deschide **2. Scrie cartea**: scrie câte o secțiune sau folosește **Scrie toată cartea**. Înainte poți corecta cuprinsul manual.",
        "fine_libro": "📖 Toate secțiunile sunt scrise. Înainte de export, verifică **3. Previzualizare** și controlul final din **4. Import / Export**.",
        "approfondita": "🌐 Pentru acest gen merită căutarea de surse **Aprofundată** (bara laterală, Surse și cercetare): găsește mai multe date verificabile înainte de cuprins.",
        "personaggi": "🎭 Pentru un roman, completează **fișa personajelor** în Proiectul cărții (fila 1. Cuprins): scrierea va păstra coerente numele, aspectul și vocile.",
    },
    "Русский": {
        "salva": "💾 Есть изменения, ещё не сохранённые в аккаунте. Нажмите **СОХРАНИТЬ СЕССИЮ** на боковой панели, чтобы их не потерять.",
        "dopo_indice": "✍️ Оглавление готово. Откройте **2. Написать книгу**: пишите по разделу или используйте **Написать всю книгу**. До этого оглавление можно поправить вручную.",
        "fine_libro": "📖 Все разделы написаны. Перед экспортом посмотрите **3. Просмотр** и выполните итоговую проверку в **4. Импорт / Экспорт**.",
        "approfondita": "🌐 Для этого жанра стоит выбрать **углублённый** поиск источников (панель, Источники и поиск): больше проверяемых данных до оглавления.",
        "personaggi": "🎭 Для романа заполните **карточку персонажей** в Проекте книги (вкладка 1. Оглавление): имена, внешность и голоса останутся последовательными.",
    },
    "العربية": {
        "salva": "💾 لديك تعديلات لم تُحفظ بعد في حسابك. اضغط **حفظ الجلسة** في الشريط الجانبي حتى لا تفقدها.",
        "dopo_indice": "✍️ الفهرس جاهز. افتح **2. اكتب الكتاب**: اكتب قسماً تلو الآخر أو استخدم **اكتب الكتاب كله**. يمكنك قبل ذلك تعديل الفهرس يدوياً.",
        "fine_libro": "📖 كُتبت جميع الأقسام. قبل التصدير راجع **3. المعاينة** وأجرِ الفحص النهائي في **4. استيراد / تصدير**.",
        "approfondita": "🌐 لهذا النوع يُنصح بالبحث **المعمّق** عن المصادر (الشريط الجانبي، المصادر والبحث): بيانات أكثر قابلة للتحقق قبل الفهرس.",
        "personaggi": "🎭 للرواية، املأ **بطاقة الشخصيات** في مشروع الكتاب (تبويب 1. الفهرس): ستبقى الأسماء والملامح والأصوات متسقة.",
    },
    "中文": {
        "salva": "💾 有尚未保存到账户的修改。请点击侧边栏中的 **保存会话**，以免丢失。",
        "dopo_indice": "✍️ 目录已准备好。打开 **2. 写作全书**：可逐节写作，或使用 **写作全书**。在此之前仍可手动修改目录。",
        "fine_libro": "📖 所有章节已完成。导出前请查看 **3. 预览**，并在 **4. 导入 / 导出** 中运行最终检查。",
        "approfondita": "🌐 这个类型建议使用 **深入** 资料检索（侧边栏 · 资料与研究）：在生成目录前找到更多可核实的数据。",
        "personaggi": "🎭 写小说时，请在图书项目（1. 目录）中填写 **人物卡**：写作会保持姓名、外貌和语气一致。",
    },
}
TITOLO_CHIUDI = {"Italiano": "Chiudi", "English": "Close", "Español": "Cerrar", "Français": "Fermer", "Deutsch": "Schließen",
                 "Română": "Închide", "Русский": "Закрыть", "العربية": "إغلاق", "中文": "关闭"}


def suggerimenti_attivi(stato: dict, chiusi: dict | None = None, massimo: int = 2) -> list[str]:
    """Identificativi dei suggerimenti da mostrare ora, dal più urgente.

    ``stato`` contiene: job_attivo, non_salvato, firma_contenuti, indice_pronto,
    sezioni_scritte, sezioni_previste, brief_pronto, tipo_opera, livello_ricerca,
    livello_consigliato, scheda_personaggi_vuota.
    ``chiusi`` mappa id -> firma al momento della chiusura ("" = chiuso e basta).
    """
    if stato.get("job_attivo"):
        return []
    chiusi = dict(chiusi or {})
    candidati = []
    if stato.get("non_salvato"):
        candidati.append("salva")
    if stato.get("indice_pronto") and not stato.get("sezioni_scritte"):
        candidati.append("dopo_indice")
    if (stato.get("tipo_opera") == "narrativa" and stato.get("indice_pronto")
            and stato.get("scheda_personaggi_vuota")):
        candidati.append("personaggi")
    if (stato.get("brief_pronto") and not stato.get("indice_pronto")
            and stato.get("livello_consigliato") == "approfondita"
            and stato.get("livello_ricerca") == "standard"):
        candidati.append("approfondita")
    previste = int(stato.get("sezioni_previste") or 0)
    if previste and int(stato.get("sezioni_scritte") or 0) >= previste:
        candidati.append("fine_libro")
    attivi = []
    for chiave in candidati:
        if chiave in chiusi:
            # "salva" torna solo se il contenuto è cambiato dopo la chiusura.
            if chiave != "salva" or chiusi[chiave] == stato.get("firma_contenuti", ""):
                continue
        attivi.append(chiave)
    return attivi[:massimo]


def testo_suggerimento(chiave: str, lingua: str) -> str:
    voci = SUGGERIMENTI.get(lingua) or SUGGERIMENTI["English"]
    return voci.get(chiave) or SUGGERIMENTI["English"][chiave]


# --------------------------------------------------------------------------
# 2. Consigli durante le attese
# --------------------------------------------------------------------------
CONSIGLI_ATTESA = {
    "Italiano": (
        "Puoi correggere a mano qualsiasi sezione: poi premi Salva sessione.",
        "Il cervello economico costa circa un terzo del cervello costoso.",
        "Con il CSV (scheda 4) puoi spostare il progetto su un altro computer.",
        "La scheda di coerenza ricorda personaggi, fatti e promesse fatte al lettore.",
        "Nella scheda 1 puoi migliorare l'indice parlando con la chat dell'indice.",
        "L'Anteprima (scheda 3) mostra il libro come lo leggerà il lettore.",
        "Le fonti web trovate prima dell'indice vengono usate anche nei capitoli.",
        "Puoi mettere in pausa Scrivi tutto il libro e riprendere quando vuoi.",
    ),
    "English": (
        "You can edit any section by hand: then press Save session.",
        "The economical brain costs about a third of the premium brain.",
        "With the CSV (tab 4) you can move the project to another computer.",
        "The coherence sheet remembers characters, facts and promises made to the reader.",
        "In tab 1 you can improve the outline by talking to the outline chat.",
        "Preview (tab 3) shows the book as the reader will see it.",
        "Web sources found before the outline are also used in the chapters.",
        "You can pause Write the whole book and resume whenever you like.",
    ),
    "Español": (
        "Puedes corregir a mano cualquier sección: luego pulsa Guardar sesión.",
        "El cerebro económico cuesta alrededor de un tercio del cerebro caro.",
        "Con el CSV (pestaña 4) puedes llevar el proyecto a otro ordenador.",
        "La ficha de coherencia recuerda personajes, hechos y promesas al lector.",
        "En la pestaña 1 puedes mejorar el índice hablando con el chat del índice.",
        "La Vista previa (pestaña 3) muestra el libro como lo verá el lector.",
        "Las fuentes web encontradas antes del índice se usan también en los capítulos.",
        "Puedes pausar Escribir todo el libro y reanudar cuando quieras.",
    ),
    "Français": (
        "Vous pouvez corriger n’importe quelle section à la main, puis enregistrer la session.",
        "Le cerveau économique coûte environ un tiers du cerveau premium.",
        "Avec le CSV (onglet 4), vous pouvez déplacer le projet sur un autre ordinateur.",
        "La fiche de cohérence retient personnages, faits et promesses faites au lecteur.",
        "Dans l’onglet 1, vous pouvez améliorer le plan avec le chat du plan.",
        "L’Aperçu (onglet 3) montre le livre tel que le lecteur le verra.",
        "Les sources web trouvées avant le plan servent aussi dans les chapitres.",
        "Vous pouvez mettre en pause Écrire tout le livre et reprendre quand vous voulez.",
    ),
    "Deutsch": (
        "Sie können jeden Abschnitt von Hand ändern und danach die Sitzung speichern.",
        "Das sparsame Gehirn kostet etwa ein Drittel des teuren Gehirns.",
        "Mit der CSV-Datei (Reiter 4) können Sie das Projekt auf einen anderen Computer bringen.",
        "Das Kohärenzblatt merkt sich Figuren, Fakten und Versprechen an den Leser.",
        "In Reiter 1 können Sie die Gliederung im Gespräch mit dem Gliederungs-Chat verbessern.",
        "Die Vorschau (Reiter 3) zeigt das Buch so, wie es der Leser sieht.",
        "Webquellen aus der Recherche vor der Gliederung fließen auch in die Kapitel ein.",
        "Sie können Ganzes Buch schreiben pausieren und jederzeit fortsetzen.",
    ),
    "Română": (
        "Poți corecta manual orice secțiune, apoi apasă Salvează sesiunea.",
        "Creierul economic costă aproximativ o treime din creierul scump.",
        "Cu CSV-ul (fila 4) poți muta proiectul pe alt calculator.",
        "Fișa de coerență ține minte personaje, fapte și promisiuni făcute cititorului.",
        "În fila 1 poți îmbunătăți cuprinsul discutând cu chatul cuprinsului.",
        "Previzualizarea (fila 3) arată cartea așa cum o va vedea cititorul.",
        "Sursele web găsite înainte de cuprins sunt folosite și în capitole.",
        "Poți pune pe pauză Scrie toată cartea și relua oricând.",
    ),
    "Русский": (
        "Любой раздел можно поправить вручную, а затем сохранить сессию.",
        "Экономичный мозг стоит примерно треть от дорогого.",
        "С помощью CSV (вкладка 4) проект можно перенести на другой компьютер.",
        "Карточка согласованности помнит персонажей, факты и обещания читателю.",
        "На вкладке 1 оглавление можно улучшить в чате оглавления.",
        "Просмотр (вкладка 3) показывает книгу так, как её увидит читатель.",
        "Веб-источники, найденные до оглавления, используются и в главах.",
        "«Написать всю книгу» можно приостановить и продолжить в любой момент.",
    ),
    "العربية": (
        "يمكنك تعديل أي قسم يدوياً، ثم اضغط حفظ الجلسة.",
        "العقل الاقتصادي يكلف نحو ثلث العقل المكلف.",
        "باستخدام ملف CSV (التبويب 4) يمكنك نقل المشروع إلى حاسوب آخر.",
        "بطاقة الاتساق تتذكر الشخصيات والوقائع والوعود المقدّمة للقارئ.",
        "في التبويب 1 يمكنك تحسين الفهرس بالحديث مع دردشة الفهرس.",
        "المعاينة (التبويب 3) تعرض الكتاب كما سيراه القارئ.",
        "مصادر الويب التي وُجدت قبل الفهرس تُستخدم أيضاً في الفصول.",
        "يمكنك إيقاف «اكتب الكتاب كله» مؤقتاً والاستئناف متى شئت.",
    ),
    "中文": (
        "任何章节都可以手动修改，之后点击保存会话。",
        "经济型大脑的费用约为高级大脑的三分之一。",
        "通过 CSV（第 4 页）可以把项目转移到另一台电脑。",
        "一致性卡会记住人物、事实以及对读者的承诺。",
        "在第 1 页可以通过目录聊天改进目录。",
        "预览（第 3 页）按读者看到的样子显示整本书。",
        "生成目录前找到的网络资料也会用于各章节。",
        "“写作全书”可以随时暂停和继续。",
    ),
}
PREFISSO_CONSIGLIO = {"Italiano": "Lo sapevi?", "English": "Did you know?", "Español": "¿Sabías que…?", "Français": "Le saviez-vous ?",
                      "Deutsch": "Schon gewusst?", "Română": "Știai că?", "Русский": "А вы знали?", "العربية": "هل تعلم؟", "中文": "你知道吗？"}


def consiglio_attesa(lingua: str, seme: int = 0) -> str:
    """Un consiglio a rotazione (``seme`` può essere un contatore o il tempo)."""
    consigli = CONSIGLI_ATTESA.get(lingua) or CONSIGLI_ATTESA["English"]
    prefisso = PREFISSO_CONSIGLIO.get(lingua) or PREFISSO_CONSIGLIO["English"]
    return f"💡 {prefisso} {consigli[int(seme) % len(consigli)]}"


# --------------------------------------------------------------------------
# 3. Schede ancora vuote: cosa vedrai qui e cosa fare prima
# --------------------------------------------------------------------------
# indice della scheda di destinazione nel menu (ordine del DOM): 2 = 1. Indice, 3 = 2. Scrivi
SCHEDE_VUOTE = {
    "Italiano": {
        "scrivi": ("Qui scriverai il libro, sezione per sezione. Prima serve l'indice.", "📊 Vai a 1. Indice", 2),
        "anteprima": ("Qui vedrai il libro impaginato come lo leggerà il lettore. Prima scrivi almeno una sezione.", "✍️ Vai a 2. Scrivi il libro", 3),
        "esporta": ("Qui esporterai il libro in Word, PDF o CSV e farai i controlli finali. Puoi già importare un CSV salvato.", "✍️ Vai a 2. Scrivi il libro", 3),
        "formattazione": ("Qui preparerai il file per la pubblicazione (KDP). Prima scrivi il libro.", "✍️ Vai a 2. Scrivi il libro", 3),
    },
    "English": {
        "scrivi": ("Here you will write the book, section by section. First you need the outline.", "📊 Go to 1. Outline", 2),
        "anteprima": ("Here you will see the book laid out as the reader will read it. First write at least one section.", "✍️ Go to 2. Write the book", 3),
        "esporta": ("Here you will export the book to Word, PDF or CSV and run the final checks. You can already import a saved CSV.", "✍️ Go to 2. Write the book", 3),
        "formattazione": ("Here you will prepare the file for publishing (KDP). First write the book.", "✍️ Go to 2. Write the book", 3),
    },
    "Español": {
        "scrivi": ("Aquí escribirás el libro, sección por sección. Primero necesitas el índice.", "📊 Ir a 1. Índice", 2),
        "anteprima": ("Aquí verás el libro maquetado como lo leerá el lector. Primero escribe al menos una sección.", "✍️ Ir a 2. Escribe el libro", 3),
        "esporta": ("Aquí exportarás el libro a Word, PDF o CSV y harás los controles finales. Ya puedes importar un CSV guardado.", "✍️ Ir a 2. Escribe el libro", 3),
        "formattazione": ("Aquí prepararás el archivo para publicar (KDP). Primero escribe el libro.", "✍️ Ir a 2. Escribe el libro", 3),
    },
    "Français": {
        "scrivi": ("Ici vous écrirez le livre, section par section. Il faut d’abord le plan.", "📊 Aller à 1. Plan", 2),
        "anteprima": ("Ici vous verrez le livre mis en page tel que le lecteur le lira. Écrivez d’abord au moins une section.", "✍️ Aller à 2. Écrire le livre", 3),
        "esporta": ("Ici vous exporterez le livre en Word, PDF ou CSV et ferez les contrôles finaux. Vous pouvez déjà importer un CSV enregistré.", "✍️ Aller à 2. Écrire le livre", 3),
        "formattazione": ("Ici vous préparerez le fichier pour la publication (KDP). Écrivez d’abord le livre.", "✍️ Aller à 2. Écrire le livre", 3),
    },
    "Deutsch": {
        "scrivi": ("Hier schreiben Sie das Buch, Abschnitt für Abschnitt. Zuerst brauchen Sie die Gliederung.", "📊 Zu 1. Gliederung", 2),
        "anteprima": ("Hier sehen Sie das Buch so gesetzt, wie es der Leser liest. Schreiben Sie zuerst mindestens einen Abschnitt.", "✍️ Zu 2. Buch schreiben", 3),
        "esporta": ("Hier exportieren Sie das Buch als Word, PDF oder CSV und machen die Endkontrolle. Eine gespeicherte CSV können Sie schon importieren.", "✍️ Zu 2. Buch schreiben", 3),
        "formattazione": ("Hier bereiten Sie die Datei für die Veröffentlichung (KDP) vor. Schreiben Sie zuerst das Buch.", "✍️ Zu 2. Buch schreiben", 3),
    },
    "Română": {
        "scrivi": ("Aici vei scrie cartea, secțiune cu secțiune. Mai întâi ai nevoie de cuprins.", "📊 Mergi la 1. Cuprins", 2),
        "anteprima": ("Aici vei vedea cartea paginată așa cum o va citi cititorul. Mai întâi scrie cel puțin o secțiune.", "✍️ Mergi la 2. Scrie cartea", 3),
        "esporta": ("Aici vei exporta cartea în Word, PDF sau CSV și vei face controalele finale. Poți deja importa un CSV salvat.", "✍️ Mergi la 2. Scrie cartea", 3),
        "formattazione": ("Aici vei pregăti fișierul pentru publicare (KDP). Mai întâi scrie cartea.", "✍️ Mergi la 2. Scrie cartea", 3),
    },
    "Русский": {
        "scrivi": ("Здесь вы будете писать книгу раздел за разделом. Сначала нужно оглавление.", "📊 Перейти к 1. Оглавление", 2),
        "anteprima": ("Здесь вы увидите свёрстанную книгу так, как её прочтёт читатель. Сначала напишите хотя бы один раздел.", "✍️ Перейти к 2. Написать книгу", 3),
        "esporta": ("Здесь вы экспортируете книгу в Word, PDF или CSV и выполните итоговые проверки. Сохранённый CSV можно импортировать уже сейчас.", "✍️ Перейти к 2. Написать книгу", 3),
        "formattazione": ("Здесь вы подготовите файл к публикации (KDP). Сначала напишите книгу.", "✍️ Перейти к 2. Написать книгу", 3),
    },
    "العربية": {
        "scrivi": ("هنا ستكتب الكتاب قسماً بعد قسم. تحتاج أولاً إلى الفهرس.", "📊 انتقل إلى 1. الفهرس", 2),
        "anteprima": ("هنا سترى الكتاب منسقاً كما سيقرؤه القارئ. اكتب أولاً قسماً واحداً على الأقل.", "✍️ انتقل إلى 2. اكتب الكتاب", 3),
        "esporta": ("هنا ستصدّر الكتاب إلى Word أو PDF أو CSV وتجري الفحوص النهائية. يمكنك الآن استيراد ملف CSV محفوظ.", "✍️ انتقل إلى 2. اكتب الكتاب", 3),
        "formattazione": ("هنا ستجهز الملف للنشر (KDP). اكتب الكتاب أولاً.", "✍️ انتقل إلى 2. اكتب الكتاب", 3),
    },
    "中文": {
        "scrivi": ("你将在这里逐节写作。首先需要目录。", "📊 前往 1. 目录", 2),
        "anteprima": ("这里会按读者看到的版式显示全书。请先至少写完一节。", "✍️ 前往 2. 写作全书", 3),
        "esporta": ("你将在这里把书导出为 Word、PDF 或 CSV 并做最终检查。现在已经可以导入保存的 CSV。", "✍️ 前往 2. 写作全书", 3),
        "formattazione": ("你将在这里准备出版文件（KDP）。请先写完这本书。", "✍️ 前往 2. 写作全书", 3),
    },
}


def scheda_vuota(chiave: str, lingua: str) -> tuple[str, str, int]:
    voci = SCHEDE_VUOTE.get(lingua) or SCHEDE_VUOTE["English"]
    return voci.get(chiave) or SCHEDE_VUOTE["English"][chiave]


# --------------------------------------------------------------------------
# 4. Spiegazioni (?) dei campi della sidebar
# --------------------------------------------------------------------------
AIUTI_CAMPI = {
    "Italiano": {
        "editor_language": "La lingua dell'interfaccia e del libro. Puoi cambiarla in qualsiasi momento.",
        "book_title": "Il titolo del libro. Puoi metterne uno provvisorio, es. «Dormire bene in 30 giorni».",
        "book_author": "Il nome che comparirà in copertina e nei metadati, es. «Mario Rossi».",
        "fonti_file": "Facoltativo. PDF o DOCX tuoi (appunti, ricerche): l'AI ne ricava i concetti e scrive con parole sue.",
        "book_genre": "Il genere decide la struttura: romanzo (scene e personaggi), saggio (tesi e prove) o manuale (procedure).",
        "book_writing_style": "Il tipo di testo, es. divulgativo, accademico o pratico. Cambia lessico e livello di dettaglio.",
        "book_narrative_style": "Il tono del racconto, es. coinvolgente, ironico, tecnico.",
        "book_tense": "Il tempo verbale del racconto: passato (più classico) o presente (più immediato).",
        "book_point_of_view": "A chi si rivolge il testo: «tu» (diretto), «voi», o impersonale.",
        "book_goal": "Cosa saprà fare o provare il lettore alla fine, es. «preparare il pane in casa».",
        "book_desired_result": "Il risultato concreto che vuoi ottenere, es. «un piano serale da seguire ogni sera».",
        "book_plot": "Di cosa parla il libro: la trama per un romanzo, l'argomento per un saggio o un manuale.",
        "book_further_details": "Facoltativo: aspetti da trattare, esempi, vincoli o temi da evitare.",
        "book_personal_voice": "Facoltativo: come scrivi tu (frasi brevi, ironia, termini preferiti) per un libro con la tua voce.",
        "book_personal_material": "Facoltativo: casi, ricordi o esperienze tue da inserire nel libro.",
        "book_personal_priorities": "Facoltativo: cosa per te deve emergere di più.",
        "book_personal_boundaries": "Facoltativo: cosa il libro non deve dire o fare.",
    },
    "English": {
        "editor_language": "The language of the interface and of the book. You can change it at any time.",
        "book_title": "The book title. A working title is fine, e.g. “Sleep Well in 30 Days”.",
        "book_author": "The name shown on the cover and in the metadata, e.g. “Jane Smith”.",
        "fonti_file": "Optional. Your own PDFs or DOCX files (notes, research): the AI extracts the ideas and writes in its own words.",
        "book_genre": "The genre sets the structure: novel (scenes and characters), essay (thesis and evidence) or manual (procedures).",
        "book_writing_style": "The kind of text, e.g. popular, academic or practical. It changes vocabulary and level of detail.",
        "book_narrative_style": "The tone of the writing, e.g. engaging, ironic, technical.",
        "book_tense": "The tense of the story: past (more classic) or present (more immediate).",
        "book_point_of_view": "Who the text speaks to: “you” (direct), plural, or impersonal.",
        "book_goal": "What the reader will be able to do or feel at the end, e.g. “bake bread at home”.",
        "book_desired_result": "The concrete result you want, e.g. “an evening routine to follow every night”.",
        "book_plot": "What the book is about: the plot for a novel, the topic for an essay or a manual.",
        "book_further_details": "Optional: aspects to cover, examples, constraints or topics to avoid.",
        "book_personal_voice": "Optional: how you write (short sentences, irony, favourite words) for a book in your voice.",
        "book_personal_material": "Optional: your own cases, memories or experiences to include.",
        "book_personal_priorities": "Optional: what matters most to you.",
        "book_personal_boundaries": "Optional: what the book must not say or do.",
    },
    "Español": {
        "editor_language": "El idioma de la interfaz y del libro. Puedes cambiarlo en cualquier momento.",
        "book_title": "El título del libro. Vale uno provisional, p. ej. «Dormir bien en 30 días».",
        "book_author": "El nombre que aparecerá en la portada y en los metadatos, p. ej. «Ana López».",
        "fonti_file": "Opcional. Tus PDF o DOCX (apuntes, investigaciones): la IA extrae las ideas y escribe con sus palabras.",
        "book_genre": "El género define la estructura: novela (escenas y personajes), ensayo (tesis y pruebas) o manual (procedimientos).",
        "book_writing_style": "El tipo de texto, p. ej. divulgativo, académico o práctico. Cambia el léxico y el nivel de detalle.",
        "book_narrative_style": "El tono del texto, p. ej. cercano, irónico, técnico.",
        "book_tense": "El tiempo verbal del relato: pasado (más clásico) o presente (más inmediato).",
        "book_point_of_view": "A quién se dirige el texto: «tú» (directo), «vosotros» o impersonal.",
        "book_goal": "Qué sabrá hacer o sentir el lector al final, p. ej. «hacer pan en casa».",
        "book_desired_result": "El resultado concreto que buscas, p. ej. «una rutina para cada noche».",
        "book_plot": "De qué trata el libro: la trama de una novela, el tema de un ensayo o manual.",
        "book_further_details": "Opcional: aspectos a tratar, ejemplos, límites o temas a evitar.",
        "book_personal_voice": "Opcional: cómo escribes tú (frases cortas, ironía, palabras favoritas) para un libro con tu voz.",
        "book_personal_material": "Opcional: casos, recuerdos o experiencias tuyas para incluir.",
        "book_personal_priorities": "Opcional: lo que más debe destacar para ti.",
        "book_personal_boundaries": "Opcional: lo que el libro no debe decir ni hacer.",
    },
    "Français": {
        "editor_language": "La langue de l’interface et du livre. Vous pouvez la changer à tout moment.",
        "book_title": "Le titre du livre. Un titre provisoire suffit, ex. « Bien dormir en 30 jours ».",
        "book_author": "Le nom affiché sur la couverture et dans les métadonnées, ex. « Marie Dupont ».",
        "fonti_file": "Facultatif. Vos PDF ou DOCX (notes, recherches) : l’IA en tire les idées et écrit avec ses mots.",
        "book_genre": "Le genre fixe la structure : roman (scènes et personnages), essai (thèse et preuves) ou manuel (procédures).",
        "book_writing_style": "Le type de texte, ex. vulgarisation, académique ou pratique. Il change le vocabulaire et le niveau de détail.",
        "book_narrative_style": "Le ton du texte, ex. captivant, ironique, technique.",
        "book_tense": "Le temps du récit : passé (plus classique) ou présent (plus immédiat).",
        "book_point_of_view": "À qui s’adresse le texte : « tu », « vous » ou impersonnel.",
        "book_goal": "Ce que le lecteur saura faire ou ressentir à la fin, ex. « faire son pain maison ».",
        "book_desired_result": "Le résultat concret voulu, ex. « une routine à suivre chaque soir ».",
        "book_plot": "Le sujet du livre : l’intrigue d’un roman, le thème d’un essai ou d’un manuel.",
        "book_further_details": "Facultatif : aspects à traiter, exemples, contraintes ou sujets à éviter.",
        "book_personal_voice": "Facultatif : votre façon d’écrire (phrases courtes, ironie, mots préférés) pour un livre à votre voix.",
        "book_personal_material": "Facultatif : vos cas, souvenirs ou expériences à inclure.",
        "book_personal_priorities": "Facultatif : ce qui doit ressortir le plus pour vous.",
        "book_personal_boundaries": "Facultatif : ce que le livre ne doit pas dire ni faire.",
    },
    "Deutsch": {
        "editor_language": "Die Sprache der Oberfläche und des Buches. Sie können sie jederzeit ändern.",
        "book_title": "Der Buchtitel. Ein Arbeitstitel genügt, z. B. „Gut schlafen in 30 Tagen“.",
        "book_author": "Der Name auf dem Cover und in den Metadaten, z. B. „Anna Müller“.",
        "fonti_file": "Optional. Eigene PDF- oder DOCX-Dateien (Notizen, Recherchen): Die KI übernimmt die Ideen und schreibt mit eigenen Worten.",
        "book_genre": "Das Genre bestimmt den Aufbau: Roman (Szenen und Figuren), Sachbuch (These und Belege) oder Handbuch (Abläufe).",
        "book_writing_style": "Die Textart, z. B. populär, wissenschaftlich oder praktisch. Sie ändert Wortwahl und Detailtiefe.",
        "book_narrative_style": "Der Ton des Textes, z. B. mitreißend, ironisch, technisch.",
        "book_tense": "Die Zeitform der Geschichte: Vergangenheit (klassischer) oder Gegenwart (unmittelbarer).",
        "book_point_of_view": "Wen der Text anspricht: „du“, „Sie“ oder unpersönlich.",
        "book_goal": "Was der Leser am Ende kann oder fühlt, z. B. „Brot zu Hause backen“.",
        "book_desired_result": "Das konkrete Ergebnis, z. B. „eine Abendroutine für jeden Tag“.",
        "book_plot": "Worum es im Buch geht: die Handlung eines Romans, das Thema eines Sach- oder Handbuchs.",
        "book_further_details": "Optional: Aspekte, Beispiele, Vorgaben oder Themen, die vermieden werden sollen.",
        "book_personal_voice": "Optional: wie Sie schreiben (kurze Sätze, Ironie, Lieblingswörter) für ein Buch mit Ihrer Stimme.",
        "book_personal_material": "Optional: eigene Fälle, Erinnerungen oder Erfahrungen für das Buch.",
        "book_personal_priorities": "Optional: was Ihnen am wichtigsten ist.",
        "book_personal_boundaries": "Optional: was das Buch nicht sagen oder tun darf.",
    },
    "Română": {
        "editor_language": "Limba interfeței și a cărții. O poți schimba oricând.",
        "book_title": "Titlul cărții. Merge și unul provizoriu, ex. „Dormi bine în 30 de zile”.",
        "book_author": "Numele de pe copertă și din metadate, ex. „Ana Popescu”.",
        "fonti_file": "Opțional. PDF-uri sau DOCX-uri proprii (notițe, cercetări): AI-ul extrage ideile și scrie cu cuvintele lui.",
        "book_genre": "Genul stabilește structura: roman (scene și personaje), eseu (teză și dovezi) sau manual (proceduri).",
        "book_writing_style": "Tipul de text, ex. de popularizare, academic sau practic. Schimbă vocabularul și nivelul de detaliu.",
        "book_narrative_style": "Tonul textului, ex. captivant, ironic, tehnic.",
        "book_tense": "Timpul verbal al poveștii: trecut (mai clasic) sau prezent (mai direct).",
        "book_point_of_view": "Cui i se adresează textul: „tu”, „voi” sau impersonal.",
        "book_goal": "Ce va ști să facă sau să simtă cititorul la final, ex. „să facă pâine acasă”.",
        "book_desired_result": "Rezultatul concret dorit, ex. „o rutină de seară de urmat zilnic”.",
        "book_plot": "Despre ce este cartea: intriga unui roman, tema unui eseu sau manual.",
        "book_further_details": "Opțional: aspecte de tratat, exemple, limite sau teme de evitat.",
        "book_personal_voice": "Opțional: cum scrii tu (fraze scurte, ironie, cuvinte preferate) pentru o carte cu vocea ta.",
        "book_personal_material": "Opțional: cazuri, amintiri sau experiențe proprii de inclus.",
        "book_personal_priorities": "Opțional: ce trebuie să iasă cel mai mult în evidență pentru tine.",
        "book_personal_boundaries": "Opțional: ce nu trebuie să spună sau să facă cartea.",
    },
    "Русский": {
        "editor_language": "Язык интерфейса и книги. Его можно изменить в любой момент.",
        "book_title": "Название книги. Подойдёт и рабочее, например «Крепкий сон за 30 дней».",
        "book_author": "Имя на обложке и в метаданных, например «Анна Иванова».",
        "fonti_file": "Необязательно. Ваши PDF или DOCX (заметки, исследования): ИИ возьмёт идеи и напишет своими словами.",
        "book_genre": "Жанр задаёт структуру: роман (сцены и персонажи), эссе (тезис и доводы) или руководство (процедуры).",
        "book_writing_style": "Тип текста, например научно-популярный, академический или практический. Меняет лексику и детализацию.",
        "book_narrative_style": "Тон текста, например увлекательный, ироничный, технический.",
        "book_tense": "Время повествования: прошедшее (классика) или настоящее (живее).",
        "book_point_of_view": "К кому обращается текст: «ты», «вы» или безличная форма.",
        "book_goal": "Что читатель сможет сделать или почувствовать в конце, например «печь хлеб дома».",
        "book_desired_result": "Конкретный результат, например «вечерний ритуал на каждый день».",
        "book_plot": "О чём книга: сюжет романа, тема эссе или руководства.",
        "book_further_details": "Необязательно: аспекты, примеры, ограничения или темы, которых избегать.",
        "book_personal_voice": "Необязательно: как пишете вы (короткие фразы, ирония, любимые слова) — для книги вашим голосом.",
        "book_personal_material": "Необязательно: ваши случаи, воспоминания или опыт для книги.",
        "book_personal_priorities": "Необязательно: что для вас важнее всего.",
        "book_personal_boundaries": "Необязательно: чего книга не должна говорить или делать.",
    },
    "العربية": {
        "editor_language": "لغة الواجهة والكتاب. يمكنك تغييرها في أي وقت.",
        "book_title": "عنوان الكتاب. يكفي عنوان مؤقت، مثل «نوم هادئ في 30 يوماً».",
        "book_author": "الاسم الذي سيظهر على الغلاف وفي البيانات الوصفية.",
        "fonti_file": "اختياري. ملفات PDF أو DOCX خاصة بك (ملاحظات، أبحاث): يستخرج الذكاء الاصطناعي الأفكار ويكتب بكلماته.",
        "book_genre": "النوع يحدد البنية: رواية (مشاهد وشخصيات)، مقالة (أطروحة وأدلة) أو دليل (إجراءات).",
        "book_writing_style": "نوع النص، مثل تبسيطي أو أكاديمي أو عملي. يغيّر المفردات ومستوى التفاصيل.",
        "book_narrative_style": "نبرة النص، مثل مشوّقة أو ساخرة أو تقنية.",
        "book_tense": "زمن السرد: الماضي (أكثر كلاسيكية) أو المضارع (أكثر مباشرة).",
        "book_point_of_view": "لمن يتوجّه النص: «أنت» أو «أنتم» أو بصيغة غير شخصية.",
        "book_goal": "ما الذي سيستطيع القارئ فعله أو الشعور به في النهاية، مثل «خَبز الخبز في البيت».",
        "book_desired_result": "النتيجة الملموسة المطلوبة، مثل «روتين مسائي لكل ليلة».",
        "book_plot": "عمّ يتحدث الكتاب: حبكة الرواية، أو موضوع المقالة أو الدليل.",
        "book_further_details": "اختياري: جوانب يجب تناولها، أمثلة، قيود أو موضوعات يجب تجنبها.",
        "book_personal_voice": "اختياري: أسلوبك في الكتابة (جمل قصيرة، سخرية، كلمات مفضلة) لكتاب بصوتك.",
        "book_personal_material": "اختياري: حالات أو ذكريات أو تجارب خاصة بك لإدراجها.",
        "book_personal_priorities": "اختياري: ما الأهم بالنسبة إليك.",
        "book_personal_boundaries": "اختياري: ما لا يجب أن يقوله الكتاب أو يفعله.",
    },
    "中文": {
        "editor_language": "界面和图书的语言，可随时更改。",
        "book_title": "书名。可以先用暂定书名，例如《30 天睡个好觉》。",
        "book_author": "显示在封面和元数据中的作者名。",
        "fonti_file": "可选。你自己的 PDF 或 DOCX（笔记、研究）：AI 会提取观点并用自己的话写作。",
        "book_genre": "类型决定结构：小说（场景和人物）、论述类（论点和论据）或手册（操作步骤）。",
        "book_writing_style": "文本类型，例如科普、学术或实用。会改变用词和详细程度。",
        "book_narrative_style": "行文语气，例如引人入胜、幽默、专业。",
        "book_tense": "叙述时态：过去时（更经典）或现在时（更直接）。",
        "book_point_of_view": "文本对谁说话：“你”、“你们”或非人称。",
        "book_goal": "读完后读者能做到或感受到什么，例如“在家烤面包”。",
        "book_desired_result": "你想要的具体成果，例如“每晚可执行的睡前流程”。",
        "book_plot": "这本书讲什么：小说的情节，或论述类、手册的主题。",
        "book_further_details": "可选：要涵盖的方面、例子、限制或需避免的话题。",
        "book_personal_voice": "可选：你的写作方式（短句、幽默、常用词），让书带有你的声音。",
        "book_personal_material": "可选：要写进书里的个人案例、回忆或经历。",
        "book_personal_priorities": "可选：对你来说最重要的内容。",
        "book_personal_boundaries": "可选：书中不能说或不能做的事情。",
    },
}


def aiuto_campo(chiave: str, lingua: str) -> str:
    voci = AIUTI_CAMPI.get(lingua) or AIUTI_CAMPI["English"]
    return voci.get(chiave) or AIUTI_CAMPI["English"].get(chiave, "")


# --------------------------------------------------------------------------
# 5. Visita guidata al primo accesso
# --------------------------------------------------------------------------
# Ogni passo: (selettore CSS dell'elemento da indicare, titolo, testo).
# Selettore vuoto = fumetto al centro della pagina.
SELETTORI_TOUR = (
    "",
    '[data-testid="stSidebar"]',
    ".st-key-avvia_chat_sidebar_subito",
    ".ss-project-panel",
    '[data-testid="stTabs"] [role="tablist"]',
    ".st-key-salva_sessione_manuale",
    "",
)
TOUR = {
    "Italiano": {
        "passi": (
            ("Benvenuto in Scrittore Site 👋", "In un minuto ti mostro dove si trova tutto. Puoi saltare quando vuoi."),
            ("La sidebar", "Qui imposti il libro: lingua, cervello AI, titolo, genere, obiettivo e trama. Su telefono si apre con ☰."),
            ("Il modo più semplice", "La chat guidata ti fa poche domande e compila la sidebar al posto tuo."),
            ("A che punto sei", "Il Centro del progetto mostra i passaggi e ti dice sempre il prossimo passo."),
            ("Il percorso", "Segui i numeri: 0 sidebar, 1 indice, 2 scrivi, 3 anteprima, 4 esporta, 5 formattazione."),
            ("Salva spesso", "Salva sessione conserva tutto nel tuo account. Riapri l'ultimo salvataggio lo recupera."),
            ("Tutto pronto ✨", "Puoi rivedere questa visita dalla sidebar, sotto il video. Buona scrittura!"),
        ),
        "avanti": "Avanti", "indietro": "Indietro", "salta": "Salta", "fine": "Inizia", "rivedi": "🧭 Rivedi la visita guidata",
    },
    "English": {
        "passi": (
            ("Welcome to Scrittore Site 👋", "In one minute I'll show you where everything is. You can skip at any time."),
            ("The sidebar", "Set up your book here: language, AI brain, title, genre, goal and plot. On a phone, open it with ☰."),
            ("The easiest way", "The guided chat asks a few questions and fills in the sidebar for you."),
            ("Where you are", "The Project centre shows the steps and always tells you the next one."),
            ("The path", "Follow the numbers: 0 sidebar, 1 outline, 2 write, 3 preview, 4 export, 5 formatting."),
            ("Save often", "Save session keeps everything in your account. Reopen last save brings it back."),
            ("All set ✨", "You can replay this tour from the sidebar, below the video. Happy writing!"),
        ),
        "avanti": "Next", "indietro": "Back", "salta": "Skip", "fine": "Start", "rivedi": "🧭 Replay the guided tour",
    },
    "Español": {
        "passi": (
            ("Bienvenido a Scrittore Site 👋", "En un minuto te muestro dónde está todo. Puedes saltar cuando quieras."),
            ("La barra lateral", "Aquí configuras el libro: idioma, cerebro IA, título, género, objetivo y trama. En el móvil se abre con ☰."),
            ("La forma más fácil", "El chat guiado te hace pocas preguntas y completa la barra lateral por ti."),
            ("Dónde estás", "El Centro del proyecto muestra los pasos y siempre te indica el siguiente."),
            ("El recorrido", "Sigue los números: 0 barra lateral, 1 índice, 2 escribe, 3 vista previa, 4 exporta, 5 formato."),
            ("Guarda a menudo", "Guardar sesión conserva todo en tu cuenta. Reabrir último guardado lo recupera."),
            ("Todo listo ✨", "Puedes repetir esta visita desde la barra lateral, bajo el vídeo. ¡Buena escritura!"),
        ),
        "avanti": "Siguiente", "indietro": "Atrás", "salta": "Saltar", "fine": "Empezar", "rivedi": "🧭 Repetir la visita guiada",
    },
    "Français": {
        "passi": (
            ("Bienvenue sur Scrittore Site 👋", "En une minute, je vous montre où tout se trouve. Vous pouvez passer à tout moment."),
            ("La barre latérale", "Configurez votre livre ici : langue, cerveau IA, titre, genre, objectif et intrigue. Sur téléphone, ouvrez-la avec ☰."),
            ("Le plus simple", "Le chat guidé pose quelques questions et remplit la barre latérale pour vous."),
            ("Où vous en êtes", "Le Centre du projet montre les étapes et indique toujours la suivante."),
            ("Le parcours", "Suivez les numéros : 0 barre latérale, 1 plan, 2 rédaction, 3 aperçu, 4 export, 5 mise en forme."),
            ("Enregistrez souvent", "Enregistrer la session garde tout dans votre compte. Rouvrir la dernière sauvegarde le récupère."),
            ("C’est prêt ✨", "Vous pouvez revoir cette visite depuis la barre latérale, sous la vidéo. Bonne écriture !"),
        ),
        "avanti": "Suivant", "indietro": "Retour", "salta": "Passer", "fine": "Commencer", "rivedi": "🧭 Revoir la visite guidée",
    },
    "Deutsch": {
        "passi": (
            ("Willkommen bei Scrittore Site 👋", "In einer Minute zeige ich Ihnen, wo alles ist. Sie können jederzeit überspringen."),
            ("Die Seitenleiste", "Hier richten Sie das Buch ein: Sprache, KI-Gehirn, Titel, Genre, Ziel und Handlung. Auf dem Handy öffnen Sie sie mit ☰."),
            ("Am einfachsten", "Der geführte Chat stellt wenige Fragen und füllt die Seitenleiste für Sie aus."),
            ("Wo Sie stehen", "Die Projektzentrale zeigt die Schritte und nennt immer den nächsten."),
            ("Der Ablauf", "Folgen Sie den Nummern: 0 Seitenleiste, 1 Gliederung, 2 Schreiben, 3 Vorschau, 4 Export, 5 Formatierung."),
            ("Oft speichern", "Sitzung speichern sichert alles in Ihrem Konto. Letzte Speicherung öffnen holt es zurück."),
            ("Alles bereit ✨", "Sie können diese Tour in der Seitenleiste unter dem Video erneut starten. Viel Freude beim Schreiben!"),
        ),
        "avanti": "Weiter", "indietro": "Zurück", "salta": "Überspringen", "fine": "Loslegen", "rivedi": "🧭 Tour erneut ansehen",
    },
    "Română": {
        "passi": (
            ("Bine ai venit în Scrittore Site 👋", "Într-un minut îți arăt unde se află totul. Poți sări oricând."),
            ("Bara laterală", "Aici configurezi cartea: limbă, creier AI, titlu, gen, obiectiv și subiect. Pe telefon se deschide cu ☰."),
            ("Cel mai simplu", "Chatul ghidat îți pune câteva întrebări și completează bara laterală în locul tău."),
            ("Unde ai ajuns", "Centrul proiectului arată pașii și îți spune mereu pasul următor."),
            ("Parcursul", "Urmează numerele: 0 bara laterală, 1 cuprins, 2 scrie, 3 previzualizare, 4 export, 5 formatare."),
            ("Salvează des", "Salvează sesiunea păstrează totul în cont. Redeschide ultima salvare îl recuperează."),
            ("Totul e gata ✨", "Poți revedea turul din bara laterală, sub video. Scriere plăcută!"),
        ),
        "avanti": "Înainte", "indietro": "Înapoi", "salta": "Sari", "fine": "Începe", "rivedi": "🧭 Revezi turul ghidat",
    },
    "Русский": {
        "passi": (
            ("Добро пожаловать в Scrittore Site 👋", "За минуту покажу, где что находится. Пропустить можно в любой момент."),
            ("Боковая панель", "Здесь настраивается книга: язык, мозг ИИ, название, жанр, цель и сюжет. На телефоне она открывается кнопкой ☰."),
            ("Проще всего", "Управляемый чат задаст несколько вопросов и заполнит панель за вас."),
            ("Где вы сейчас", "Центр проекта показывает этапы и всегда подсказывает следующий шаг."),
            ("Порядок работы", "Следуйте номерам: 0 панель, 1 оглавление, 2 текст, 3 просмотр, 4 экспорт, 5 форматирование."),
            ("Сохраняйте чаще", "«Сохранить сессию» хранит всё в аккаунте. «Открыть последнее сохранение» возвращает проект."),
            ("Всё готово ✨", "Тур можно пройти снова на боковой панели под видео. Приятной работы!"),
        ),
        "avanti": "Далее", "indietro": "Назад", "salta": "Пропустить", "fine": "Начать", "rivedi": "🧭 Пройти тур снова",
    },
    "العربية": {
        "passi": (
            ("مرحباً بك في Scrittore Site 👋", "في دقيقة واحدة سأريك أين يوجد كل شيء. يمكنك التخطي في أي وقت."),
            ("الشريط الجانبي", "هنا تضبط الكتاب: اللغة، عقل الذكاء الاصطناعي، العنوان، النوع، الهدف والحبكة. على الهاتف يُفتح بزر ☰."),
            ("الطريقة الأسهل", "الدردشة الموجّهة تطرح عليك أسئلة قليلة وتملأ الشريط الجانبي عنك."),
            ("أين وصلت", "مركز المشروع يعرض الخطوات ويخبرك دائماً بالخطوة التالية."),
            ("المسار", "اتبع الأرقام: 0 الشريط الجانبي، 1 الفهرس، 2 الكتابة، 3 المعاينة، 4 التصدير، 5 التنسيق."),
            ("احفظ كثيراً", "حفظ الجلسة يحفظ كل شيء في حسابك. إعادة فتح آخر حفظ يستعيده."),
            ("كل شيء جاهز ✨", "يمكنك إعادة هذه الجولة من الشريط الجانبي تحت الفيديو. كتابة ممتعة!"),
        ),
        "avanti": "التالي", "indietro": "السابق", "salta": "تخطٍّ", "fine": "ابدأ", "rivedi": "🧭 أعد الجولة الإرشادية",
    },
    "中文": {
        "passi": (
            ("欢迎来到 Scrittore Site 👋", "用一分钟带你认识各个区域。你可以随时跳过。"),
            ("侧边栏", "在这里设置图书：语言、AI 大脑、书名、类型、目标和情节。手机上点 ☰ 打开。"),
            ("最简单的方式", "引导式聊天会问几个问题，并替你填写侧边栏。"),
            ("当前进度", "项目中心显示各个步骤，并始终提示下一步。"),
            ("流程", "按数字进行：0 侧边栏、1 目录、2 写作、3 预览、4 导出、5 排版。"),
            ("经常保存", "“保存会话”会把一切保存到账户，“重新打开上次保存”可以找回。"),
            ("准备就绪 ✨", "你可以在侧边栏视频下方重新查看本导览。写作愉快！"),
        ),
        "avanti": "下一步", "indietro": "上一步", "salta": "跳过", "fine": "开始", "rivedi": "🧭 重新查看导览",
    },
}


def dati_tour(lingua: str) -> dict:
    """Testi e selettori della visita guidata, pronti per lo script."""
    voci = TOUR.get(lingua) or TOUR["English"]
    passi = [
        {"sel": sel, "titolo": titolo, "testo": testo}
        for sel, (titolo, testo) in zip(SELETTORI_TOUR, voci["passi"])
    ]
    return {
        "passi": passi, "avanti": voci["avanti"], "indietro": voci["indietro"],
        "salta": voci["salta"], "fine": voci["fine"], "rtl": lingua == "العربية",
    }
