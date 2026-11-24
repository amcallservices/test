// Visita guidata dell'editor: parte da sola al primo accesso (una volta per
// browser) oppure quando l'utente preme "Rivedi la visita guidata".
// Lavora sulla pagina principale dall'iframe invisibile di components.html.
// Se qualcosa non è disponibile, non fa nulla: l'editor resta identico.
(function () {
  const DATI = __DATI_TOUR__;
  const FORZA = __FORZA_TOUR__;
  const CHIAVE = "ss_tour_editor_v2";   // v2: visita completa (24 passi)
  let doc, win;
  try { win = window.parent; doc = win.document; } catch (e) { return; }
  if (!doc || doc.__ssTourAttivo) { return; }
  let giaVisto = false;
  try { giaVisto = win.localStorage.getItem(CHIAVE) === "1"; } catch (e) { giaVisto = false; }
  if (giaVisto && !FORZA) { return; }

  function segnaVisto() { try { win.localStorage.setItem(CHIAVE, "1"); } catch (e) {} }

  function avvia() {
    if (doc.__ssTourAttivo) { return; }
    doc.__ssTourAttivo = true;
    const SEL_SCHEDE = '[data-testid="stTabs"] [role="tab"]';
    function visibile(el) {
      if (!el) { return false; }
      const r = el.getBoundingClientRect();
      return r.width > 4 && r.height > 4;
    }
    // Elemento del passo: quello principale se visibile, altrimenti la riserva.
    function trova(p) {
      if (!p || !p.sel) { return null; }
      const el = doc.querySelector(p.sel);
      if (visibile(el)) { return el; }
      const alt = p.alt ? doc.querySelector(p.alt) : null;
      return visibile(alt) ? alt : (el || alt);
    }
    const passi = DATI.passi.filter(function (p) {
      return !p.sel || p.scheda !== null && p.scheda !== undefined || doc.querySelector(p.sel) || (p.alt && doc.querySelector(p.alt));
    });
    let i = 0;
    // Scheda aperta all'inizio: la visita ci torna alla fine.
    const schedaIniziale = (function () {
      const tutte = Array.from(doc.querySelectorAll(SEL_SCHEDE));
      return tutte.findIndex(function (t) { return t.getAttribute("aria-selected") === "true"; });
    })();
    function apriScheda(n, fatto) {
      const tutte = doc.querySelectorAll(SEL_SCHEDE);
      const scheda = tutte[n];
      if (!scheda || scheda.getAttribute("aria-selected") === "true") { fatto(); return; }
      scheda.click();
      win.setTimeout(fatto, 450);   // il contenuto della scheda compare subito, poi si assesta
    }

    const stile = doc.createElement("style");
    stile.textContent = [
      ".ss-tour-velo{position:fixed;inset:0;z-index:2147483000;background:transparent}",
      ".ss-tour-luce{position:fixed;z-index:2147483001;border:2px solid #f2b84b;border-radius:14px;",
      "box-shadow:0 0 0 9999px rgba(6,9,18,.76),0 0 22px rgba(242,184,75,.45);transition:all .35s cubic-bezier(.22,.8,.26,1);pointer-events:none}",
      ".ss-tour-fumetto{position:fixed;z-index:2147483002;max-width:min(360px,calc(100vw - 32px));padding:1.05rem 1.1rem .9rem;",
      "border-radius:16px;background:#121a2e;color:#f4efe6;border:1px solid #5a4620;",
      "box-shadow:0 18px 40px rgba(0,0,0,.45);font:15px/1.5 'Source Sans Pro',system-ui,sans-serif;transition:top .35s ease,left .35s ease}",
      ".ss-tour-fumetto b{display:block;font:500 1.2rem/1.2 'Fraunces',Georgia,serif;margin-bottom:.4rem;color:#fbf7ef}",
      ".ss-tour-fumetto p{margin:0 0 .85rem;color:#b6bfd3}",
      ".ss-tour-barra{display:flex;align-items:center;gap:.4rem}",
      ".ss-tour-barra small{margin-inline-end:auto;color:#f2b84b;font-weight:700}",
      ".ss-tour-barra button{border:0;border-radius:999px;padding:.42rem .85rem;font:700 13px/1 inherit;cursor:pointer}",
      ".ss-tour-salta{background:transparent;color:#8e99b3}",
      ".ss-tour-indietro{background:transparent;color:#f4efe6;box-shadow:inset 0 0 0 1px #2d3858}",
      ".ss-tour-avanti{background:#f2b84b;color:#1a1206}",
      ".ss-tour-barra button:focus-visible{outline:3px solid #7cc4f5;outline-offset:2px}",
      ".ss-tour-avanzamento{height:3px;border-radius:3px;background:#1c2540;margin:0 0 .8rem;overflow:hidden}",
      ".ss-tour-avanzamento i{display:block;height:100%;background:#f2b84b;transition:width .35s ease}"
    ].join("");
    doc.head.appendChild(stile);

    const velo = doc.createElement("div"); velo.className = "ss-tour-velo";
    const luce = doc.createElement("div"); luce.className = "ss-tour-luce";
    const fumetto = doc.createElement("div"); fumetto.className = "ss-tour-fumetto";
    fumetto.setAttribute("role", "dialog");
    if (DATI.rtl) { fumetto.dir = "rtl"; }
    doc.body.appendChild(velo); doc.body.appendChild(luce); doc.body.appendChild(fumetto);

    function chiudi() {
      segnaVisto();
      if (schedaIniziale >= 0) {
        const tutte = doc.querySelectorAll(SEL_SCHEDE);
        if (tutte[schedaIniziale] && tutte[schedaIniziale].getAttribute("aria-selected") !== "true") { tutte[schedaIniziale].click(); }
      }
      [velo, luce, fumetto, stile].forEach(function (el) { if (el.parentNode) { el.parentNode.removeChild(el); } });
      win.removeEventListener("resize", posiziona);
      doc.removeEventListener("scroll", suScroll, true);
      doc.removeEventListener("keydown", tasti, true);
      doc.__ssTourAttivo = false;
    }
    function tasti(ev) {
      if (ev.key === "Escape") { chiudi(); }
      else if (ev.key === "ArrowRight") { vai(1); }
      else if (ev.key === "ArrowLeft") { vai(-1); }
    }

    // ---- Telefono: la sidebar copre la pagina, quindi la visita la apre per i
    // passi della sidebar e la chiude per quelli della pagina. ----
    const SEL_SIDEBAR = '[data-testid="stSidebar"]';
    function telefono() { return win.innerWidth < 768; }
    function sidebarAperta() {
      const sb = doc.querySelector(SEL_SIDEBAR);
      return !!sb && sb.getBoundingClientRect().right > 120;
    }
    function preparaSidebar(p, fatto) {
      if (!telefono() || !p.sel) { fatto(); return; }
      const el = trova(p);
      if (!el) { fatto(); return; }
      const vuoleAperta = p.sel === SEL_SIDEBAR || !!el.closest(SEL_SIDEBAR);
      if (sidebarAperta() === vuoleAperta) { fatto(); return; }
      const bottone = vuoleAperta
        ? doc.querySelector('[data-testid="stExpandSidebarButton"]') || doc.querySelector('button[aria-controls="stSidebar"][aria-expanded="false"]')
        : doc.querySelector('[data-testid="stSidebarCollapseButton"] button') || doc.querySelector('button[aria-controls="stSidebar"][aria-expanded="true"]');
      if (!bottone) { fatto(); return; }
      bottone.click();
      win.setTimeout(fatto, 520);   // attende la fine dell'animazione della sidebar
    }

    function bersaglio() {
      const p = passi[i];
      if (!p || !p.sel) { return null; }
      const el = trova(p);
      if (!el) { return null; }
      const r = el.getBoundingClientRect();
      // Sidebar chiusa (telefono) o elemento invisibile: fumetto al centro.
      if (r.width < 8 || r.height < 8 || r.right <= 0) { return null; }
      // Elemento coperto (es. sidebar aperta sopra la pagina su telefono).
      const cx = Math.min(Math.max(r.left + r.width / 2, 1), win.innerWidth - 1);
      const cy = Math.min(Math.max(r.top + r.height / 2, 1), win.innerHeight - 1);
      const pe = velo.style.pointerEvents, vis = fumetto.style.visibility;
      velo.style.pointerEvents = "none"; fumetto.style.visibility = "hidden";
      const sopra = doc.elementFromPoint(cx, cy);
      velo.style.pointerEvents = pe; fumetto.style.visibility = vis;
      if (sopra && !el.contains(sopra) && !sopra.contains(el)) { return null; }
      return el;
    }

    function posiziona() {
      const el = bersaglio();
      const vw = win.innerWidth, vh = win.innerHeight;
      const fw = fumetto.offsetWidth, fh = fumetto.offsetHeight;
      if (!el) {
        luce.style.cssText = "top:50%;left:50%;width:0;height:0;";
        fumetto.style.top = Math.max(16, (vh - fh) / 2) + "px";
        fumetto.style.left = Math.max(16, (vw - fw) / 2) + "px";
        return;
      }
      const r = el.getBoundingClientRect();
      const m = el.matches(SEL_SIDEBAR) ? -2 : 6;
      const top = Math.min(Math.max(3, r.top - m), vh - 24);
      const left = Math.min(Math.max(3, r.left - m), vw - 24);
      const destra = Math.min(vw - 3, r.right + m), basso = Math.min(vh - 3, r.bottom + m);
      const w = Math.max(20, destra - left), h = Math.max(20, basso - top);
      luce.style.cssText = "top:" + top + "px;left:" + left + "px;width:" + w + "px;height:" + h + "px;";
      let ft, fl;
      if (r.width < vw * 0.4 && r.right + fw + 24 < vw) {        // a destra (es. sidebar)
        ft = Math.min(Math.max(16, r.top + 24), vh - fh - 16); fl = r.right + 18;
      } else if (r.bottom + fh + 24 < vh) {                        // sotto
        ft = r.bottom + 16; fl = Math.min(Math.max(16, r.left), vw - fw - 16);
      } else if (r.top - fh - 24 > 0) {                            // sopra
        ft = r.top - fh - 16; fl = Math.min(Math.max(16, r.left), vw - fw - 16);
      } else {                                                     // dentro, in basso
        ft = vh - fh - 24; fl = Math.max(16, (vw - fw) / 2);
      }
      // Il fumetto resta sempre dentro lo schermo.
      ft = Math.min(Math.max(16, ft), Math.max(16, vh - fh - 16));
      fl = Math.min(Math.max(16, fl), Math.max(16, vw - fw - 16));
      fumetto.style.top = ft + "px"; fumetto.style.left = fl + "px";
    }
    let inAttesa = false;
    function suScroll() {
      if (inAttesa) { return; }
      inAttesa = true;
      win.requestAnimationFrame(function () { inAttesa = false; posiziona(); });
    }

    function disegna() {
      const p = passi[i];
      fumetto.style.visibility = "hidden"; luce.style.opacity = "0";
      const dopoScheda = function () { preparaSidebar(p, function () { mostra(p); }); };
      if (p && p.scheda !== null && p.scheda !== undefined) { apriScheda(p.scheda, dopoScheda); } else { dopoScheda(); }
    }
    function mostra(p) {
      const ultimo = i === passi.length - 1;
      fumetto.innerHTML = "";
      const t = doc.createElement("b"); t.textContent = p.titolo;
      const x = doc.createElement("p"); x.textContent = p.testo;
      const barra = doc.createElement("div"); barra.className = "ss-tour-barra";
      const conta = doc.createElement("small"); conta.textContent = (i + 1) + " / " + passi.length;
      barra.appendChild(conta);
      if (!ultimo) {
        const salta = doc.createElement("button"); salta.className = "ss-tour-salta"; salta.textContent = DATI.salta;
        salta.onclick = chiudi; barra.appendChild(salta);
      }
      if (i > 0) {
        const indietro = doc.createElement("button"); indietro.className = "ss-tour-indietro"; indietro.textContent = DATI.indietro;
        indietro.onclick = function () { vai(-1); }; barra.appendChild(indietro);
      }
      const avanti = doc.createElement("button"); avanti.className = "ss-tour-avanti";
      avanti.textContent = ultimo ? DATI.fine : DATI.avanti;
      avanti.onclick = function () { if (ultimo) { chiudi(); } else { vai(1); } };
      barra.appendChild(avanti);
      const avanzamento = doc.createElement("div"); avanzamento.className = "ss-tour-avanzamento";
      const pieno = doc.createElement("i"); pieno.style.width = ((i + 1) / passi.length * 100) + "%";
      avanzamento.appendChild(pieno);
      fumetto.appendChild(avanzamento); fumetto.appendChild(t); fumetto.appendChild(x); fumetto.appendChild(barra);
      // Prima porta l'elemento in vista (scorrimento immediato), poi controlla
      // se è visibile e calcola la posizione sull'elemento già fermo.
      const grezzo = trova(p);
      if (grezzo && grezzo.scrollIntoView && !grezzo.matches(SEL_SIDEBAR)) {
        // Elementi alti (es. Centro del progetto su telefono): in cima allo
        // schermo, così il fumetto trova spazio sotto.
        const alto = grezzo.getBoundingClientRect().height > win.innerHeight * 0.45;
        grezzo.scrollIntoView({ block: alto ? "start" : "center", behavior: "auto" });
      }
      posiziona();
      fumetto.style.visibility = "visible"; luce.style.opacity = "1";
      win.setTimeout(posiziona, 150);
      win.setTimeout(posiziona, 600);
      avanti.focus({ preventScroll: true });
    }
    function vai(passo) {
      const nuovo = i + passo;
      if (nuovo < 0 || nuovo >= passi.length) { return; }
      i = nuovo; disegna();
    }

    win.addEventListener("resize", posiziona);
    doc.addEventListener("scroll", suScroll, true);
    doc.addEventListener("keydown", tasti, true);
    disegna();
  }

  // Attende che l'editor sia disegnato (sidebar e menu presenti).
  let tentativi = 0;
  (function attendi() {
    tentativi += 1;
    if (doc.querySelector('[data-testid="stTabs"] [role="tablist"]') || tentativi > 40) {
      win.setTimeout(avvia, 600);
    } else {
      win.setTimeout(attendi, 250);
    }
  })();
})();
