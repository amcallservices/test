"""Testi delle guide dell'area riservata (versione 7x)."""

IT = {
    "titolo": "Guida area riservata Scrittore Site",
    "sottotitolo": "Istruzioni aggiornate per progettare, scrivere, controllare, salvare ed esportare un libro",
    "versione": "versione 7x",
    "area": "Area riservata · versione 7x",
    "nota_copertina": "Questa guida spiega le funzioni disponibili dopo l'accesso. Non include la home pubblica, "
                      "la registrazione o il pagamento esterno. I costi mostrati nell'app prima di ogni azione "
                      "sono sempre quelli da considerare.",
    "novita": "<b>Novità della versione 7x</b><br/>"
              "• I due cervelli si chiamano ora <b>Cervello costoso</b> e <b>Cervello economico</b>.<br/>"
              "• Nuovo <b>Progetto del libro</b> per ogni genere: scaletta, verità nascosta e semi per i romanzi, "
              "tesi per i saggi, obiettivi e prerequisiti per i manuali.<br/>"
              "• <b>Scheda di coerenza</b> che si aggiorna da sola dopo ogni sezione e <b>revisione del capitolo</b>.<br/>"
              "• Per i romanzi: scelta di <b>chi racconta</b> e del <b>tempo verbale</b>, istruzioni di scrittura dedicate.<br/>"
              "• La <b>Chat guidata</b> compila in automatico anche il progetto del libro.<br/>"
              "• Dati incerti segnati con <b>[DA VERIFICARE]</b> e nuovi consigli nel controllo finale.",
    "capitoli": [
        {
            "titolo": "Orientamento",
            "intro": "L'area riservata organizza tutto il libro in un solo progetto: brief, progetto del libro, indice, "
                     "manoscritto, fonti, immagini e controlli. Puoi leggere e modificare i testi manualmente in ogni momento.",
            "blocchi": [
                ("h2", "Le zone della pagina"),
                ("tabella", ["Area", "A cosa serve"], [
                    ["Sidebar", "Configura l'account, il cervello AI e il brief editoriale del libro."],
                    ["Centro del progetto", "Mostra Brief, Indice, Manoscritto, Fonti e il prossimo passo consigliato. Non modifica nulla."],
                    ["Centro operativo", "Raccoglie la Chat della nicchia e le sezioni 0-5. Segui il percorso oppure apri direttamente ciò che ti serve."],
                ], [0.28, 0.72]),
                ("h2", "Il percorso consigliato"),
                ("punti", [
                    "Se vuoi, usa prima la Chat della nicchia per ragionare sul mercato.",
                    "Apri la sezione 0 e usa la Chat guidata: prepara il brief e compila da sola anche il progetto del libro.",
                    "Applica la scheda alla sidebar, scegli il cervello e genera l'indice.",
                    "In Scrivi il libro controlla il riquadro <b>Progetto del libro</b>, poi scrivi una sezione o tutto il libro.",
                    "Rivedi i capitoli, controlla Anteprima e il report Pronto per pubblicare, salva la sessione ed esporta.",
                ]),
            ],
        },
        {
            "titolo": "Sidebar account e progetto",
            "intro": "La sidebar contiene la lingua, il cervello AI, il saldo e il brief. Le personalizzazioni del libro "
                     "restano facoltative e non devono bloccare la creazione dell'indice.",
            "blocchi": [
                ("h2", "Comandi account"),
                ("tabella", ["Comando", "Cosa fa", "Quando usarlo"], [
                    ["Aggiorna saldo crediti", "Rilegge il saldo reale dell'account.", "Dopo un acquisto o un premio referral."],
                    ["Ricarica crediti", "Apre pacchetti e pagamento sicuro.", "Quando vuoi acquistare crediti."],
                    ["Invita e guadagna crediti", "Mostra link referral, inviti e premi maturati.", "Per condividere il software."],
                    ["Esci", "Salva una fotografia aggiornata del progetto e chiude la sessione.", "Attendi la schermata di accesso."],
                    ["Reset progetto", "Cancella il progetto aperto: sidebar, indice, testi, fonti, immagini, memoria e cache.", "Solo per iniziare davvero un progetto nuovo."],
                ], [0.24, 0.44, 0.32]),
                ("h2", "Lingua e cervello AI"),
                ("punti", [
                    "Scegli la lingua prima di creare indice e manoscritto: etichette, chat, prompt e testo seguono quella lingua. "
                    "Sono disponibili 9 lingue.",
                    "<b>Cervello costoso</b>: percorso completo, incluse ricerca web, verifica copyright web e controllo fatti online.",
                    "<b>Cervello economico</b>: stesso percorso di scrittura con consumi più leggeri; le funzioni web restano "
                    "disponibili solo con il Cervello costoso.",
                    "Apri il tariffario sotto il cervello selezionato. Il preventivo visualizzato prima dell'avvio prevale sempre su esempi o guide.",
                    "Con il Cervello economico le piccole operazioni possono essere conteggiate in unità: tre unità corrispondono a un credito.",
                ]),
                ("h2", "Il brief editoriale"),
                ("tabella", ["Gruppo", "Campi", "Perché servono"], [
                    ["Identità", "Titolo e autore", "Intestazione, esportazioni e metadati."],
                    ["Direzione", "Genere, tipologia, stile, ritmo", "Tono, struttura e profondità della scrittura."],
                    ["Punto di vista", "Saggi e manuali: Tu, Voi, Noi o Impersonale. Romanzi: <b>chi racconta</b> (prima persona, "
                     "terza persona vicina, onnisciente, più punti di vista) e <b>tempo verbale</b> (passato o presente).",
                     "Mantiene la stessa voce in tutto il libro."],
                    ["Obiettivo", "Argomento o trama, lettore, risultato desiderato", "Direzione concreta dell'indice e delle sezioni."],
                    ["Approfondimenti", "Vincoli, esempi, fatti, destinatari", "Informazioni utili che non rientrano altrove."],
                    ["Lunghezza", "Compatto, Standard KDP, Approfondito", "Pianifica sezioni e pagine senza aggiungere riempitivi."],
                ], [0.18, 0.46, 0.36]),
            ],
        },
        {
            "titolo": "Chat della nicchia e Chat guidata",
            "intro": "Le due chat sono facoltative e hanno ruoli diversi. Usano sempre il Cervello costoso e la lingua scelta; "
                     "il costo della risposta è mostrato nell'interfaccia prima dell'uso.",
            "blocchi": [
                ("h2", "Chat della nicchia"),
                ("punti", [
                    "Serve per confrontarsi su lettore, mercato, domanda, concorrenza e opportunità editoriale.",
                    "Non modifica sidebar, indice o manoscritto: alla fine produce un prompt da copiare nella Chat guidata.",
                ]),
                ("h2", "Sezione 0 · Chat guidata"),
                ("punti", [
                    "Descrivi l'idea, anche in una frase. La chat fa solo le domande utili e chiede sempre se vuoi personalizzare il libro.",
                    "Prepara una scheda con tutti i campi della sidebar e, <b>in automatico</b>, anche il progetto del libro:",
                    "<b>romanzi</b>: chi racconta, tempo verbale, personaggi e mondo, verità nascosta con la cronologia, mappa dei semi;",
                    "<b>saggi</b>: tesi centrale, problema del lettore e idee chiave;",
                    "<b>manuali</b>: obiettivi di apprendimento, prerequisiti e apparati utili.",
                    "Applica la scheda riempiendo solo i campi vuoti oppure sostituendo quelli esistenti. Controlla la proposta prima di applicarla.",
                    "La chat non inventa esperienze personali attribuite a te; nelle biografie usa solo fatti reali noti.",
                ]),
                ("h2", "Personalizza il tuo libro"),
                ("tabella", ["Campo", "Uso"], [
                    ["Voce, materiale, priorità e confini personali", "Rendono il progetto più individuale quando sono pertinenti."],
                    ["Modalità checkpoint", "Sceglie se la stesura completa deve fermarsi prima delle Parti o della conclusione."],
                    ["Note checkpoint", "Scrivi quale scelta vuoi rivedere durante una pausa. Lascia vuoto se non serve."],
                ], [0.38, 0.62]),
            ],
        },
        {
            "titolo": "Fonti, memoria e coerenza",
            "intro": "Fonti, memoria e scheda di coerenza mantengono il libro ordinato e coerente. Non sostituiscono la "
                     "verifica dell'utente né autorizzano a copiare contenuti protetti.",
            "blocchi": [
                ("h2", "Fonti opzionali"),
                ("punti", [
                    "Carica PDF o DOCX: il software ricava una mappa concettuale per orientare indice e testo, senza riprendere frasi delle fonti.",
                    "Rigenera fonti web: il sistema conserva solo le fonti utili al brief.",
                    "Le fonti guidano il lavoro e i controlli; non diventano automaticamente bibliografia o testo pubblicato.",
                ]),
                ("h2", "Memoria editoriale e continuità"),
                ("punti", [
                    "Brief, progetto, indice, sezioni scritte e modifiche approvate alimentano una memoria editoriale strutturata.",
                    "Ogni nuova sezione riparte <b>dal finale</b> della sezione precedente, per evitare salti e ripetizioni.",
                    "La <b>scheda di coerenza</b> si aggiorna da sola dopo ogni sezione: dove sono i personaggi e cosa sanno, "
                    "idee e termini già spiegati, promesse e misteri ancora aperti. Puoi correggerla nel riquadro Progetto del libro.",
                    "Se modifichi un testo a mano, salva la sessione affinché il progetto conservi la versione aggiornata.",
                ]),
                ("h2", "Salvataggio e recupero"),
                ("tabella", ["Pulsante", "Cosa fa"], [
                    ["Salva sessione", "Salva nel tuo account sidebar, progetto, indice, sezioni, fonti, immagini e memoria."],
                    ["Riaggiorna all'ultima stesura", "Ripristina l'ultima fotografia salvata. Usalo dopo login, logout, refresh o cambio dispositivo."],
                    ["Aggiorna pagina", "Ricarica l'interfaccia. Dopo modifiche importanti, salva prima la sessione."],
                    ["Esci", "Tenta il salvataggio finale prima di chiudere. Per una copia portabile usa anche l'esportazione CSV."],
                ], [0.32, 0.68]),
            ],
        },
        {
            "titolo": "Indice professionale",
            "intro": "La sezione 1 trasforma brief e progetto in una struttura modificabile. L'indice comprende anche la "
                     "Prefazione e definisce le sezioni disponibili nell'editor.",
            "blocchi": [
                ("h2", "Cosa fanno i comandi"),
                ("tabella", ["Comando", "Risultato"], [
                    ["Genera indice professionale", "Studia brief, progetto del libro e, se attivata, la ricerca. Produce un indice gerarchico con Prefazione."],
                    ["Barra di avanzamento", "Mostra la fase della generazione. Se non appare un indice utilizzabile, non cancella il progetto esistente."],
                    ["Voto o revisione dell'indice", "Evidenzia miglioramenti possibili senza aggiungere voci inutili."],
                    ["Salva e sincronizza capitoli", "Rende le voci dell'indice disponibili in Scrittura, Anteprima ed esportazione."],
                    ["Modifica manuale", "Puoi correggere titoli e struttura. Salva e sincronizza dopo la modifica."],
                ], [0.32, 0.68]),
                ("h2", "Struttura e qualità"),
                ("punti", [
                    "Nei romanzi l'indice segue un arco in tre atti: incidente scatenante entro il 10%, svolta al 25%, "
                    "ribaltamento a metà, punto più basso al 75%, poi climax ed epilogo.",
                    "Se il progetto contiene una mappa dei semi, i capitoli indicati devono esistere nell'indice.",
                    "Compatto mira a un libro breve, Standard KDP a un manoscritto medio, Approfondito a un trattamento più esteso. "
                    "Il sistema non aggiunge capitoli inutili solo per raggiungere un numero di pagine.",
                ]),
            ],
        },
        {
            "titolo": "Progetto del libro",
            "intro": "Nella sezione 2, il riquadro <b>Progetto del libro</b> raccoglie il piano che guida ogni sezione. "
                     "Cambia in base al genere ed è compilato in automatico dalla Chat guidata; puoi correggerlo quando vuoi.",
            "blocchi": [
                ("h2", "Campi per tipo di libro"),
                ("tabella", ["Tipo", "Campi", "Come li usa l'IA"], [
                    ["Romanzi", "Personaggi e mondo · Verità nascosta e cronologia · Mappa dei semi",
                     "Rispetta personaggi e luoghi come canone, non rivela la verità prima del tempo, introduce e risolve "
                     "ogni seme nelle sezioni indicate."],
                    ["Saggi", "Tesi centrale e idee chiave", "Ogni capitolo sviluppa idea, prove, obiezione e sintesi al servizio della tesi."],
                    ["Manuali", "Obiettivi di apprendimento e prerequisiti", "Procede dal semplice al complesso, senza usare concetti non ancora spiegati."],
                    ["Tutti", "Scaletta delle sezioni · Scheda di coerenza", "Segue i punti della scaletta e non contraddice la scheda."],
                ], [0.14, 0.34, 0.52]),
                ("h2", "Comandi del riquadro"),
                ("tabella", ["Comando", "Cosa fa"], [
                    ["Proponi il progetto completo", "Compila i campi vuoti e la scaletta di ogni sezione in una sola richiesta. "
                     "Ciò che hai già scritto resta invariato."],
                    ["Aggiorna la scheda dai capitoli scritti", "Solo romanzi: aggiorna personaggi e mondo leggendo le sezioni già scritte."],
                    ["Scheda di coerenza", "Si aggiorna da sola dopo ogni sezione scritta. Non serve premere nulla."],
                    ["Rivedi il capitolo", "Un editor rilegge il capitolo scelto e segnala incoerenze, ripetizioni, punti deboli "
                     "e dati da verificare. Non modifica il testo."],
                ], [0.36, 0.64]),
                ("h2", "Formato della mappa dei semi"),
                ("punti", [
                    "Un seme per riga: <i>- La lettera del padre | compare: Capitolo 2 | si risolve: Capitolo 11</i>.",
                    "Il formato è riconosciuto in tutte le lingue del sito (per esempio <i>appears / resolves</i> in inglese).",
                ]),
            ],
        },
        {
            "titolo": "Scrittura e Quiz",
            "intro": "Nella sezione 2 scrivi una voce alla volta o avvii la stesura completa. Il testo creato resta modificabile dall'editor professionale.",
            "blocchi": [
                ("h2", "Scrivere una sezione"),
                ("punti", [
                    "Scegli la sezione e premi Scrivi contenuto dettagliato. Il risultato viene salvato e appare nell'editor e nell'anteprima.",
                    "Ogni sezione riceve progetto, scaletta, scheda di coerenza e la struttura del suo genere: aggancio in apertura "
                    "di capitolo e motivo per continuare in chiusura; nei saggi prove e obiezioni; nei manuali passi con il risultato "
                    "atteso, riepilogo ed esercizio a fine capitolo.",
                    "I romanzi usano istruzioni di scrittura dedicate: scene, dialoghi, voce narrante coerente, nessuna checklist. "
                    "In italiano i dialoghi usano le caporali «…».",
                    "Le lunghezze sono flessibili: una scena breve e intensa non viene allungata con riempitivi.",
                    "Rielabora con IA migliora solo la sezione selezionata secondo una richiesta precisa.",
                ]),
                ("h2", "Dati da verificare"),
                ("punti", [
                    "Nei saggi e nei manuali un dato non certo viene segnato con <b>[DA VERIFICARE]</b> invece di essere inventato.",
                    "Controlla ogni dato segnato e cancella il segno quando è verificato. Word e PDF lo tolgono comunque.",
                ]),
                ("h2", "Scrivi tutto il libro"),
                ("punti", [
                    "Se la scaletta manca, il software prepara prima il progetto del libro in automatico (costo indicato nel preventivo).",
                    "Poi lavora sezione per sezione, compresa la Prefazione; la barra mostra avanzamento e sezione corrente.",
                    "Pausa conserva quanto completato; Riprendi continua dalle sezioni mancanti; Stop definitivo lascia intatti indice e testi.",
                ]),
                ("h2", "Modifiche manuali"),
                ("punti", [
                    "Puoi riscrivere direttamente un testo nell'editor. Salva sessione dopo una modifica importante.",
                    "Se modifichi l'indice, sincronizzalo di nuovo.",
                ]),
            ],
        },
        {
            "titolo": "Anteprima",
            "intro": "La sezione 3 serve per leggere il libro come un manoscritto continuo prima dell'esportazione.",
            "blocchi": [
                ("punti", [
                    "Usa l'indice cliccabile per raggiungere una sezione, la ricerca nel manoscritto e il lettore vocale per ascoltare il testo.",
                    "La stima pagine usa le parole già scritte e una previsione prudente delle sezioni mancanti. È un indicatore, non una promessa.",
                    "Le modifiche manuali e le sezioni create sono visibili qui dopo il salvataggio e la sincronizzazione dell'indice.",
                ]),
            ],
        },
        {
            "titolo": "Importa Esporta Copyright",
            "intro": "La sezione 4 raccoglie backup, recupero, controlli e file finali. Esportare è sempre possibile, ma un "
                     "avviso editoriale invita a correggere prima della pubblicazione.",
            "blocchi": [
                ("h2", "CSV completo"),
                ("tabella", ["Comando", "Cosa fa"], [
                    ["Esporta progetto completo CSV", "Scarica sidebar, progetto del libro, indice, sezioni, fonti, immagini e memoria come copia portabile."],
                    ["Importa e ripristina progetto", "Carica un CSV esportato dal software e ripristina il progetto nella pagina corrente."],
                    ["Controlla completezza", "Segnala sezioni vuote o incomplete. Non riscrive automaticamente il libro."],
                ], [0.34, 0.66]),
                ("h2", "Pronto per pubblicare"),
                ("punti", [
                    "Struttura, manoscritto e frasi concluse devono essere verificati.",
                    "Finché restano dati <b>[DA VERIFICARE]</b>, il file esportato è segnalato come bozza e trovi l'elenco delle frasi da controllare.",
                    "<b>Consigli editoriali</b> (non bloccano l'esportazione): semi senza risoluzione o con capitoli inesistenti, misteri "
                    "ancora aperti secondo la scheda di coerenza, espressioni ripetute più di 3 volte, frasi fatte, dialoghi italiani senza caporali.",
                ]),
                ("h2", "Originalità, copyright e KDP"),
                ("punti", [
                    "Il controllo originalità locale confronta il manoscritto solo con PDF e DOCX caricati.",
                    "Il controllo copyright web (Cervello costoso) segnala somiglianze o punti da verificare. Non certifica legalmente l'originalità.",
                    "Il controllo conformità KDP consulta le linee guida ufficiali e produce un report; non garantisce la pubblicazione.",
                ]),
                ("h2", "Word e PDF"),
                ("punti", [
                    "Scarica Word per continuare la revisione in un editor esterno, oppure PDF per una versione impaginata. "
                    "Controlla sempre il file finale prima di inviarlo a una piattaforma.",
                ]),
            ],
        },
        {
            "titolo": "Formattazione e metadati KDP",
            "intro": "La sezione 5 prepara materiali utili prima della pubblicazione finale.",
            "blocchi": [
                ("tabella", ["Funzione", "Cosa fa"], [
                    ["Genera metadati dettagliati", "Analizza un manoscritto caricato e propone descrizione marketing e sette keyword a coda lunga nella lingua scelta."],
                    ["Formatta documento", "Per un DOCX applica impostazioni 6 x 9, margini, font, titoli, rientri, testo giustificato e numeri pagina."],
                    ["Scarica Word 6 x 9", "Scarica il DOCX formattato. Verifica sempre il risultato nel programma di impaginazione o nel controllo KDP."],
                ], [0.32, 0.68]),
            ],
        },
        {
            "titolo": "Crediti, sicurezza e buone pratiche",
            "intro": "L'app mostra un preventivo prima delle azioni AI a pagamento. Il preventivo visualizzato prevale sempre su questa guida.",
            "blocchi": [
                ("h2", "Cosa consuma crediti"),
                ("tabella", ["Azione", "Crediti indicativi"], [
                    ["Leggere, modificare, salvare, importare, esportare", "Gratuito"],
                    ["Scheda di coerenza automatica dopo ogni sezione", "Gratuito"],
                    ["Proponi il progetto completo", "2 crediti (anche se preparato in automatico da Scrivi tutto il libro)"],
                    ["Rivedi il capitolo · Aggiorna la scheda personaggi", "1 credito ciascuno"],
                    ["Indice, scrittura, chat, ricerca, controlli e metadati", "Vedi il tariffario del cervello selezionato"],
                ], [0.55, 0.45]),
                ("punti", [
                    "Non incollare dati sensibili non necessari. Conserva un CSV del progetto e verifica fatti, citazioni, diritti e dati tecnici.",
                    "Il software non pubblica libri automaticamente: la revisione finale e il rispetto delle regole KDP restano dell'utente.",
                ]),
                ("h2", "Se qualcosa non appare"),
                ("punti", [
                    "Dopo login o cambio dispositivo, premi Riaggiorna all'ultima stesura.",
                    "Se una sezione è scritta ma non è visibile, controlla che l'indice sia salvato e sincronizzato.",
                    "Il riquadro Progetto del libro compare in Scrivi il libro dopo aver creato l'indice.",
                    "Per iniziare un libro nuovo usa Reset progetto: è l'unico comando che cancella l'intero progetto aperto.",
                ]),
            ],
        },
    ],
}

