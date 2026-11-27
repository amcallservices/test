import { chromium } from "playwright";

// Controlla che la home pubblica di Scrittore Site risponda e, se Streamlit
// Community Cloud l'ha addormentata, preme "Yes, get this app back up!".
//
// La home vive in un iframe di Streamlit Cloud (/~/+/); nella pagina ci sono
// anche altri frame (widget di stato statuspage.io, componenti di sessione,
// iframe "about:srcdoc"): li controlliamo tutti tranne statuspage.io.

const appUrl = process.env.STREAMLIT_URL;
if (!appUrl || new URL(appUrl).protocol !== "https:") {
  throw new Error("STREAMLIT_URL deve essere un indirizzo HTTPS valido.");
}

// Attesa massima complessiva: circa 3 minuti.
const ATTESA_MASSIMA_MS = 180_000;
// Senza pulsante di risveglio e senza testi di caricamento/errore, dopo
// questo tempo consideriamo l'app attiva anche se non leggiamo i testi della
// home (per esempio se la grafica cambia di nuovo).
const GRAZIA_SENZA_PULSANTE_MS = 60_000;
const RICARICA_OGNI_MS = 45_000;
const RIPROVA_RISVEGLIO_DOPO_MS = 60_000;
const MAX_RISVEGLI = 3;

// Elementi e testi che compaiono solo nella home di Scrittore Site
// (vecchia e nuova grafica, italiano e inglese).
const SELETTORI_HOME = [".ss2-hero", ".ss2-h1", ".ss-headline", ".ss-languages-hero"];
const TESTI_HOME = /\b(accedi|registrati|funzioni|scrittura editoriale con ai|log in|write your book|scrivi il tuo libro)\b/i;
const PULSANTE_RISVEGLIO = /get this app back up|wake.*app|riattiva|risveglia/i;
const TESTI_ERRORE = /this app has encountered an error|this app has gone over its resource limits|error running app/i;
const TESTI_AVVIO = /in the oven|is waking up|getting this app back up|please wait|starting up|loading/i;

// Un frame appena creato ha l'indirizzo vuoto e lo riceve solo dopo il
// caricamento: per questo l'indirizzo si ricontrolla anche dopo la lettura.
const frameUtile = (frame) => {
  const url = frame.url();
  return url !== "" && url !== "about:blank" && !/statuspage\.io/i.test(url);
};

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ locale: "en-US" });
  const response = await page.goto(appUrl, { waitUntil: "domcontentloaded", timeout: 60_000 });
  const statoHttp = response?.status() ?? 0;
  console.log(`Visita iniziale: HTTP ${statoHttp || "sconosciuto"}`);

  const testoFrame = async (frame) => {
    const testo = await frame.locator("body").innerText({ timeout: 5_000 }).catch(() => "");
    return frameUtile(frame) ? testo : "";
  };
  const testoPagina = async () =>
    (await Promise.all(page.frames().filter(frameUtile).map(testoFrame))).filter(Boolean).join("\n");

  // Home visibile: un elemento noto visibile, oppure un testo noto, in uno
  // qualunque dei frame utili.
  const homeVisibile = async () => {
    for (const frame of page.frames().filter(frameUtile)) {
      for (const selettore of SELETTORI_HOME) {
        if (await frame.locator(selettore).first().isVisible().catch(() => false) && frameUtile(frame)) {
          return `elemento ${selettore}`;
        }
      }
      const testo = await testoFrame(frame);
      const trovato = testo.match(TESTI_HOME);
      if (trovato) return `testo "${trovato[0]}"`;
    }
    return "";
  };

  const pulsanteRisveglio = async () => {
    for (const frame of page.frames().filter(frameUtile)) {
      const pulsante = frame.getByRole("button", { name: PULSANTE_RISVEGLIO }).first();
      if (await pulsante.isVisible().catch(() => false) && frameUtile(frame)) return pulsante;
    }
    return null;
  };

  const inizio = Date.now();
  const scadenza = inizio + ATTESA_MASSIMA_MS;
  let risvegli = 0;
  let ultimoRisveglio = 0;
  let ultimaRicarica = Date.now();
  let ultimoStato = statoHttp;
  let esito = "";

  while (Date.now() < scadenza) {
    const motivo = await homeVisibile();
    if (motivo) {
      esito = `${risvegli > 0 ? "App riattivata" : "App già attiva"}: home di Scrittore Site visibile (${motivo}).`;
      break;
    }

    const testo = await testoPagina();
    if (TESTI_ERRORE.test(testo)) {
      throw new Error("Streamlit mostra un errore dell'app, non una semplice sospensione.");
    }

    const pulsante = await pulsanteRisveglio();
    if (pulsante) {
      if (risvegli < MAX_RISVEGLI && (risvegli === 0 || Date.now() - ultimoRisveglio >= RIPROVA_RISVEGLIO_DOPO_MS)) {
        try {
          await pulsante.click({ timeout: 15_000 });
          risvegli += 1;
          ultimoRisveglio = Date.now();
          ultimaRicarica = ultimoRisveglio;
          console.log(`Pagina sospesa: tentativo di risveglio ${risvegli}/${MAX_RISVEGLI}.`);
        } catch {
          console.log("Il pulsante di risveglio è cambiato durante il clic: riproverò.");
        }
      }
    } else if (
      risvegli === 0
      && ultimoStato >= 200 && ultimoStato < 400
      && Date.now() - inizio >= GRAZIA_SENZA_PULSANTE_MS
      && !TESTI_AVVIO.test(testo)
    ) {
      // Pagina che risponde, nessun pulsante di risveglio, nessun avvio in
      // corso né errore: l'app è sveglia anche se i testi non coincidono.
      esito = `App attiva: HTTP ${ultimoStato} e nessun pulsante di risveglio (testi della home non riconosciuti).`;
      break;
    }

    // La pagina di risveglio non sempre si aggiorna da sola: ricarichiamo
    // periodicamente la sola home pubblica.
    if (Date.now() - ultimaRicarica >= RICARICA_OGNI_MS) {
      try {
        const nuova = await page.reload({ waitUntil: "domcontentloaded", timeout: 45_000 });
        ultimoStato = nuova?.status() ?? ultimoStato;
      } catch {
        console.log("Ricaricamento temporaneamente non riuscito: continuo il controllo.");
      }
      ultimaRicarica = Date.now();
    }

    await page.waitForTimeout(3_000);
  }

  if (!esito) {
    const testo = await testoPagina();
    const frame = page.frames().map((f) => f.url()).join(", ");
    throw new Error(
      `Home non visibile dopo ${Math.round(ATTESA_MASSIMA_MS / 60_000)} minuti (${risvegli} tentativi di risveglio). `
      + `Frame: ${frame}. Testo: ${testo.slice(0, 350)}`,
    );
  }
  console.log(esito);
} finally {
  await browser.close();
}
