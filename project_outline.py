"""Regole deterministiche per indice, struttura e stime editoriali.

Questo modulo non conosce Streamlit, crediti o chiamate AI. Le funzioni qui
contenute possono quindi essere controllate separatamente prima di usare un
indice nel flusso dell'app.
"""

from __future__ import annotations

import math
import re
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from editorial_rules import PROFILI_LUNGHEZZA_STESURA


PAROLE_PER_PAGINA_6X9 = 275


def profilo_tipologia_stesura(stile: str) -> str:
    """Restituisce istruzioni di stesura diverse per ogni tipologia."""
    profili = {
        "Standard": "Esponi con chiarezza e ordine. Alterna spiegazione, esempio e applicazione senza estremi retorici.",
        "Professionale Accademico": "Definisci termini, separa fatti, metodo, interpretazioni e limiti. Usa un registro preciso e prudente; non trasformare il testo in un elenco di istruzioni quando il contenuto richiede argomentazione.",
        "Persuasivo (Neuromarketing Applicato)": "Parti da un problema concreto, chiarisci valore e prove, affronta obiezioni e guida verso una scelta o un'azione. Non usare pressione, manipolazione o promesse garantite.",
        "Conversazionale ed Empatico": "Accompagna il lettore con un linguaggio umano e rispettoso. Anticipa dubbi reali, normalizza gli ostacoli e offri indicazioni applicabili senza toni paternalistici.",
        "Scientifico Divulgativo": "Rendi comprensibili concetti complessi attraverso definizioni semplici, meccanismi, esempi e limiti. Distingui sempre dati, ipotesi, analogie e aspetti da verificare.",
        "Storytelling Immersivo": "Costruisci scene, azioni, conseguenze e dettagli sensoriali coerenti. Ogni sezione deve far evolvere conflitto, personaggio, relazione o posta in gioco; non riassumere ciò che può essere mostrato.",
        "Giornalistico d'Inchiesta": "Mantieni una linea di verifica: fatti documentabili, fonti da controllare, contraddizioni, contesto e conseguenze. Non presentare ipotesi come prove e non inventare testimonianze.",
        "Socratico (Dialogico / Riflessivo)": "Organizza la sezione attorno a una domanda reale. Esplora presupposti, dubbi e obiezioni, quindi porta il lettore a una conclusione argomentata o a una riflessione verificabile.",
        "Epico ed Evocativo": "Usa immagini e ritmo evocativi senza perdere chiarezza. La trasformazione, le prove e il significato devono essere concreti e adeguati al genere, non formule decorative.",
        "Minimalista ed Essenziale": "Elimina tutto ciò che non serve. Usa frasi sobrie, titoli funzionali, esempi strettamente necessari e una sola idea centrale per blocco di testo.",
    }
    return profili.get(stile, profili["Standard"])


