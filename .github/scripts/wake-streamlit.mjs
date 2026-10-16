import { chromium } from "playwright";

// La home pubblica espone questo titolo solo dopo l'esecuzione dell'app.
// Una risposta HTTP 200, da sola, potrebbe essere la pagina di sospensione.
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

  const ready = page.locator("h1.ss-title", { hasText: "Scrittore Site" });
  const wakeButton = page.getByRole("button", {
    name: /get this app back up|wake.*app|riattiva|risveglia/i,
  }).first();
  const deadline = Date.now() + 240_000;
  let wakeClicked = false;
  let lastReloadAt = Date.now();

  while (Date.now() < deadline) {
    if (await ready.isVisible().catch(() => false)) {
      console.log(wakeClicked
        ? "App riattivata: home di Scrittore Site visibile."
        : "App già attiva: home di Scrittore Site visibile.");
      process.exitCode = 0;
      break;
    }

    if (!wakeClicked && await wakeButton.isVisible().catch(() => false)) {
      console.log("Pagina di sospensione rilevata: avvio il risveglio.");
      await wakeButton.click({ timeout: 15_000 });
      wakeClicked = true;
      lastReloadAt = Date.now();
    }

    const visibleText = await page.locator("body").innerText().catch(() => "");
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

  if (!(await ready.isVisible().catch(() => false))) {
    const visibleText = await page.locator("body").innerText().catch(() => "");
    throw new Error(`Home non visibile dopo 4 minuti. Stato: ${visibleText.slice(0, 350)}`);
  }
} finally {
  await browser.close();
}
