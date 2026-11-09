"""Testi dell'interfaccia dei romanzi nelle 9 lingue di Scrittore Site.

I valori tecnici salvati nel progetto (per esempio il narratore scelto)
restano quelli italiani di ``narrative_prompts``: qui ci sono solo le
etichette mostrate all'utente. Una lingua sconosciuta usa l'italiano.
"""

from __future__ import annotations

from narrative_prompts import NARRATORI, TEMPI_VERBALI, istruzioni_chat_romanzi as _istruzioni_chat_base

LINGUE = ("Italiano", "English", "Español", "Français", "Deutsch", "Română", "Русский", "العربية", "中文")

TESTI: dict[str, dict] = {
    "Italiano": {
        "narratore": "Chi racconta la storia",
        "tempo": "Tempo verbale del racconto",
        "narratore_help": "Prima persona: racconta il protagonista («io»). Terza persona vicina: si segue un personaggio alla volta.",
        "opzioni_narratore": (
            "Terza persona vicina a un personaggio",
            "Prima persona (il protagonista racconta)",
            "Terza persona onnisciente",
            "Terza persona a più punti di vista (uno per scena)",
        ),
        "opzioni_tempo": ("Passato (passato remoto e imperfetto)", "Presente"),
        "riquadro": "🧭 Scaletta e personaggi del romanzo",
        "intro": "Più sono precisi questi due campi, più il romanzo resta coerente. Puoi scriverli a mano o farli proporre all'IA e poi correggerli.",
        "titolo_personaggi": "Personaggi e mondo",
        "help_personaggi": "Nomi, età, aspetto, carattere, relazioni, luoghi, regole del mondo e fatti già stabiliti. L'IA li tratta come canone in ogni sezione.",
        "modello_scheda": "PERSONAGGI\n- Nome: ruolo, età, aspetto, carattere, che cosa vuole, che cosa teme\n- Nome: …\n\nRELAZIONI\n- Nome e Nome: rapporto\n\nLUOGHI E MONDO\n- Luogo: descrizione, regole da rispettare\n\nCRONOLOGIA E FATTI GIÀ STABILITI\n- …",
        "btn_scheda": "🔄 Aggiorna la scheda dai capitoli scritti",
        "desc_scheda": "Legge le sezioni già scritte e propone una scheda aggiornata nel campo qui sopra. Non modifica il manoscritto; puoi correggere la proposta prima di continuare.",
        "attesa_scheda": "Lettura dei capitoli e aggiornamento della scheda...",
        "ok_scheda": "Scheda aggiornata: controllala e correggila se serve.",
        "err_nessuna_sezione": "Scrivi almeno una sezione prima di aggiornare la scheda.",
        "titolo_scaletta": "Scaletta delle scene",
        "formato_scaletta": "Formato: il titolo della voce dell'indice tra parentesi quadre, poi i punti della scena. Esempio: [Capitolo 1: Il lago] seguito da - Marco arriva alla casa…",
        "conteggio": "Scene con scaletta: {n} su {totale}.",
        "btn_scaletta": "✨ Proponi la scaletta delle scene",
        "desc_scaletta": "Propone 3-6 punti per ogni scena dell'indice. I punti già scritti da te restano invariati. Non scrive il libro e non modifica le sezioni esistenti.",
        "attesa_scaletta": "Preparazione della scaletta delle scene...",
        "ok_scaletta": "Scaletta pronta: rileggila e correggila prima di scrivere.",
        "err_scaletta": "La risposta non conteneva una scaletta leggibile. I crediti sono stati riaccreditati: riprova.",
        "err_tecnico": "La richiesta non è riuscita e i crediti sono stati riaccreditati: riprova tra poco.",
    },
    "English": {
        "narratore": "Who tells the story",
        "tempo": "Narrative tense",
        "narratore_help": "First person: the protagonist tells the story (“I”). Close third person: the story follows one character at a time.",
        "opzioni_narratore": (
            "Close third person (one character)",
            "First person (the protagonist tells the story)",
            "Omniscient third person",
            "Third person, multiple points of view (one per scene)",
        ),
        "opzioni_tempo": ("Past tense", "Present tense"),
        "riquadro": "🧭 Novel outline and characters",
        "intro": "The more precise these two fields are, the more consistent the novel stays. Write them yourself or let the AI propose them, then correct them.",
        "titolo_personaggi": "Characters and world",
        "help_personaggi": "Names, age, appearance, personality, relationships, places, rules of the world and facts already established. The AI treats them as canon in every section.",
        "modello_scheda": "CHARACTERS\n- Name: role, age, appearance, personality, what they want, what they fear\n- Name: …\n\nRELATIONSHIPS\n- Name and Name: relationship\n\nPLACES AND WORLD\n- Place: description, rules to respect\n\nTIMELINE AND ESTABLISHED FACTS\n- …",
        "btn_scheda": "🔄 Update the sheet from written chapters",
        "desc_scheda": "Reads the sections already written and proposes an updated sheet in the field above. It does not change the manuscript; you can correct the proposal before continuing.",
        "attesa_scheda": "Reading the chapters and updating the sheet...",
        "ok_scheda": "Sheet updated: check it and correct it if needed.",
        "err_nessuna_sezione": "Write at least one section before updating the sheet.",
        "titolo_scaletta": "Scene outline",
        "formato_scaletta": "Format: the index entry title in square brackets, then the scene points. Example: [Chapter 1: The lake] followed by - Marco arrives at the house…",
        "conteggio": "Scenes with an outline: {n} of {totale}.",
        "btn_scaletta": "✨ Propose the scene outline",
        "desc_scaletta": "Proposes 3-6 points for every scene in the index. Points you have already written stay unchanged. It does not write the book or change existing sections.",
        "attesa_scaletta": "Preparing the scene outline...",
        "ok_scaletta": "Outline ready: read it and correct it before writing.",
        "err_scaletta": "The reply did not contain a readable outline. Your credits have been refunded: please try again.",
        "err_tecnico": "The request failed and your credits have been refunded: please try again shortly.",
    },
    "Español": {
        "narratore": "Quién cuenta la historia",
        "tempo": "Tiempo verbal del relato",
        "narratore_help": "Primera persona: narra el protagonista («yo»). Tercera persona cercana: se sigue a un personaje cada vez.",
        "opzioni_narratore": (
            "Tercera persona cercana a un personaje",
            "Primera persona (narra el protagonista)",
            "Tercera persona omnisciente",
            "Tercera persona con varios puntos de vista (uno por escena)",
        ),
        "opzioni_tempo": ("Pasado (pretérito e imperfecto)", "Presente"),
        "riquadro": "🧭 Escaleta y personajes de la novela",
        "intro": "Cuanto más precisos sean estos dos campos, más coherente será la novela. Puedes escribirlos tú o pedir una propuesta a la IA y luego corregirla.",
        "titolo_personaggi": "Personajes y mundo",
        "help_personaggi": "Nombres, edad, aspecto, carácter, relaciones, lugares, reglas del mundo y hechos ya establecidos. La IA los trata como canon en cada sección.",
        "modello_scheda": "PERSONAJES\n- Nombre: papel, edad, aspecto, carácter, qué quiere, qué teme\n- Nombre: …\n\nRELACIONES\n- Nombre y Nombre: relación\n\nLUGARES Y MUNDO\n- Lugar: descripción, reglas que respetar\n\nCRONOLOGÍA Y HECHOS YA ESTABLECIDOS\n- …",
        "btn_scheda": "🔄 Actualizar la ficha con los capítulos escritos",
        "desc_scheda": "Lee las secciones ya escritas y propone una ficha actualizada en el campo superior. No modifica el manuscrito; puedes corregir la propuesta antes de continuar.",
        "attesa_scheda": "Leyendo los capítulos y actualizando la ficha...",
        "ok_scheda": "Ficha actualizada: revísala y corrígela si hace falta.",
        "err_nessuna_sezione": "Escribe al menos una sección antes de actualizar la ficha.",
        "titolo_scaletta": "Escaleta de escenas",
        "formato_scaletta": "Formato: el título de la entrada del índice entre corchetes y después los puntos de la escena. Ejemplo: [Capítulo 1: El lago] seguido de - Marco llega a la casa…",
        "conteggio": "Escenas con escaleta: {n} de {totale}.",
        "btn_scaletta": "✨ Proponer la escaleta de escenas",
        "desc_scaletta": "Propone 3-6 puntos para cada escena del índice. Los puntos que ya escribiste no cambian. No escribe el libro ni modifica las secciones existentes.",
        "attesa_scaletta": "Preparando la escaleta de escenas...",
        "ok_scaletta": "Escaleta lista: revísala y corrígela antes de escribir.",
        "err_scaletta": "La respuesta no contenía una escaleta legible. Los créditos se han devuelto: inténtalo de nuevo.",
        "err_tecnico": "La solicitud no se completó y los créditos se han devuelto: inténtalo de nuevo en breve.",
    },
    "Français": {
        "narratore": "Qui raconte l'histoire",
        "tempo": "Temps du récit",
        "narratore_help": "Première personne : le protagoniste raconte (« je »). Troisième personne proche : on suit un personnage à la fois.",
        "opzioni_narratore": (
            "Troisième personne proche d'un personnage",
            "Première personne (le protagoniste raconte)",
            "Troisième personne omnisciente",
            "Troisième personne à plusieurs points de vue (un par scène)",
        ),
        "opzioni_tempo": ("Passé (passé simple et imparfait)", "Présent"),
        "riquadro": "🧭 Plan et personnages du roman",
        "intro": "Plus ces deux champs sont précis, plus le roman reste cohérent. Vous pouvez les rédiger vous-même ou les faire proposer par l'IA, puis les corriger.",
        "titolo_personaggi": "Personnages et univers",
        "help_personaggi": "Noms, âge, apparence, caractère, relations, lieux, règles de l'univers et faits déjà établis. L'IA les traite comme canon dans chaque section.",
        "modello_scheda": "PERSONNAGES\n- Nom : rôle, âge, apparence, caractère, ce qu'il veut, ce qu'il craint\n- Nom : …\n\nRELATIONS\n- Nom et Nom : relation\n\nLIEUX ET UNIVERS\n- Lieu : description, règles à respecter\n\nCHRONOLOGIE ET FAITS ÉTABLIS\n- …",
        "btn_scheda": "🔄 Mettre à jour la fiche avec les chapitres écrits",
        "desc_scheda": "Lit les sections déjà écrites et propose une fiche mise à jour dans le champ ci-dessus. Le manuscrit n'est pas modifié ; vous pouvez corriger la proposition avant de continuer.",
        "attesa_scheda": "Lecture des chapitres et mise à jour de la fiche...",
        "ok_scheda": "Fiche mise à jour : vérifiez-la et corrigez-la si nécessaire.",
        "err_nessuna_sezione": "Écrivez au moins une section avant de mettre à jour la fiche.",
        "titolo_scaletta": "Plan des scènes",
        "formato_scaletta": "Format : le titre de l'entrée du sommaire entre crochets, puis les points de la scène. Exemple : [Chapitre 1 : Le lac] suivi de - Marco arrive à la maison…",
        "conteggio": "Scènes avec un plan : {n} sur {totale}.",
        "btn_scaletta": "✨ Proposer le plan des scènes",
        "desc_scaletta": "Propose 3 à 6 points pour chaque scène du sommaire. Les points que vous avez déjà écrits restent inchangés. N'écrit pas le livre et ne modifie pas les sections existantes.",
        "attesa_scaletta": "Préparation du plan des scènes...",
        "ok_scaletta": "Plan prêt : relisez-le et corrigez-le avant d'écrire.",
        "err_scaletta": "La réponse ne contenait pas de plan lisible. Les crédits ont été remboursés : réessayez.",
        "err_tecnico": "La demande a échoué et les crédits ont été remboursés : réessayez dans un instant.",
    },
    "Deutsch": {
        "narratore": "Wer erzählt die Geschichte",
        "tempo": "Erzählzeit",
        "narratore_help": "Ich-Erzähler: Die Hauptfigur erzählt („ich“). Personale Er-Erzählung: Die Geschichte folgt jeweils einer Figur.",
        "opzioni_narratore": (
            "Personale Er-/Sie-Erzählung (nah an einer Figur)",
            "Ich-Erzähler (die Hauptfigur erzählt)",
            "Allwissender Erzähler",
            "Er-/Sie-Erzählung mit mehreren Perspektiven (eine pro Szene)",
        ),
        "opzioni_tempo": ("Vergangenheit (Präteritum)", "Gegenwart (Präsens)"),
        "riquadro": "🧭 Szenenplan und Figuren des Romans",
        "intro": "Je genauer diese beiden Felder sind, desto stimmiger bleibt der Roman. Sie können sie selbst schreiben oder von der KI vorschlagen lassen und dann korrigieren.",
        "titolo_personaggi": "Figuren und Welt",
        "help_personaggi": "Namen, Alter, Aussehen, Charakter, Beziehungen, Orte, Regeln der Welt und bereits feststehende Fakten. Die KI behandelt sie in jedem Abschnitt als Kanon.",
        "modello_scheda": "FIGUREN\n- Name: Rolle, Alter, Aussehen, Charakter, was die Figur will, was sie fürchtet\n- Name: …\n\nBEZIEHUNGEN\n- Name und Name: Beziehung\n\nORTE UND WELT\n- Ort: Beschreibung, einzuhaltende Regeln\n\nZEITLEISTE UND FESTSTEHENDE FAKTEN\n- …",
        "btn_scheda": "🔄 Figurenblatt aus den geschriebenen Kapiteln aktualisieren",
        "desc_scheda": "Liest die bereits geschriebenen Abschnitte und schlägt im Feld oben ein aktualisiertes Figurenblatt vor. Das Manuskript bleibt unverändert; Sie können den Vorschlag vor dem Weiterschreiben korrigieren.",
        "attesa_scheda": "Kapitel werden gelesen und das Figurenblatt wird aktualisiert...",
        "ok_scheda": "Figurenblatt aktualisiert: Bitte prüfen und bei Bedarf korrigieren.",
        "err_nessuna_sezione": "Schreiben Sie mindestens einen Abschnitt, bevor Sie das Figurenblatt aktualisieren.",
        "titolo_scaletta": "Szenenplan",
        "formato_scaletta": "Format: der Titel des Inhaltsverzeichnis-Eintrags in eckigen Klammern, danach die Punkte der Szene. Beispiel: [Kapitel 1: Der See] gefolgt von - Marco kommt am Haus an…",
        "conteggio": "Szenen mit Plan: {n} von {totale}.",
        "btn_scaletta": "✨ Szenenplan vorschlagen",
        "desc_scaletta": "Schlägt für jede Szene des Inhaltsverzeichnisses 3-6 Punkte vor. Bereits von Ihnen geschriebene Punkte bleiben unverändert. Das Buch wird nicht geschrieben und vorhandene Abschnitte werden nicht geändert.",
        "attesa_scaletta": "Szenenplan wird vorbereitet...",
        "ok_scaletta": "Szenenplan bereit: Bitte vor dem Schreiben lesen und korrigieren.",
        "err_scaletta": "Die Antwort enthielt keinen lesbaren Szenenplan. Die Credits wurden erstattet: Bitte erneut versuchen.",
        "err_tecnico": "Die Anfrage ist fehlgeschlagen und die Credits wurden erstattet: Bitte gleich erneut versuchen.",
    },
    "Română": {
        "narratore": "Cine spune povestea",
        "tempo": "Timpul verbal al narațiunii",
        "narratore_help": "Persoana întâi: povestește protagonistul („eu”). Persoana a treia apropiată: povestea urmărește câte un personaj.",
        "opzioni_narratore": (
            "Persoana a treia, aproape de un personaj",
            "Persoana întâi (povestește protagonistul)",
            "Persoana a treia omniscientă",
            "Persoana a treia cu mai multe perspective (una pe scenă)",
        ),
        "opzioni_tempo": ("Trecut", "Prezent"),
        "riquadro": "🧭 Planul scenelor și personajele romanului",
        "intro": "Cu cât aceste două câmpuri sunt mai precise, cu atât romanul rămâne mai coerent. Le poți scrie singur sau le poți cere IA, apoi le corectezi.",
        "titolo_personaggi": "Personaje și lume",
        "help_personaggi": "Nume, vârstă, aspect, caracter, relații, locuri, regulile lumii și fapte deja stabilite. IA le tratează drept canon în fiecare secțiune.",
        "modello_scheda": "PERSONAJE\n- Nume: rol, vârstă, aspect, caracter, ce vrea, de ce se teme\n- Nume: …\n\nRELAȚII\n- Nume și Nume: relație\n\nLOCURI ȘI LUME\n- Loc: descriere, reguli de respectat\n\nCRONOLOGIE ȘI FAPTE STABILITE\n- …",
        "btn_scheda": "🔄 Actualizează fișa din capitolele scrise",
        "desc_scheda": "Citește secțiunile deja scrise și propune o fișă actualizată în câmpul de mai sus. Nu modifică manuscrisul; poți corecta propunerea înainte să continui.",
        "attesa_scheda": "Se citesc capitolele și se actualizează fișa...",
        "ok_scheda": "Fișa a fost actualizată: verific-o și corecteaz-o dacă e nevoie.",
        "err_nessuna_sezione": "Scrie cel puțin o secțiune înainte de a actualiza fișa.",
        "titolo_scaletta": "Planul scenelor",
        "formato_scaletta": "Format: titlul intrării din cuprins între paranteze drepte, apoi punctele scenei. Exemplu: [Capitolul 1: Lacul] urmat de - Marco ajunge la casă…",
        "conteggio": "Scene cu plan: {n} din {totale}.",
        "btn_scaletta": "✨ Propune planul scenelor",
        "desc_scaletta": "Propune 3-6 puncte pentru fiecare scenă din cuprins. Punctele scrise deja de tine rămân neschimbate. Nu scrie cartea și nu modifică secțiunile existente.",
        "attesa_scaletta": "Se pregătește planul scenelor...",
        "ok_scaletta": "Planul este gata: recitește-l și corectează-l înainte de a scrie.",
        "err_scaletta": "Răspunsul nu conținea un plan lizibil. Creditele au fost returnate: încearcă din nou.",
        "err_tecnico": "Cererea nu a reușit, iar creditele au fost returnate: încearcă din nou în curând.",
    },
    "Русский": {
        "narratore": "Кто рассказывает историю",
        "tempo": "Время повествования",
        "narratore_help": "Первое лицо: рассказывает главный герой («я»). Близкое третье лицо: повествование следует за одним персонажем.",
        "opzioni_narratore": (
            "Третье лицо, близко к одному персонажу",
            "Первое лицо (рассказывает главный герой)",
            "Всезнающий рассказчик в третьем лице",
            "Третье лицо с несколькими точками зрения (одна на сцену)",
        ),
        "opzioni_tempo": ("Прошедшее время", "Настоящее время"),
        "riquadro": "🧭 План сцен и персонажи романа",
        "intro": "Чем точнее эти два поля, тем последовательнее роман. Их можно написать самому или попросить ИИ предложить вариант, а затем исправить.",
        "titolo_personaggi": "Персонажи и мир",
        "help_personaggi": "Имена, возраст, внешность, характер, отношения, места, правила мира и уже установленные факты. ИИ считает их каноном в каждом разделе.",
        "modello_scheda": "ПЕРСОНАЖИ\n- Имя: роль, возраст, внешность, характер, чего хочет, чего боится\n- Имя: …\n\nОТНОШЕНИЯ\n- Имя и Имя: отношения\n\nМЕСТА И МИР\n- Место: описание, правила, которые нужно соблюдать\n\nХРОНОЛОГИЯ И УСТАНОВЛЕННЫЕ ФАКТЫ\n- …",
        "btn_scheda": "🔄 Обновить карточку по написанным главам",
        "desc_scheda": "Читает уже написанные разделы и предлагает обновлённую карточку в поле выше. Рукопись не меняется; вы можете исправить предложение, прежде чем продолжить.",
        "attesa_scheda": "Чтение глав и обновление карточки...",
        "ok_scheda": "Карточка обновлена: проверьте её и при необходимости исправьте.",
        "err_nessuna_sezione": "Напишите хотя бы один раздел, прежде чем обновлять карточку.",
        "titolo_scaletta": "План сцен",
        "formato_scaletta": "Формат: название пункта оглавления в квадратных скобках, затем пункты сцены. Пример: [Глава 1: Озеро], затем - Марко приезжает в дом…",
        "conteggio": "Сцен с планом: {n} из {totale}.",
        "btn_scaletta": "✨ Предложить план сцен",
        "desc_scaletta": "Предлагает 3-6 пунктов для каждой сцены оглавления. Уже написанные вами пункты не меняются. Книга не пишется, существующие разделы не изменяются.",
        "attesa_scaletta": "Подготовка плана сцен...",
        "ok_scaletta": "План готов: прочитайте и исправьте его перед написанием.",
        "err_scaletta": "Ответ не содержал читаемого плана. Кредиты возвращены: попробуйте ещё раз.",
        "err_tecnico": "Запрос не выполнен, кредиты возвращены: попробуйте ещё раз чуть позже.",
    },
    "العربية": {
        "narratore": "من يروي القصة",
        "tempo": "زمن السرد",
        "narratore_help": "ضمير المتكلم: يروي البطل القصة («أنا»). الغائب القريب: تتبع القصة شخصية واحدة في كل مرة.",
        "opzioni_narratore": (
            "ضمير الغائب قريباً من شخصية واحدة",
            "ضمير المتكلم (يروي البطل)",
            "راوٍ عليم بضمير الغائب",
            "ضمير الغائب بوجهات نظر متعددة (واحدة لكل مشهد)",
        ),
        "opzioni_tempo": ("الزمن الماضي", "الزمن المضارع"),
        "riquadro": "🧭 مخطط المشاهد وشخصيات الرواية",
        "intro": "كلما كان هذان الحقلان أدق، بقيت الرواية أكثر اتساقاً. يمكنك كتابتهما بنفسك أو طلب اقتراح من الذكاء الاصطناعي ثم تصحيحه.",
        "titolo_personaggi": "الشخصيات والعالم",
        "help_personaggi": "الأسماء والعمر والمظهر والطباع والعلاقات والأماكن وقواعد العالم والحقائق الثابتة. يعاملها الذكاء الاصطناعي كمرجع ثابت في كل قسم.",
        "modello_scheda": "الشخصيات\n- الاسم: الدور، العمر، المظهر، الطباع، ماذا يريد، ممّ يخاف\n- الاسم: …\n\nالعلاقات\n- الاسم والاسم: العلاقة\n\nالأماكن والعالم\n- المكان: الوصف، القواعد الواجب احترامها\n\nالتسلسل الزمني والحقائق الثابتة\n- …",
        "btn_scheda": "🔄 حدّث البطاقة من الفصول المكتوبة",
        "desc_scheda": "يقرأ الأقسام المكتوبة ويقترح بطاقة محدثة في الحقل أعلاه. لا يغيّر المخطوطة، ويمكنك تصحيح الاقتراح قبل المتابعة.",
        "attesa_scheda": "جارٍ قراءة الفصول وتحديث البطاقة...",
        "ok_scheda": "تم تحديث البطاقة: راجعها وصححها إذا لزم الأمر.",
        "err_nessuna_sezione": "اكتب قسماً واحداً على الأقل قبل تحديث البطاقة.",
        "titolo_scaletta": "مخطط المشاهد",
        "formato_scaletta": "الصيغة: عنوان بند الفهرس بين قوسين معقوفين، ثم نقاط المشهد. مثال: [الفصل 1: البحيرة] ثم - يصل ماركو إلى المنزل…",
        "conteggio": "مشاهد لها مخطط: {n} من {totale}.",
        "btn_scaletta": "✨ اقترح مخطط المشاهد",
        "desc_scaletta": "يقترح من 3 إلى 6 نقاط لكل مشهد في الفهرس. تبقى النقاط التي كتبتها كما هي. لا يكتب الكتاب ولا يغيّر الأقسام الموجودة.",
        "attesa_scaletta": "جارٍ إعداد مخطط المشاهد...",
        "ok_scaletta": "المخطط جاهز: راجعه وصححه قبل الكتابة.",
        "err_scaletta": "لم يتضمن الرد مخططاً قابلاً للقراءة. تمت إعادة الأرصدة: حاول مرة أخرى.",
        "err_tecnico": "تعذر تنفيذ الطلب وتمت إعادة الأرصدة: حاول مرة أخرى بعد قليل.",
    },
    "中文": {
        "narratore": "谁来讲述故事",
        "tempo": "叙事时态",
        "narratore_help": "第一人称：由主人公讲述（“我”）。贴近的第三人称：每次跟随一个人物。",
        "opzioni_narratore": (
            "贴近某个人物的第三人称",
            "第一人称（由主人公讲述）",
            "全知第三人称",
            "多视角第三人称（每个场景一个视角）",
        ),
        "opzioni_tempo": ("过去时", "现在时"),
        "riquadro": "🧭 小说场景大纲与人物",
        "intro": "这两个字段越准确，小说就越连贯。你可以自己填写，也可以让 AI 提出建议后再修改。",
        "titolo_personaggi": "人物与世界",
        "help_personaggi": "姓名、年龄、外貌、性格、关系、地点、世界规则以及已经确定的事实。AI 会在每个章节中把它们视为既定设定。",
        "modello_scheda": "人物\n- 姓名：角色、年龄、外貌、性格、想要什么、害怕什么\n- 姓名：…\n\n关系\n- 姓名与姓名：关系\n\n地点与世界\n- 地点：描述、需要遵守的规则\n\n时间线与已确定的事实\n- …",
        "btn_scheda": "🔄 根据已写章节更新人物卡",
        "desc_scheda": "读取已写好的章节，并在上方字段中提出更新后的人物卡。不会修改手稿；继续之前你可以修改建议。",
        "attesa_scheda": "正在阅读章节并更新人物卡...",
        "ok_scheda": "人物卡已更新：请检查，必要时修改。",
        "err_nessuna_sezione": "更新人物卡之前，请至少写完一个章节。",
        "titolo_scaletta": "场景大纲",
        "formato_scaletta": "格式：方括号中写目录条目的标题，然后列出场景要点。示例：[第1章：湖] 之后写 - 马可来到房子…",
        "conteggio": "已有大纲的场景：{n} / {totale}。",
        "btn_scaletta": "✨ 提出场景大纲",
        "desc_scaletta": "为目录中的每个场景提出 3-6 个要点。你已写好的要点保持不变。不会撰写书籍，也不会修改已有章节。",
        "attesa_scaletta": "正在准备场景大纲...",
        "ok_scaletta": "大纲已准备好：写作前请阅读并修改。",
        "err_scaletta": "回复中没有可读的大纲。积分已退还：请重试。",
        "err_tecnico": "请求未成功，积分已退还：请稍后重试。",
    },
}