EN = {
    "titolo": "Scrittore Site Private Area Guide",
    "sottotitolo": "Updated instructions to plan, write, check, save and export a book",
    "versione": "version 7x",
    "area": "Private area · version 7x",
    "nota_copertina": "This guide explains the features available after you sign in. It does not cover the public home page, "
                      "registration or external payment. The costs shown in the app before each action always prevail.",
    "novita": "<b>What's new in version 7x</b><br/>"
              "• The two AI engines are now called <b>Expensive brain</b> and <b>Economy brain</b>.<br/>"
              "• New <b>Book plan</b> for every genre: outline, hidden truth and setups for novels, thesis for essays, "
              "objectives and prerequisites for manuals.<br/>"
              "• A <b>consistency sheet</b> that updates itself after every section, and <b>chapter review</b>.<br/>"
              "• For novels: choose <b>who tells the story</b> and the <b>tense</b>, with dedicated writing instructions.<br/>"
              "• The <b>Guided chat</b> also fills in the book plan automatically.<br/>"
              "• Uncertain facts marked <b>[TO VERIFY]</b> and new advice in the final check.",
    "capitoli": [
        {
            "titolo": "Getting started",
            "intro": "The private area keeps the whole book in one project: brief, book plan, outline, manuscript, sources, "
                     "images and checks. You can read and edit the texts manually at any time.",
            "blocchi": [
                ("h2", "Areas of the page"),
                ("tabella", ["Area", "What it is for"], [
                    ["Sidebar", "Sets up the account, the AI engine and the editorial brief of the book."],
                    ["Project Centre", "Shows Brief, Outline, Manuscript, Sources and the next recommended step. It changes nothing."],
                    ["Operational Centre", "Contains the Niche chat and sections 0-5. Follow the path or open what you need directly."],
                ], [0.28, 0.72]),
                ("h2", "Recommended path"),
                ("punti", [
                    "Optionally, use the Niche chat first to think about the market.",
                    "Open section 0 and use the Guided chat: it prepares the brief and also fills in the book plan.",
                    "Apply the form to the sidebar, choose the engine and generate the outline.",
                    "In Write the book, check the <b>Book plan</b> panel, then write one section or the whole book.",
                    "Review the chapters, check Preview and the Ready to publish report, save the session and export.",
                ]),
            ],
        },
        {
            "titolo": "Sidebar, account and project",
            "intro": "The sidebar contains language, AI engine, balance and brief. Book personalisation stays optional and must not block the outline.",
            "blocchi": [
                ("h2", "Account commands"),
                ("tabella", ["Command", "What it does", "When to use it"], [
                    ["Refresh credit balance", "Reloads the real account balance.", "After a purchase or a referral reward."],
                    ["Top up credits", "Opens packages and secure payment.", "When you want to buy credits."],
                    ["Invite and earn credits", "Shows referral link, invitations and rewards.", "To share the software."],
                    ["Sign out", "Saves an updated snapshot of the project and closes the session.", "Wait for the sign-in screen."],
                    ["Reset project", "Deletes the open project: sidebar, outline, texts, sources, images, memory and cache.", "Only to really start a new project."],
                ], [0.24, 0.44, 0.32]),
                ("h2", "Language and AI engine"),
                ("punti", [
                    "Choose the language before creating outline and manuscript: labels, chats, prompts and text follow it. 9 languages are available.",
                    "<b>Expensive brain</b>: the complete path, including web research, web copyright check and online fact check.",
                    "<b>Economy brain</b>: the same writing path with lighter consumption; web features remain available only with the Expensive brain.",
                    "Open the price list below the selected engine. The estimate shown before starting always prevails over examples or guides.",
                    "With the Economy brain small operations can be counted in units: three units equal one credit.",
                ]),
                ("h2", "The editorial brief"),
                ("tabella", ["Group", "Fields", "Why they matter"], [
                    ["Identity", "Title and author", "Header, exports and metadata."],
                    ["Direction", "Genre, writing type, style, pacing", "Tone, structure and depth of the writing."],
                    ["Point of view", "Essays and manuals: You, Plural you, We or Impersonal. Novels: <b>who tells the story</b> "
                     "(first person, close third, omniscient, multiple points of view) and <b>tense</b> (past or present).",
                     "Keeps the same voice throughout the book."],
                    ["Goal", "Topic or plot, reader, desired result", "Concrete direction for outline and sections."],
                    ["Further details", "Constraints, examples, facts, audience", "Useful information that does not fit elsewhere."],
                    ["Length", "Compact, Standard KDP, In depth", "Plans sections and pages without filler."],
                ], [0.18, 0.46, 0.36]),
            ],
        },
        {
            "titolo": "Niche chat and Guided chat",
            "intro": "Both chats are optional and have different roles. They always use the Expensive brain and the selected language; "
                     "the cost of each reply is shown before use.",
            "blocchi": [
                ("h2", "Niche chat"),
                ("punti", [
                    "Helps you discuss reader, market, demand, competition and publishing opportunity.",
                    "It does not change sidebar, outline or manuscript: at the end it produces a prompt to copy into the Guided chat.",
                ]),
                ("h2", "Section 0 · Guided chat"),
                ("punti", [
                    "Describe your idea, even in one sentence. The chat asks only useful questions and always asks whether you want to personalise the book.",
                    "It prepares a form with all sidebar fields and, <b>automatically</b>, the book plan too:",
                    "<b>novels</b>: who tells the story, tense, characters and world, hidden truth with timeline, setup map;",
                    "<b>essays</b>: central thesis, the reader's problem and key ideas;",
                    "<b>manuals</b>: learning objectives, prerequisites and useful extras.",
                    "Apply the form by filling only empty fields or replacing existing ones. Check the proposal before applying it.",
                    "The chat never invents personal experiences attributed to you; biographies use only known real facts.",
                ]),
                ("h2", "Personalise your book"),
                ("tabella", ["Field", "Use"], [
                    ["Personal voice, material, priorities and boundaries", "Make the project more individual when relevant."],
                    ["Checkpoint mode", "Chooses whether full writing pauses before Parts or before the conclusion."],
                    ["Checkpoint notes", "Write which choice you want to review during a pause. Leave empty if not needed."],
                ], [0.38, 0.62]),
            ],
        },
        {
            "titolo": "Sources, memory and consistency",
            "intro": "Sources, memory and the consistency sheet keep the book orderly and consistent. They do not replace your "
                     "own checks or authorise copying protected content.",
            "blocchi": [
                ("h2", "Optional sources"),
                ("punti", [
                    "Upload PDF or DOCX: the software builds a concept map to guide outline and text, without reusing sentences from the sources.",
                    "Regenerate web sources: only sources useful to the brief are kept.",
                    "Sources guide work and checks; they do not automatically become a bibliography or published text.",
                ]),
                ("h2", "Editorial memory and continuity"),
                ("punti", [
                    "Brief, plan, outline, written sections and approved edits feed a structured editorial memory.",
                    "Each new section continues <b>from the ending</b> of the previous one, avoiding jumps and repetitions.",
                    "The <b>consistency sheet</b> updates itself after every section: where characters are and what they know, ideas and "
                    "terms already explained, promises and mysteries still open. You can edit it in the Book plan panel.",
                    "If you edit a text manually, save the session so the project keeps the updated version.",
                ]),
                ("h2", "Saving and recovery"),
                ("tabella", ["Button", "What it does"], [
                    ["Save session", "Saves sidebar, plan, outline, sections, sources, images and memory to your account."],
                    ["Refresh latest draft", "Restores the last saved snapshot. Use it after sign-in, sign-out, refresh or a device change."],
                    ["Refresh page", "Reloads the interface. After important edits, save the session first."],
                    ["Sign out", "Attempts a final save before closing. For a portable copy also use the CSV export."],
                ], [0.32, 0.68]),
            ],
        },
        {
            "titolo": "Professional outline",
            "intro": "Section 1 turns brief and plan into an editable structure. The outline includes the Preface and defines the sections available in the editor.",
            "blocchi": [
                ("h2", "What the commands do"),
                ("tabella", ["Command", "Result"], [
                    ["Generate professional outline", "Studies brief, book plan and, if enabled, research. Produces a hierarchical outline with Preface."],
                    ["Progress bar", "Shows the generation stage. If no usable outline appears, the existing project is not deleted."],
                    ["Outline score or review", "Highlights possible improvements without adding useless entries."],
                    ["Save and synchronize chapters", "Makes the outline entries available in Writing, Preview and export."],
                    ["Manual edit", "You can revise titles and structure. Save and synchronize again after editing."],
                ], [0.32, 0.68]),
                ("h2", "Structure and quality"),
                ("punti", [
                    "For novels the outline follows a three-act arc: inciting incident within the first 10%, turning point at 25%, "
                    "midpoint reversal, lowest point at 75%, then climax and epilogue.",
                    "If the plan contains a setup map, the chapters it mentions must exist in the outline.",
                    "Compact aims at a short book, Standard KDP at a medium manuscript, In depth at a longer treatment. "
                    "The system does not add useless chapters just to reach a page count.",
                ]),
            ],
        },
        {
            "titolo": "Book plan",
            "intro": "In section 2, the <b>Book plan</b> panel holds the plan that guides every section. It adapts to the genre "
                     "and is filled in automatically by the Guided chat; you can edit it whenever you like.",
            "blocchi": [
                ("h2", "Fields by type of book"),
                ("tabella", ["Type", "Fields", "How the AI uses them"], [
                    ["Novels", "Characters and world · Hidden truth and timeline · Setup map",
                     "Treats characters and places as canon, does not reveal the truth too early, plants and pays off each setup in the indicated sections."],
                    ["Essays", "Central thesis and key ideas", "Each chapter develops idea, evidence, objection and summary in support of the thesis."],
                    ["Manuals", "Learning objectives and prerequisites", "Moves from simple to complex, never using concepts not yet explained."],
                    ["All", "Section outline · Consistency sheet", "Follows the outline points and never contradicts the sheet."],
                ], [0.14, 0.34, 0.52]),
                ("h2", "Panel commands"),
                ("tabella", ["Command", "What it does"], [
                    ["Propose the full plan", "Fills in empty fields and the outline of every section in a single request. What you already wrote stays unchanged."],
                    ["Update the sheet from written chapters", "Novels only: updates characters and world by reading the sections already written."],
                    ["Consistency sheet", "Updates itself after each written section. Nothing to press."],
                    ["Review the chapter", "An editor rereads the selected chapter and flags inconsistencies, repetitions, weak points and facts to verify. It does not change the text."],
                ], [0.36, 0.64]),
                ("h2", "Setup map format"),
                ("punti", [
                    "One setup per line: <i>- The father's letter | appears: Chapter 2 | resolves: Chapter 11</i>.",
                    "The format is recognised in every language of the site.",
                ]),
            ],
        },
        {
            "titolo": "Writing and quizzes",
            "intro": "In section 2 you write one entry at a time or start full writing. The created text stays editable in the professional editor.",
            "blocchi": [
                ("h2", "Writing a section"),
                ("punti", [
                    "Choose the section and press Write detailed content. The result is saved and appears in the editor and in the preview.",
                    "Each section receives plan, outline, consistency sheet and the structure of its genre: a hook when a chapter opens and a "
                    "reason to keep reading when it closes; evidence and objections in essays; steps with the expected result, summary and "
                    "exercise at the end of chapters in manuals.",
                    "Novels use dedicated writing instructions: scenes, dialogue, a consistent narrative voice, no checklists. "
                    "Italian dialogue uses the «…» quotation marks.",
                    "Lengths are flexible: a short, intense scene is not padded with filler.",
                    "Rework with AI improves only the selected section according to a precise request.",
                ]),
                ("h2", "Facts to verify"),
                ("punti", [
                    "In essays and manuals an uncertain fact is marked <b>[TO VERIFY]</b> instead of being invented "
                    "(the mark follows the book language, e.g. [DA VERIFICARE] in Italian).",
                    "Check every marked fact and delete the mark once verified. Word and PDF remove it anyway.",
                ]),
                ("h2", "Write the whole book"),
                ("punti", [
                    "If the outline is missing, the software first prepares the book plan automatically (cost shown in the estimate).",
                    "It then works section by section, Preface included; the bar shows progress and the current section.",
                    "Pause keeps what is completed; Resume continues from the missing sections; Stop permanently leaves outline and texts intact.",
                ]),
                ("h2", "Manual edits"),
                ("punti", [
                    "You can rewrite any text directly in the editor. Save the session after an important edit.",
                    "If you change the outline, synchronize it again.",
                ]),
            ],
        },
        {
            "titolo": "Preview",
            "intro": "Section 3 lets you read the book as a continuous manuscript before exporting.",
            "blocchi": [
                ("punti", [
                    "Use the clickable outline to reach a section, the manuscript search and the voice reader to listen to the text.",
                    "The page estimate uses the words already written and a cautious forecast for missing sections. It is an indicator, not a promise.",
                    "Manual edits and new sections appear here after saving and synchronizing the outline.",
                ]),
            ],
        },
        {
            "titolo": "Import Export Copyright",
            "intro": "Section 4 contains backup, recovery, checks and final files. Export is always possible, but an editorial warning invites you to fix issues before publishing.",
            "blocchi": [
                ("h2", "Complete CSV"),
                ("tabella", ["Command", "What it does"], [
                    ["Export complete project CSV", "Downloads sidebar, book plan, outline, sections, sources, images and memory as a portable copy."],
                    ["Import and restore project", "Loads a CSV exported by the software and restores the project in the current page."],
                    ["Check manuscript completeness", "Flags empty or incomplete sections. It does not rewrite the book automatically."],
                ], [0.34, 0.66]),
                ("h2", "Ready to publish"),
                ("punti", [
                    "Structure, manuscript and complete sentences must be checked.",
                    "While <b>[TO VERIFY]</b> facts remain, the export is flagged as a draft and you get the list of sentences to check.",
                    "<b>Editorial advice</b> (does not block export): setups without a payoff or pointing to missing chapters, mysteries still "
                    "open according to the consistency sheet, expressions repeated more than 3 times, clichés, Italian dialogue without «…».",
                ]),
                ("h2", "Originality, copyright and KDP"),
                ("punti", [
                    "The local originality check compares the manuscript only with uploaded PDF and DOCX files.",
                    "The web copyright check (Expensive brain) flags similarities or points to verify. It does not legally certify originality.",
                    "The KDP compliance check reads the official guidelines and produces a report; it does not guarantee publication.",
                ]),
                ("h2", "Word and PDF"),
                ("punti", [
                    "Download Word to keep revising in an external editor, or PDF for a typeset version. Always check the final file before submitting it.",
                ]),
            ],
        },
        {
            "titolo": "KDP formatting and metadata",
            "intro": "Section 5 prepares useful material before final publication.",
            "blocchi": [
                ("tabella", ["Feature", "What it does"], [
                    ["Generate detailed metadata", "Analyses an uploaded manuscript and proposes a marketing description and seven long-tail keywords in the selected language."],
                    ["Format document", "For a DOCX applies 6 x 9 settings, margins, fonts, headings, indents, justified text and page numbers."],
                    ["Download Word 6 x 9", "Downloads the formatted DOCX. Always check the result in your layout program or in the KDP previewer."],
                ], [0.32, 0.68]),
            ],
        },
        {
            "titolo": "Credits, security and good practice",
            "intro": "The app shows an estimate before paid AI actions. The estimate shown always prevails over this guide.",
            "blocchi": [
                ("h2", "What uses credits"),
                ("tabella", ["Action", "Indicative credits"], [
                    ["Reading, editing, saving, importing, exporting", "Free"],
                    ["Automatic consistency sheet after each section", "Free"],
                    ["Propose the full plan", "2 credits (also when prepared automatically by Write the whole book)"],
                    ["Review the chapter · Update the character sheet", "1 credit each"],
                    ["Outline, writing, chats, research, checks and metadata", "See the price list of the selected engine"],
                ], [0.55, 0.45]),
                ("punti", [
                    "Do not paste unnecessary sensitive data. Keep a CSV of the project and verify facts, quotations, rights and technical data.",
                    "The software does not publish books automatically: final review and compliance with KDP rules remain your responsibility.",
                ]),
                ("h2", "If something does not appear"),
                ("punti", [
                    "After signing in or changing device, press Refresh latest draft.",
                    "If a section is written but not visible, check that the outline is saved and synchronized.",
                    "The Book plan panel appears in Write the book once the outline exists.",
                    "To start a new book use Reset project: it is the only command that deletes the whole open project.",
                ]),
            ],
        },
    ],
}

GUIDE = {"Italiano": IT, "English": EN}
