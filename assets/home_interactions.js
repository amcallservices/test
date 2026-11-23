// Home pubblica: interazioni che seguono il mouse.
// Gira nell'iframe invisibile di components.html e lavora sulla pagina
// principale. Se il browser non lo permette, la home resta solo CSS.
(function () {
  let doc, win;
  try { win = window.parent; doc = win.document; } catch (e) { return; }
  // Guardia con versione: dopo un aggiornamento dell'app (senza ricaricare la
  // pagina) la versione nuova parte anche se quella vecchia è ancora attiva.
  const VERSIONE = "3";
  if (!doc || doc.__ssHomeInterattiva === VERSIONE) { return; }
  doc.__ssHomeInterattiva = VERSIONE;

  const radice = doc.documentElement;
  const mouseVero = win.matchMedia("(hover: hover) and (pointer: fine)").matches;
  const fermo = win.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const SCHEDE = ".ss-priority, .ss-feature-group, .ss-card, .ss-ai-card, .ss-advantage, .ss-languages-hero, .ss-hero-copy, .ss-libro";
  const MAGNETICI = ".st-key-landing_signup button, .st-key-landing_login button, .st-key-download_private_area_guide_it button, .st-key-download_private_area_guide_en button";

  // 1) Barra di avanzamento della lettura + menu che evidenzia la sezione visibile.
  const sezioni = ["ss-percorso", "ss-funzioni", "ss-vantaggi", "ss-cervelli", "ss-crediti", "ss-faq", "ss-guide"];
  function contenitore() { return doc.querySelector('[data-testid="stMain"]'); }
  function aggiornaScorrimento() {
    const c = contenitore();
    if (!c || !doc.querySelector(".ss-quick-nav")) { return; }
    const max = Math.max(1, c.scrollHeight - c.clientHeight);
    radice.style.setProperty("--ss-scroll", (c.scrollTop / max).toFixed(4));
    let attiva = "";
    const soglia = c.getBoundingClientRect().top + c.clientHeight * 0.35;
    for (const id of sezioni) {
      const el = doc.getElementById(id);
      if (el && el.getBoundingClientRect().top <= soglia) { attiva = id; }
    }
    doc.querySelectorAll(".ss-quick-nav a, .ss-mobile-nav a").forEach(function (a) {
      a.classList.toggle("ss-attivo", attiva !== "" && a.getAttribute("href") === "#" + attiva);
    });
  }
  doc.addEventListener("scroll", function () { win.requestAnimationFrame(aggiornaScorrimento); }, true);
  win.setInterval(aggiornaScorrimento, 1200);

  // 2) Slide di "Come funziona": avanzano da sole ogni 6 secondi, si fermano
  //    con il mouse sopra o mentre l'utente le usa; frecce, pallini, tasti
  //    freccia e scorrimento col dito. Funziona anche su telefono.
  const DURATA = 6000;
  function mostraSlide(box, n, verso) {
    const slide = box.querySelectorAll(".ss-slide");
    if (!slide.length) { return; }
    const tot = slide.length;
    const prima = Number(box.dataset.attiva || 0);
    n = ((n % tot) + tot) % tot;
    slide.forEach(function (el, k) {
      const attiva = k === n;
      el.classList.toggle("attiva", attiva);
      el.classList.toggle("uscita", k === prima && !attiva && verso > 0);
      el.setAttribute("aria-hidden", attiva ? "false" : "true");
    });
    box.querySelectorAll(".ss-punto").forEach(function (p, k) { p.classList.toggle("attivo", k === n); });
    box.dataset.attiva = String(n);
    box.dataset.da = String(Date.now());
    // Riavvia la barra di avanzamento del pallino attivo.
    box.classList.remove("in-corsa"); void box.offsetWidth;
    box.classList.add("in-corsa");
  }
  function boxDa(el) { return el && el.closest ? el.closest(".ss-slides") : null; }
  doc.addEventListener("click", function (ev) {
    const box = boxDa(ev.target);
    if (!box) { return; }
    const freccia = ev.target.closest(".ss-freccia");
    const punto = ev.target.closest(".ss-punto");
    const attuale = Number(box.dataset.attiva || 0);
    if (freccia) { const v = Number(freccia.dataset.passo || 1); mostraSlide(box, attuale + v, v); }
    else if (punto) { const n = Number(punto.dataset.vai || 0); mostraSlide(box, n, n >= attuale ? 1 : -1); }
  }, true);
  doc.addEventListener("keydown", function (ev) {
    const box = boxDa(doc.activeElement);
    if (!box || (ev.key !== "ArrowRight" && ev.key !== "ArrowLeft")) { return; }
    const avanti = (ev.key === "ArrowRight") !== (box.closest("[dir=rtl]") !== null);
    mostraSlide(box, Number(box.dataset.attiva || 0) + (avanti ? 1 : -1), avanti ? 1 : -1);
    ev.preventDefault();
  }, true);
  let tocco = null;
  doc.addEventListener("pointerdown", function (ev) {
    const box = boxDa(ev.target);
    tocco = box && ev.pointerType !== "mouse" ? { box: box, x: ev.clientX, y: ev.clientY } : null;
  }, { passive: true, capture: true });
  doc.addEventListener("pointerup", function (ev) {
    if (!tocco) { return; }
    const dx = ev.clientX - tocco.x, dy = ev.clientY - tocco.y;
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.4) {
      const avanti = (dx < 0) !== (tocco.box.closest("[dir=rtl]") !== null);
      mostraSlide(tocco.box, Number(tocco.box.dataset.attiva || 0) + (avanti ? 1 : -1), avanti ? 1 : -1);
    }
    tocco = null;
  }, { passive: true, capture: true });
  function inPausa(box) {
    return box.matches(":hover") || box.contains(doc.activeElement) || doc.hidden;
  }
  win.setInterval(function () {
    doc.querySelectorAll(".ss-slides").forEach(function (box) {
      if (!box.dataset.da) {                                      // slide appena disegnata
        box.classList.add("js");                                  // lo script prende il comando
        mostraSlide(box, 0, 1); return;
      }
      const pausa = inPausa(box);
      box.classList.toggle("in-pausa", pausa);
      if (pausa) { box.dataset.da = String(Number(box.dataset.da) + 250); return; }
      if (Date.now() - Number(box.dataset.da) >= DURATA) {
        mostraSlide(box, Number(box.dataset.attiva || 0) + 1, 1);
      }
    });
  }, 250);

  if (!mouseVero || fermo) { return; }

  // 3) Schede che si inclinano verso il mouse, con una luce che lo segue.
  // 4) Pulsanti "magnetici" che si avvicinano leggermente al puntatore.
  let corrente = null, magnete = null, x = 0, y = 0, inAttesa = false;
  function azzera(el) {
    if (!el) { return; }
    el.style.removeProperty("--rx"); el.style.removeProperty("--ry");
    el.classList.remove("ss-segue");
  }
  function muovi() {
    inAttesa = false;
    const sotto = doc.elementFromPoint(x, y);
    const scheda = sotto && sotto.closest ? sotto.closest(SCHEDE) : null;
    if (scheda !== corrente) { azzera(corrente); corrente = scheda; }
    if (scheda) {
      const r = scheda.getBoundingClientRect();
      const px = (x - r.left) / r.width, py = (y - r.top) / r.height;
      const forza = scheda.classList.contains("ss-hero-copy") ? 2 : (scheda.classList.contains("ss-libro") ? 10 : 7);
      scheda.style.setProperty("--mx", (px * 100).toFixed(1) + "%");
      scheda.style.setProperty("--my", (py * 100).toFixed(1) + "%");
      scheda.style.setProperty("--ry", ((px - 0.5) * forza).toFixed(2) + "deg");
      scheda.style.setProperty("--rx", ((0.5 - py) * forza).toFixed(2) + "deg");
      scheda.classList.add("ss-segue");
    }
    const bottone = sotto && sotto.closest ? sotto.closest(MAGNETICI) : null;
    if (bottone !== magnete) {
      if (magnete) { magnete.style.removeProperty("translate"); }
      magnete = bottone;
    }
    if (bottone) {
      const r = bottone.getBoundingClientRect();
      const dx = (x - (r.left + r.width / 2)) / r.width, dy = (y - (r.top + r.height / 2)) / r.height;
      bottone.style.translate = (dx * 10).toFixed(1) + "px " + (dy * 6).toFixed(1) + "px";
    }
  }
  doc.addEventListener("pointermove", function (ev) {
    x = ev.clientX; y = ev.clientY;
    if (!inAttesa) { inAttesa = true; win.requestAnimationFrame(muovi); }
  }, { passive: true });
  doc.addEventListener("pointerleave", function () {
    azzera(corrente); corrente = null;
    if (magnete) { magnete.style.removeProperty("translate"); magnete = null; }
  });
})();