def profilo_genere_stesura(genere: str) -> str:
    """Regole di forma e contenuto per tutti i generi offerti dall'interfaccia."""
    profili = {
        "Saggio Scientifico": "Sostieni una tesi con definizioni, metodo, evidenze, controargomentazioni, limiti e implicazioni. Non inventare dati o studi.",
        "Quiz Scientifico": "Alterna spiegazione essenziale, domande verificabili, soluzioni motivate e chiarimento degli errori più probabili.",
        "Manuale Tecnico": "Fornisci prerequisiti, strumenti, parametri, sequenze operative, controlli, errori e criteri di riuscita. Se software o norme possono cambiare, segnala cosa verificare.",
        "Religioso / Teologico": "Distingui testi, interpretazioni, tradizioni e opinioni. Mantieni rispetto, precisione storica e nessuna affermazione dogmatica non attribuita.",
        "Spirituale / Esoterico": "Usa un tono rispettoso e non prescrittivo. Presenta pratiche come esperienze personali o tradizionali, non come cure o certezze scientifiche.",
        "Meditazione / Mindfulness": "Offri pratiche graduali, istruzioni sicure, durata indicativa, osservazioni e alternative. Evita promesse terapeutiche o risultati garantiti.",
        "Business & Marketing": "Usa obiettivi, pubblico, casi, metriche, scelte operative e criteri di verifica. Se i dati non sono forniti, usa esempi dichiaratamente ipotetici.",
        "Economia e Finanza": "Separa educazione generale da consulenza personalizzata. Spiega rischio, limiti, dati e ipotesi; non dare raccomandazioni finanziarie individuali.",
        "Romanzo Rosa": "Sviluppa desiderio, relazione, vulnerabilità, ostacoli e scelta emotiva attraverso scene, dialoghi e trasformazione dei personaggi.",
        "Thriller / Noir": "Costruisci tensione con indizi, conseguenze, conflitti e rivelazioni coerenti. Ogni capitolo deve cambiare le informazioni disponibili o aumentare la posta in gioco.",
        "Fantasy": "Mantieni coerenti mondo, regole, conflitti e conseguenze. Mostra il worldbuilding dentro azioni e scene, senza blocchi enciclopedici.",
        "Fantascienza": "Rendi coerente la premessa speculativa e mostra come modifica società, tecnologia, personaggi e conflitto. Non sostituire la storia con spiegazioni astratte.",
        "Manuale Psicologico": "Spiega modelli e pratiche in modo accessibile, con limiti chiari. Non fare diagnosi, non promettere cura e invita a rivolgersi a professionisti quando necessario.",
        "Biografia": "Segui una cronologia significativa, usando fonti verificabili e distinguendo fatti, testimonianze e interpretazioni. Privilegia svolte e contesto rispetto a elenchi di date.",
        "Ricettario": "Ogni capitolo-ricetta deve contenere porzioni, tempi, ingredienti con dosi, procedimento numerato, segnali di riuscita, errore e correzione, variante e conservazione solo se verificata. Non duplicare la stessa ricetta in forma breve ed estesa.",
        "Test Prep (Preparazione Esami)": "Spiega soltanto le competenze pertinenti alla prova, poi fornisci esercizi reali, soluzioni ragionate, errori tipici e criteri di autovalutazione. Quando una sezione promette quiz, test o simulazioni, deve contenere le domande effettive e non istruzioni generiche su come studiare. Mantieni separati quesiti e soluzioni, verifica il numero richiesto, evita duplicati e non inventare regole d'esame non verificate.",
        "Narrativo": "Sviluppa personaggi, conflitto, cause e conseguenze in scene concrete. Ogni capitolo deve avere una funzione narrativa distinta.",
        "Romanzo Classico": "Usa una costruzione narrativa solida, personaggi coerenti, ambientazione e temi sviluppati attraverso azioni e dialoghi; evita imitazioni di autori viventi.",
        "Contemporaneo": "Racconta conflitti e relazioni con voce naturale, dettagli specifici e temi attuali trattati attraverso la storia, non con prediche.",
        "Self-Help": "Definisci problemi realistici, pratiche graduali, esempi e criteri di verifica. Evita promesse di trasformazione garantita o consigli clinici.",
        "Manuale Pratico": "Fornisci un percorso eseguibile: materiali o prerequisiti, passaggi, controlli, errori, alternative e risultato finale verificabile.",
        "Storico": "Ordina il racconto per nessi causali e cronologia, distinguendo fonti, fatti, interpretazioni e controversie. Non inventare citazioni o date.",
    }
    return profili.get(genere, "Mantieni una struttura coerente con pubblico, obiettivo, genere e limiti dichiarati.")


def estrai_numero_ricette(titolo: str, trama: str, obiettivo: str) -> int | None:
    testo = f"{titolo} {trama} {obiettivo}".lower()
    match = re.search(r"\b(\d{1,3})\s+(?:ricette|recipes|recetas|recettes|rezepte|rețete|рецептов|وصفات|个食谱)\b", testo)
    return int(match.group(1)) if match else None


