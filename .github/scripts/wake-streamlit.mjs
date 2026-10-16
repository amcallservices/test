import { chromium } from "playwright";

// La home pubblica vive in un iframe di Streamlit Cloud. Una risposta HTTP 200,
// da sola, potrebbe essere soltanto la pagina di sospensione.
const appUrl = process.env.STREAMLIT_URL;
if (!appUrl || new URL(appUrl).protocol !== "https:") {
  throw new Error("STREAMLIT_URL deve essere un indirizzo HTTPS valido.");
}

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ locale: "en-US" });
  const response = await page.goto(appUrl, {
    waitUntil: "domcontentloaded",
    timeout: 60_000,
  });
  console.log(`Visita iniziale: HTTP ${response?.status() ?? "sconosciuto"}`);

  const appIsReady = async () => {
    for (const frame of page.frames()) {
      const languages = frame.locator(".ss-languages-hero");
      const headline = frame.locator(".ss-headline");
      if (await languages.isVisible().catch(() => false)
          && await headline.isVisible().catch(() => false)) {
        return true;
      }
    }
    return false;
  };
  const findWakeButton = async () => {
    for (const frame of page.frames()) {
      const button = frame.getByRole("button", {
        name: /get this app back up|wake.*app|riattiva|risveglia/i,
      }).first();
      if (await button.isVisible().catch(() => false)) return button;
    }
    return null;
  };
  const visiblePageText = async () => {
    const parts = await Promise.all(page.frames().map(async (frame) =>
      frame.locator("body").innerText().catch(() => "")));
    return parts.filter(Boolean).join("\n");
  };
  // Un avvio a freddo può richiedere diversi minuti. Se Streamlit torna alla
  // schermata di sospensione, riproviamo il pulsante senza avviare altre funzioni.
  const deadline = Date.now() + 480_000;
  let wakeAttempts = 0;
  let lastWakeAt = 0;
  let lastReloadAt = Date.now();

  while (Date.now() < deadline) {
    if (await appIsReady()) {
      console.log(wakeAttempts > 0
        ? "App riattivata: home di Scrittore Site visibile."
        : "App già attiva: home di Scrittore Site visibile.");
      process.exitCode = 0;
      break;
    }

    const wakeButton = await findWakeButton();
    if (wakeButton && wakeAttempts < 3
        && (wakeAttempts === 0 || Date.now() - lastWakeAt >= 90_000)) {
      try {
        await wakeButton.click({ timeout: 15_000 });
        wakeAttempts += 1;
        lastWakeAt = Date.now();
        lastReloadAt = lastWakeAt;
        console.log(`Pagina sospesa: tentativo di risveglio ${wakeAttempts}/3.`);
      } catch {
        console.log("Il pulsante di risveglio è cambiato durante il clic: riproverò.");
      }
    }

    const visibleText = await visiblePageText();
    if (/this app has encountered an error|this app has gone over its resource limits|error running app/i.test(visibleText)) {
      throw new Error("Streamlit mostra un errore dell'app, non una semplice sospensione.");
    }

    // La pagina di risveglio può non aggiornarsi da sola. Anche senza pulsante
    // visibile, ricarichiamo periodicamente la sola home pubblica.
    if (Date.now() - lastReloadAt >= 45_000) {
      try {
        await page.reload({ waitUntil: "domcontentloaded", timeout: 45_000 });
      } catch {
        console.log("Ricaricamento temporaneamente non riuscito: continuo il controllo.");
      }
      lastReloadAt = Date.now();
    }

    await page.waitForTimeout(3_000);
  }

  if (!(await appIsReady())) {
    const visibleText = await visiblePageText();
    const frameUrls = page.frames().map((frame) => frame.url()).join(", ");
    throw new Error(`Home non visibile dopo 8 minuti (${wakeAttempts} tentativi di risveglio). Frame: ${frameUrls}. Stato: ${visibleText.slice(0, 350)}`);
  }
} finally {
  await browser.close();
}
