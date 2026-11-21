// Home pubblica: interazioni che seguono il mouse.
// Gira nell'iframe invisibile di components.html e lavora sulla pagina
// principale. Se il browser non lo permette, la home resta solo CSS.
(function () {
  let doc, win;
  try { win = window.parent; doc = win.document; } catch (e) { return; }
  if (!doc || doc.__ssHomeInterattiva) { return; }
  doc.__ssHomeInterattiva = true;

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

  if (!mouseVero || fermo) { return; }

  // 2) Schede che si inclinano verso il mouse, con una luce che lo segue.
  // 3) Pulsanti "magnetici" che si avvicinano leggermente al puntatore.
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