def profilo_struttura_indice(genere: str, titolo: str, trama: str, obiettivo: str) -> str:
    """Restituisce istruzioni di struttura proporzionate al tipo di libro."""
    if genere == "Ricettario":
        numero = estrai_numero_ricette(titolo, trama, obiettivo)
        quantita = f"esattamente {numero}" if numero else "un numero coerente con la richiesta"
        return f"""RICETTARIO: crea {quantita} ricette effettive, distribuite in parti tematiche coerenti. Ogni ricetta è un Capitolo autonomo e completo. Se è richiesto un numero preciso di ricette, crea esattamente quel numero di Capitoli e ciascun Capitolo deve avere il nome di una ricetta: non usare Capitoli per introduzione, ingredienti, attrezzatura, tecniche o consigli. Le Parti possono orientare il lettore senza aggiungere Capitoli introduttivi. Non creare sottocapitoli 1.1, 1.2 o 1.3 per espandere la stessa ricetta. Il numero delle ricette nell'indice deve coincidere con il numero richiesto."""
    if genere in {"Romanzo Rosa", "Thriller / Noir", "Fantasy", "Fantascienza", "Narrativo", "Romanzo Classico", "Contemporaneo", "Biografia"}:
        return "NARRATIVA E BIOGRAFIA: organizza 3-6 Parti e un numero di capitoli proporzionato all'arco narrativo. Non imporre sottocapitoli a ogni capitolo: usali solo se sono necessari e non spezzano artificialmente scene o svolte. Ogni titolo deve nominare una scena, una scelta, un luogo, un personaggio, un oggetto o una conseguenza specifici del brief. Almeno un terzo dei titoli deve contenere parole concrete tratte dal titolo o dalla trama. Evita titoli generici come 'Il ritorno', 'La scoperta', 'L'incontro inaspettato', 'Il richiamo del passato', 'Riflessioni' o 'La fine'."
    if genere in {"Quiz Scientifico", "Test Prep (Preparazione Esami)"}:
        return "QUIZ E TEST PREP: organizza fondamenti, esercitazione graduata, quiz/domande commentate, almeno una simulazione esplicitamente nominata e correzioni. Nella lingua scelta usa le parole equivalenti a ‘quiz/questions’ e ‘simulation’, così che lo scopo delle sezioni sia leggibile. Ogni unità deve indicare una competenza verificabile; non creare capitoli riempitivi."
    return "SAGGISTICA E MANUALI: distribuisci fondamenti, metodo, applicazione, verifica e sintesi in una struttura proporzionata al brief. Crea sottocapitoli solo per concetti o passaggi realmente distinti; il budget di sezioni indicato nel prompt prevale su ogni schema numerico generale."


def normalizza_indice_generato(indice: str) -> str:
    """Rimuove solo rumore di formattazione, senza alterare l'architettura proposta."""
    righe = []
    for riga in (indice or "").splitlines():
        pulita = re.sub(r"^\s*[-*#]+\s*", "", riga).strip()
        if pulita.lower() in {"indice", "table of contents", "sommaire", "inhaltsverzeichnis"}:
            continue
        if pulita:
            righe.append(pulita)
    return "\n".join(righe).strip()


