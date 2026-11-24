// Home pubblica "inchiostro e oro": interazioni (slide, schede, cervelli,
// pacchetti, FAQ, menu). Gira nell'iframe invisibile di components.html e
// lavora sulla pagina principale. Senza script la home resta leggibile:
// si vedono la prima slide, la prima scheda e la prima domanda.
(function () {
  let doc, win;
  try { win = window.parent; doc = win.document; } catch (e) { return; }
  const VERSIONE = "v2-1";
  if (!doc || doc.__ssHomeV2 === VERSIONE) { return; }
  doc.__ssHomeV2 = VERSIONE;

  const DURATA = 5200;
  const radice = () => doc.querySelector(".ss2");

  // ---------- Slide del percorso ----------
  function mostra(box, n) {
    const slide = box.querySelectorAll(".ss2-slide");
    const tot = slide.length;
    if (!tot) { return; }
    n = ((n % tot) + tot) % tot;
    slide.forEach(function (el, k) {
      el.classList.toggle("attiva", k === n);
      el.classList.toggle("prima", k < n);
      el.setAttribute("aria-hidden", k === n ? "false" : "true");
    });
    box.querySelectorAll(".ss2-passo").forEach(function (p, k) {
      p.classList.toggle("attivo", k === n);
      p.setAttribute("aria-current", k === n ? "step" : "false");
    });
    const barra = box.querySelector(".ss2-avanzamento i");
    if (barra) { barra.style.width = ((n + 1) / tot * 100) + "%"; }
    box.dataset.attiva = String(n);
    box.dataset.da = String(Date.now());
  }
  win.setInterval(function () {
    doc.querySelectorAll("[data-percorso]").forEach(function (box) {
      if (!box.dataset.da) { mostra(box, 0); return; }
      const ferma = box.classList.contains("in-pausa-utente") || box.matches(":hover") || doc.hidden;
      if (ferma) { box.dataset.da = String(Number(box.dataset.da) + 250); return; }
      if (Date.now() - Number(box.dataset.da) >= DURATA) { mostra(box, Number(box.dataset.attiva || 0) + 1); }
    });
  }, 250);

  // ---------- Cervello scelto (cambia stime e riepilogo) ----------
  function scegliCervello(quale) {
    const r = radice(); if (!r) { return; }
    r.classList.toggle("cervello-pro", quale === "pro");
    r.querySelectorAll(".ss2-scelta-btn").forEach(function (b) {
      b.setAttribute("aria-checked", b.dataset.cervello === quale ? "true" : "false");
    });
    aggiornaRiepilogo();
  }
  function aggiornaRiepilogo() {
    const r = radice(); if (!r) { return; }
    const scelto = r.querySelector(".ss2-pacchetto.scelto") || r.querySelector(".ss2-pacchetto");
    if (!scelto) { return; }
    const pro = r.classList.contains("cervello-pro");
    r.querySelectorAll("[data-riepilogo]").forEach(function (el) {
      const campo = el.dataset.riepilogo;
      if (campo === "stima") { el.textContent = pro ? scelto.dataset.pro : scelto.dataset.eco; }
      else if (scelto.dataset[campo]) { el.textContent = scelto.dataset[campo]; }
    });
  }

  // ---------- Pulsanti di accesso: usano i pulsanti nascosti di Streamlit ----------
  function premiStreamlit(azione) {
    const chiave = azione === "accedi" ? ".st-key-ss2_accedi button" : ".st-key-ss2_registrati button";
    const b = doc.querySelector(chiave);
    if (b) { b.click(); return true; }
    return false;
  }

  doc.addEventListener("click", function (ev) {
    const t = ev.target && ev.target.closest ? ev.target : null;
    if (!t || !t.closest(".ss2")) {
      doc.querySelectorAll(".ss2 details[open]").forEach(function (d) { d.removeAttribute("open"); });
      return;
    }
    const link = t.closest("a[data-azione]");
    if (link) { if (premiStreamlit(link.dataset.azione)) { ev.preventDefault(); } return; }

    const box = t.closest("[data-percorso]");
    const passo = t.closest(".ss2-passo");
    const comando = t.closest("[data-comando]");
    if (box && passo) { mostra(box, Number(passo.dataset.slide || 0)); return; }
    if (box && comando) {
      const ora = Number(box.dataset.attiva || 0);
      if (comando.dataset.comando === "prec") { mostra(box, ora - 1); }
      else if (comando.dataset.comando === "succ") { mostra(box, ora + 1); }
      else {
        const pausa = box.classList.toggle("in-pausa-utente");
        comando.setAttribute("aria-label", pausa ? comando.dataset.riproduci : comando.dataset.pausa);
        if (!pausa) { box.dataset.da = String(Date.now()); }
      }
      return;
    }
    const pill = t.closest(".ss2-pill");
    if (pill) {
      const contenitore = pill.closest(".ss2-vantaggi"); const n = pill.dataset.vantaggio;
      contenitore.querySelectorAll(".ss2-pill").forEach(function (b) {
        const on = b.dataset.vantaggio === n; b.classList.toggle("attivo", on); b.setAttribute("aria-selected", on ? "true" : "false");
      });
      contenitore.querySelectorAll(".ss2-pannello").forEach(function (p) { p.classList.toggle("attivo", p.dataset.vantaggio === n); });
      return;
    }
    const cervello = t.closest(".ss2-scelta-btn");
    if (cervello) { scegliCervello(cervello.dataset.cervello); return; }
    const pacchetto = t.closest(".ss2-pacchetto");
    if (pacchetto) {
      pacchetto.parentElement.querySelectorAll(".ss2-pacchetto").forEach(function (p) {
        const on = p === pacchetto; p.classList.toggle("scelto", on); p.setAttribute("aria-pressed", on ? "true" : "false");
      });
      aggiornaRiepilogo(); return;
    }
    const domanda = t.closest(".ss2-faq-domanda");
    if (domanda) {
      const voce = domanda.closest(".ss2-faq"); const aprire = !voce.classList.contains("aperta");
      voce.parentElement.querySelectorAll(".ss2-faq").forEach(function (f) {
        f.classList.remove("aperta"); f.querySelector(".ss2-faq-domanda").setAttribute("aria-expanded", "false");
      });
      if (aprire) { voce.classList.add("aperta"); domanda.setAttribute("aria-expanded", "true"); }
      return;
    }
    // chiude i menu aperti se si clicca altrove
    doc.querySelectorAll(".ss2 details[open]").forEach(function (d) { if (!d.contains(t)) { d.removeAttribute("open"); } });
    // le voci del menu su telefono chiudono il menu
    const voceMenu = t.closest(".ss2-menu-mobile nav a");
    if (voceMenu) { voceMenu.closest("details").removeAttribute("open"); }
  }, true);

  // ---------- Barra di lettura + voce del menu attiva ----------
  const sezioni = ["ss-percorso", "ss-funzioni", "ss-vantaggi", "ss-cervelli", "ss-crediti", "ss-faq", "ss-guide"];
  function scorri() {
    const c = doc.querySelector('[data-testid="stMain"]');
    if (!c || !radice()) { return; }
    const max = Math.max(1, c.scrollHeight - c.clientHeight);
    doc.documentElement.style.setProperty("--ss-scroll", (c.scrollTop / max).toFixed(4));
    let attiva = "";
    const soglia = c.getBoundingClientRect().top + c.clientHeight * 0.35;
    sezioni.forEach(function (id) {
      const el = doc.getElementById(id);
      if (el && el.getBoundingClientRect().top <= soglia) { attiva = id; }
    });
    doc.querySelectorAll(".ss2-nav-link").forEach(function (a) {
      a.classList.toggle("ss-attivo", attiva !== "" && a.getAttribute("href") === "#" + attiva);
    });
  }
  doc.addEventListener("scroll", function () { win.requestAnimationFrame(scorri); }, true);
  win.setInterval(scorri, 1200);
})();