def testo(chiave: str, lingua: str, **valori) -> str:
    """Testo dell'interfaccia nella lingua scelta (italiano se manca)."""
    voce = TESTI.get(lingua, TESTI["Italiano"]).get(chiave, TESTI["Italiano"][chiave])
    return voce.format(**valori) if valori and isinstance(voce, str) else voce


def etichetta_narratore(valore: str, lingua: str) -> str:
    """Mostra il narratore salvato (valore tecnico italiano) nella lingua scelta."""
    if valore in NARRATORI:
        return testo("opzioni_narratore", lingua)[NARRATORI.index(valore)]
    return valore


def etichetta_tempo(valore: str, lingua: str) -> str:
    """Mostra il tempo verbale salvato (valore tecnico italiano) nella lingua scelta."""
    if valore in TEMPI_VERBALI:
        return testo("opzioni_tempo", lingua)[TEMPI_VERBALI.index(valore)]
    return valore


def istruzioni_chat_romanzi(lingua: str) -> str:
    """Regole della chat guidata per i romanzi, con le scelte nella lingua dell'utente.

    Le etichette della scheda e i valori dei menu restano quelli tecnici
    italiani (sono gli identificatori della sidebar); la chat però deve
    presentare le opzioni all'utente con i nomi della sua lingua.
    """
    base = _istruzioni_chat_base()
    if lingua not in TESTI or lingua == "Italiano":
        return base
    corrispondenze = [
        f"- «{testo('opzioni_narratore', lingua)[i]}» = {valore}" for i, valore in enumerate(NARRATORI)
    ] + [
        f"- «{testo('opzioni_tempo', lingua)[i]}» = {valore}" for i, valore in enumerate(TEMPI_VERBALI)
    ]
    return base + f"""

LINGUA DELL'UTENTE: {lingua}
Quando parli con l'utente di narratore e tempo verbale, usa questi nomi nella sua lingua.
Nella scheda finale scrivi invece il valore tecnico italiano corrispondente (a destra del segno =):
""" + "\n".join(corrispondenze) + f"""
PERSONAGGI E MONDO va scritto in {lingua}, come gli altri valori descrittivi."""