def criticita_indice_generato(indice: str, genere: str, titolo: str, trama: str, obiettivo: str, minimo_parti: int = 4, minimo_capitoli: int | None = None) -> list[str]:
    """Intercetta gli errori strutturali più frequenti negli indici generati."""
    testo = normalizza_indice_generato(indice)
    righe = testo.splitlines()
    regex_capitolo = r"(?i)^(capitolo|chapter|kapitel|capítulo|chapitre|capitolul|глава|الفصل|章节)\s+\d+"
    regex_parte = r"(?i)^(parte|part|partie|teil|partea|часть|الجزء|部分)\s+"
    capitoli = [riga for riga in righe if re.match(regex_capitolo, riga)]
    parti = [riga for riga in righe if re.match(regex_parte, riga)]
    if not capitoli:
        return ["non sono stati riconosciuti capitoli nel formato richiesto"]
    problemi: list[str] = []
    narrativi = {"Romanzo Rosa", "Thriller / Noir", "Fantasy", "Fantascienza", "Narrativo", "Romanzo Classico", "Contemporaneo", "Biografia"}
    if genere != "Ricettario" and len(parti) < minimo_parti:
        problemi.append(f"struttura troppo breve: sono presenti solo {len(parti)} Parti, ne servono almeno {minimo_parti}")
    minimo_effettivo = (12 if genere not in {"Ricettario"} else 0) if minimo_capitoli is None else minimo_capitoli
    if len(capitoli) < minimo_effettivo:
        problemi.append(f"struttura troppo breve: sono presenti solo {len(capitoli)} Capitoli, ne servono almeno {minimo_effettivo}")
    if genere not in narrativi and genere != "Ricettario":
        senza_sviluppo = []
        for capitolo in capitoli:
            inizio = righe.index(capitolo)
            fine = next((i for i in range(inizio + 1, len(righe)) if re.match(regex_capitolo, righe[i]) or re.match(regex_parte, righe[i])), len(righe))
            sottosezioni = sum(1 for riga in righe[inizio + 1:fine] if re.match(r"^\d+\.\d+\s+", riga))
            if sottosezioni < 2:
                senza_sviluppo.append(capitolo)
        if senza_sviluppo:
            problemi.append("capitoli senza almeno due sottocapitoli distinti: " + "; ".join(senza_sviluppo[:3]))
    if genere == "Ricettario":
        richieste = estrai_numero_ricette(titolo, trama, obiettivo)
        if richieste and len(capitoli) != richieste:
            problemi.append(f"sono richieste {richieste} ricette, ma l'indice contiene {len(capitoli)} capitoli")
        titoli = " ".join(capitoli).lower()
        non_ricette = ("introduzione", "ingredient", "attrezz", "tecniche", "consigli", "dispensa", "sostituz", "substitut", "preparazione di ingredient", "nutrient", "planific", "consejos", "conservación", "alternativas", "erreurs", "conseils", "substitutions", "grundlagen")
        if any(parola in titoli for parola in non_ricette):
            problemi.append("un capitolo del ricettario è introduttivo o tecnico invece di essere una ricetta")
        if any(re.match(r"^\d+\.\d+\s+", riga) for riga in righe):
            problemi.append("il ricettario contiene sottocapitoli: ogni capitolo deve essere una ricetta completa e autonoma")
    if genere in narrativi:
        generici = {"il ritorno", "la scoperta", "l'inizio", "la fine", "il conflitto", "la scelta", "la crisi", "riflessioni", "sogni e memorie", "nuovi inizi", "l'incontro inaspettato", "il richiamo del passato", "la dolcezza del ricordo", "il richiamo della tradizione", "riscoprire se stessi", "la verità", "il segreto"}
        trovati = []
        for capitolo in capitoli:
            nome = re.sub(r"(?i)^(capitolo|chapter|kapitel|capítulo|chapitre|capitolul|глава|الفصل|章节)\s+\d+\s*:\s*", "", capitolo).strip().lower()
            if nome in generici:
                trovati.append(capitolo)
        if len(trovati) >= 2:
            problemi.append("titoli narrativi troppo generici: " + "; ".join(trovati[:3]))
        esclusioni = {"della", "delle", "dello", "degli", "dalla", "nelle", "nello", "come", "con", "una", "uno", "per", "che", "del", "dei", "gli", "le", "il", "la", "un", "e", "di", "da", "in", "su", "tra", "fra", "storia", "romanzo", "guida", "raccontare", "lettore", "lettori", "obiettivo", "titolo", "libro"}
        parole_brief = {parola for parola in re.findall(r"[a-zàèéìòóù]{4,}", f"{titolo} {trama}".lower()) if parola not in esclusioni}
        ancorati = 0
        for capitolo in capitoli:
            nome = re.sub(r"(?i)^(capitolo|chapter|kapitel|capítulo|chapitre|capitolul|глава|الفصل|章节)\s+\d+\s*:\s*", "", capitolo).lower()
            if any(parola in nome for parola in parole_brief):
                ancorati += 1
        soglia = max(3, (len(capitoli) + 2) // 3)
        if ancorati < soglia:
            problemi.append(f"titoli narrativi poco ancorati agli elementi concreti del brief ({ancorati}/{len(capitoli)} titoli specifici)")
    if genere in {"Quiz Scientifico", "Test Prep (Preparazione Esami)"}:
        testo_minuscolo = testo.lower()
        if not any(parola in testo_minuscolo for parola in ("quiz", "domand", "question", "pregunta", "frage", "вопрос", "سؤال", "问题")):
            problemi.append("manca una sezione con quiz o domande effettive")
        if not any(parola in testo_minuscolo for parola in ("simulaz", "simulation", "simulación", "simulare", "симуля", "محاك", "模拟")):
            problemi.append("manca una sezione di simulazione")
    return problemi


def firma_indice(indice: str) -> str:
    return re.sub(r"\s+", " ", (indice or "").strip().lower())


def conta_sezioni_indice(indice: str) -> int:
    regex = r"(?i)(Capitolo|Chapter|Kapitel|Capítulo|Chapitre|Capitolul|Глава|الفصل|Раздел|章节|Secţiune|Parte|Part|Partie|Teil|Partea|Часть|الجزء|部分|\d+\.)"
    return sum(1 for riga in (indice or "").splitlines() if re.search(regex, riga.strip()))


def superamenti_budget_editoriale(indice: str, massimo_parti: int | None, massimo_capitoli: int | None, massimo_sottocapitoli: int | None) -> list[str]:
    righe = [riga.strip() for riga in normalizza_indice_generato(indice).splitlines() if riga.strip()]
    regex_capitolo = r"(?i)^(capitolo|chapter|kapitel|capítulo|chapitre|capitolul|глава|الفصل|章节)\s+\d+"
    regex_parte = r"(?i)^(parte|part|partie|teil|partea|часть|الجزء|部分)\s+"
    superamenti: list[str] = []
    parti = [riga for riga in righe if re.match(regex_parte, riga)]
    capitoli = [riga for riga in righe if re.match(regex_capitolo, riga)]
    if massimo_parti and len(parti) > massimo_parti:
        superamenti.append(f"{len(parti)} Parti invece di massimo {massimo_parti}")
    if massimo_capitoli and len(capitoli) > massimo_capitoli:
        superamenti.append(f"{len(capitoli)} Capitoli invece di massimo {massimo_capitoli}")
    if not massimo_sottocapitoli:
        return superamenti
    for posizione, capitolo in enumerate(righe):
        if not re.match(regex_capitolo, capitolo):
            continue
        fine = next((i for i in range(posizione + 1, len(righe)) if re.match(regex_capitolo, righe[i]) or re.match(regex_parte, righe[i])), len(righe))
        sottocapitoli = [riga for riga in righe[posizione + 1:fine] if re.match(r"^\d+\.\d+\s+", riga)]
        if len(sottocapitoli) > massimo_sottocapitoli:
            superamenti.append(f"{capitolo} con {len(sottocapitoli)} sottocapitoli invece di massimo {massimo_sottocapitoli}")
    return superamenti


def stima_budget_parole_indice(indice: str, profilo_lunghezza: str, *, is_prefazione: Callable[[str], bool], titolo_prefazione: Callable[[], str], classifica: Callable[[str], str], ha_sottocapitoli: Callable[[str, Sequence[str]], bool]) -> dict[str, Any]:
    """Stima la capacità dell'indice, senza creare voci artificiali."""
    profilo = PROFILI_LUNGHEZZA_STESURA.get(profilo_lunghezza, PROFILI_LUNGHEZZA_STESURA["Standard KDP"])
    regex = r"(?i)^(?:capitolo|chapter|kapitel|capítulo|chapitre|capitolul|глава|الفصل|раздел|章节|secţiune|parte|part|partie|teil|partea|часть|الجزء|部分|\d+\.)"
    sezioni: list[str] = []
    for riga in str(indice or "").splitlines():
        voce = riga.strip()
        if voce and (is_prefazione(voce) or re.search(regex, voce)) and voce not in sezioni:
            sezioni.append(voce)
    if not any(is_prefazione(sezione) for sezione in sezioni):
        sezioni.insert(0, titolo_prefazione())
    minime = massime = 0
    dettaglio = {"prefazione": 0, "parti": 0, "capitoli_cornice": 0, "sezioni": 0}
    for sezione in sezioni:
        tipo = classifica(sezione)
        if tipo == "prefazione":
            minimo, massimo, categoria = 140, 220, "prefazione"
        elif tipo == "parte":
            minimo, massimo, categoria = 110, 180, "parti"
        elif tipo == "capitolo" and ha_sottocapitoli(sezione, sezioni):
            minimo, massimo, categoria = 160, 260, "capitoli_cornice"
        else:
            minimo, massimo, categoria = profilo["min_parole"], profilo["max_parole"], "sezioni"
        minime += minimo
        massime += massimo
        dettaglio[categoria] += 1
    obiettivo_pagine = int(profilo["pagine_minime"])
    tolleranza = float(profilo.get("tolleranza_pagine", 0.15))
    soglia_parole = math.ceil(obiettivo_pagine * PAROLE_PER_PAGINA_6X9 * (1 - tolleranza))
    return {"sezioni_totali": len(sezioni), "parole_minime": minime, "parole_massime": massime, "pagine_minime": math.ceil(minime / PAROLE_PER_PAGINA_6X9) if minime else 0, "pagine_massime": math.ceil(massime / PAROLE_PER_PAGINA_6X9) if massime else 0, "obiettivo_pagine": obiettivo_pagine, "soglia_pagine": math.ceil(obiettivo_pagine * (1 - tolleranza)), "soglia_parole": soglia_parole, "raggiunge_soglia": massime >= soglia_parole, "dettaglio": dettaglio}


def riepilogo_stima_pagine_manoscritto(sezioni: Sequence[str], contenuti: Mapping[str, str], indice: str, profilo_lunghezza: str, *, pulisci_testo: Callable[[str], str], classifica: Callable[[str], str], ha_sottocapitoli: Callable[[str, Sequence[str]], bool]) -> dict[str, Any]:
    """Calcola pagine attuali e una previsione prudente delle sezioni mancanti."""
    profilo = PROFILI_LUNGHEZZA_STESURA.get(profilo_lunghezza, PROFILI_LUNGHEZZA_STESURA["Standard KDP"])
    reali = minime_rimanenti = massime_rimanenti = mancanti = 0
    righe_indice = str(indice or "").splitlines()
    for sezione in sezioni or []:
        testo = pulisci_testo(str((contenuti or {}).get(sezione, "") or "")).strip()
        if testo:
            reali += len(testo.split())
            continue
        mancanti += 1
        tipo = classifica(sezione)
        if tipo == "prefazione":
            minimo, massimo = 140, 220
        elif tipo == "parte":
            minimo, massimo = 110, 180
        elif tipo == "capitolo" and ha_sottocapitoli(sezione, righe_indice):
            minimo, massimo = 160, 260
        else:
            minimo, massimo = profilo["min_parole"], profilo["max_parole"]
        minime_rimanenti += minimo
        massime_rimanenti += massimo
    obiettivo_pagine = int(profilo["pagine_minime"])
    obiettivo_parole = obiettivo_pagine * PAROLE_PER_PAGINA_6X9
    tolleranza = float(profilo.get("tolleranza_pagine", 0.15))
    soglia_parole = math.ceil(obiettivo_parole * (1 - tolleranza))
    soglia_pagine = math.ceil(obiettivo_pagine * (1 - tolleranza))
    previsione_min = reali + minime_rimanenti
    previsione_max = reali + massime_rimanenti
    return {"parole_reali": reali, "pagine_attuali": math.ceil(reali / PAROLE_PER_PAGINA_6X9) if reali else 0, "sezioni_mancanti": mancanti, "pagine_previste_min": math.ceil(previsione_min / PAROLE_PER_PAGINA_6X9) if previsione_min else 0, "pagine_previste_max": math.ceil(previsione_max / PAROLE_PER_PAGINA_6X9) if previsione_max else 0, "obiettivo_pagine": obiettivo_pagine, "obiettivo_parole": obiettivo_parole, "tolleranza_pagine": tolleranza, "soglia_pagine_tolleranza": soglia_pagine, "obiettivo_gia_raggiunto": reali >= soglia_parole, "obiettivo_nominale_raggiunto": reali >= obiettivo_parole, "obiettivo_realistico": previsione_max >= soglia_parole}
