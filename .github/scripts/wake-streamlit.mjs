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
  const deadline = Date.now() + 240_000;
  let wakeClicked = false;
  let lastReloadAt = Date.now();

  while (Date.now() < deadline) {
    if (await appIsReady()) {
      console.log(wakeClicked
        ? "App riattivata: home di Scrittore Site visibile."
        : "App già attiva: home di Scrittore Site visibile.");
      process.exitCode = 0;
      break;
    }

    const wakeButton = wakeClicked ? null : await findWakeButton();
    if (wakeButton) {
      console.log("Pagina di sospensione rilevata: avvio il risveglio.");
      await wakeButton.click({ timeout: 15_000 });
      wakeClicked = true;
      lastReloadAt = Date.now();
    }

    const visibleText = await visiblePageText();
    if (/this app has encountered an error|this app has gone over its resource limits|error running app/i.test(visibleText)) {
      throw new Error("Streamlit mostra un errore dell'app, non una semplice sospensione.");
    }

    // La pagina di risveglio può non aggiornarsi da sola: dopo 30 secondi
    // ricarichiamo soltanto la home pubblica per verificare l'app reale.
    if (wakeClicked && Date.now() - lastReloadAt > 30_000) {
      await page.reload({ waitUntil: "domcontentloaded", timeout: 45_000 });
      lastReloadAt = Date.now();
    }

    await page.waitForTimeout(3_000);
  }

  if (!(await appIsReady())) {
    const visibleText = await visiblePageText();
    const frameUrls = page.frames().map((frame) => frame.url()).join(", ");
    throw new Error(`Home non visibile dopo 4 minuti. Frame: ${frameUrls}. Stato: ${visibleText.slice(0, 350)}`);
  }
} finally {
  await browser.close();
}
