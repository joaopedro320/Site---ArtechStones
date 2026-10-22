/* Artechstone · site.js v2
   Base (sem dependências) + camada de movimento com GSAP, ScrollTrigger, SplitText e Lenis (em assets/js/vendor). */
(function () {
  "use strict";
  var d = document, w = window, html = d.documentElement;
  var I = {};
  try { I = JSON.parse(d.getElementById("i18n").textContent); } catch (e) {}
  w.dataLayer = w.dataLayer || [];
  function track(ev, data) { var o = { event: ev }; for (var k in data) o[k] = data[k]; w.dataLayer.push(o); }
  var store = {
    get: function (k, s) { try { return (s ? w.sessionStorage : w.localStorage).getItem(k); } catch (e) { return null; } },
    set: function (k, v, s) { try { (s ? w.sessionStorage : w.localStorage).setItem(k, v); } catch (e) {} }
  };
  var reduce = w.matchMedia && w.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fine = w.matchMedia && w.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var desktop = function () { return w.innerWidth > 1100; };
  var hasGsap = !!(w.gsap && w.ScrollTrigger) && !reduce;
  var lenis = null;

  /* ---------------- título do hero cabe na largura ---------------- */
  var fitHero = function () {
    d.querySelectorAll(".hero-a,.hero-b").forEach(function (el) {
      if (w.innerWidth <= 760) { el.style.fontSize = ""; return; }
      el.style.fontSize = ""; var max = w.innerWidth * .94, cs = parseFloat(getComputedStyle(el).fontSize);
      var span = d.createElement("span"); span.style.cssText = "position:absolute;visibility:hidden;white-space:nowrap;font:inherit;letter-spacing:inherit;text-transform:inherit"; span.textContent = el.textContent; el.appendChild(span);
      var wdt = span.getBoundingClientRect().width; span.remove();
      if (wdt > max) el.style.fontSize = (cs * max / wdt) + "px";
    });
  };
  var footH = function () { var hf = d.querySelector(".hero-foot"), hero = d.querySelector(".hero"); if (hf && hero) hero.style.setProperty("--foot-h", hf.offsetHeight + "px"); };
  fitHero(); footH(); w.addEventListener("resize", function () { fitHero(); footH(); });

  /* ---------------- header ---------------- */
  var header = d.querySelector("[data-header]"), lastY = 0;
  function onScroll(y) {
    y = typeof y === "number" ? y : (w.scrollY || 0);
    if (header) {
      header.classList.toggle("scrolled", y > 40);
      if (!d.body.classList.contains("menu-open") && w.innerWidth > 1100) {
        if (y > 520 && y > lastY + 3) header.classList.add("hidden");
        else if (y < lastY - 3 || y < 520) header.classList.remove("hidden");
      }
    }
    lastY = y;
  }
  w.addEventListener("scroll", function () { onScroll(); }, { passive: true }); onScroll();

  /* menu mobile */
  var mbtn = d.querySelector("[data-menu]"), nav = d.getElementById("site-nav");
  if (mbtn && nav) {
    mbtn.addEventListener("click", function () {
      var open = mbtn.getAttribute("aria-expanded") !== "true";
      mbtn.setAttribute("aria-expanded", open); nav.classList.toggle("open", open);
      d.body.classList.toggle("menu-open", open);
      if (lenis) { open ? lenis.stop() : lenis.start(); } else d.body.style.overflow = open ? "hidden" : "";
    });
    d.addEventListener("keydown", function (e) { if (e.key === "Escape" && nav.classList.contains("open")) mbtn.click(); });
  }

  /* idioma */
  d.addEventListener("click", function (e) {
    d.querySelectorAll("details.lang[open]").forEach(function (el) { if (!el.contains(e.target)) el.removeAttribute("open"); });
  });
  d.querySelectorAll("details.lang a[data-lang]").forEach(function (a) {
    a.addEventListener("click", function () { store.set("as_lang", a.getAttribute("data-lang")); track("language_switch", { to: a.getAttribute("data-lang") }); });
  });
  (function () {
    if (!I.suggest || store.get("as_lang") || store.get("as_hint")) return;
    var langs = (navigator.languages || [navigator.language || ""]).map(function (l) { return (l || "").toLowerCase().slice(0, 2); });
    var pick = null;
    for (var i = 0; i < langs.length; i++) { if (I.suggest[langs[i]]) { pick = langs[i]; break; } }
    if (!pick || pick === I.lang) return;
    var s = I.suggest[pick], box = d.createElement("div");
    box.className = "lang-hint"; box.setAttribute("role", "dialog"); box.setAttribute("lang", pick);
    box.innerHTML = '<p></p><div class="row"><a class="btn btn-solid btn-sm"></a><button type="button"></button></div>';
    box.querySelector("p").textContent = s.text;
    var a = box.querySelector("a"); a.textContent = s.btn; a.href = s.url;
    var b = box.querySelector("button"); b.textContent = s.dismiss;
    a.addEventListener("click", function () { store.set("as_lang", pick); });
    b.addEventListener("click", function () { store.set("as_hint", "1"); box.remove(); });
    setTimeout(function () { d.body.appendChild(box); }, 3200);
  })();

  /* ---------------- lightbox ---------------- */
  var items = [].slice.call(d.querySelectorAll(".g-item"));
  if (items.length) {
    var lb = d.createElement("div"), idx = 0, lastFocus = null, sx = 0;
    var ic = function (p) { return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="' + p + '"/></svg>'; };
    lb.className = "lb"; lb.setAttribute("role", "dialog"); lb.setAttribute("aria-modal", "true"); lb.setAttribute("aria-hidden", "true");
    lb.innerHTML = '<img alt=""><button class="lb-prev" type="button" aria-label="' + I.gallery[0] + '">' + ic("M15 5l-7 7 7 7") + '</button><button class="lb-next" type="button" aria-label="' + I.gallery[1] + '">' + ic("M9 5l7 7-7 7") + '</button><button class="lb-close" type="button" aria-label="' + I.gallery[2] + '">' + ic("M6 6l12 12M18 6L6 18") + '</button><p class="lb-count" aria-live="polite"></p>';
    d.body.appendChild(lb);
    var limg = lb.querySelector("img"), cnt = lb.querySelector(".lb-count");
    var show = function (i) { idx = (i + items.length) % items.length; var it = items[idx]; limg.style.opacity = 0; limg.onload = function () { limg.style.opacity = 1; }; limg.src = it.getAttribute("data-full"); limg.alt = it.getAttribute("data-alt"); cnt.textContent = (idx + 1) + " / " + items.length; };
    var open = function (i) { lastFocus = d.activeElement; show(i); lb.classList.add("open"); lb.setAttribute("aria-hidden", "false"); if (lenis) lenis.stop(); else d.body.style.overflow = "hidden"; lb.querySelector(".lb-close").focus(); track("gallery_open", { index: i + 1 }); };
    var close = function () { lb.classList.remove("open"); lb.setAttribute("aria-hidden", "true"); if (lenis) lenis.start(); else d.body.style.overflow = ""; if (lastFocus) lastFocus.focus(); };
    var moved = false;
    items.forEach(function (it, i) {
      it.addEventListener("pointerdown", function () { moved = false; });
      it.addEventListener("click", function () { if (!moved) open(i); });
    });
    lb.querySelector(".lb-prev").addEventListener("click", function () { show(idx - 1); });
    lb.querySelector(".lb-next").addEventListener("click", function () { show(idx + 1); });
    lb.querySelector(".lb-close").addEventListener("click", close);
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    d.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("open")) return;
      if (e.key === "Escape") close(); else if (e.key === "ArrowLeft") show(idx - 1); else if (e.key === "ArrowRight") show(idx + 1);
      else if (e.key === "Tab") { var f = lb.querySelectorAll("button"), first = f[0], last = f[f.length - 1]; if (e.shiftKey && d.activeElement === first) { e.preventDefault(); last.focus(); } else if (!e.shiftKey && d.activeElement === last) { e.preventDefault(); first.focus(); } }
    });
    lb.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) { var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1)); }, { passive: true });
  }

  /* ---------------- depoimentos ---------------- */
  var testi = d.querySelector("[data-testi]");
  if (testi) {
    var tqs = [].slice.call(testi.querySelectorAll("[data-tq]")), dts = [].slice.call(testi.querySelectorAll("[data-tdot]")), ti = 0, timer = null;
    var go = function (n) {
      ti = (n + tqs.length) % tqs.length;
      tqs.forEach(function (q, i) { q.classList.toggle("on", i === ti); });
      dts.forEach(function (b, i) { b.classList.remove("on"); void b.offsetWidth; b.classList.toggle("on", i === ti); });
    };
    var start = function () { clearInterval(timer); timer = setInterval(function () { go(ti + 1); }, 6000); };
    testi.querySelector("[data-tq-prev]").addEventListener("click", function () { go(ti - 1); start(); });
    testi.querySelector("[data-tq-next]").addEventListener("click", function () { go(ti + 1); start(); });
    dts.forEach(function (b, i) { b.addEventListener("click", function () { go(i); start(); }); });
    testi.addEventListener("mouseenter", function () { clearInterval(timer); testi.classList.add("paused"); });
    testi.addEventListener("mouseleave", function () { testi.classList.remove("paused"); start(); });
    if (!reduce) start();
  }

  /* ---------------- quem atendemos: imagem troca ---------------- */
  var whoItems = [].slice.call(d.querySelectorAll("[data-who]")), whoImgs = [].slice.call(d.querySelectorAll("[data-who-img]"));
  function setWho(i) {
    whoItems.forEach(function (li) { li.classList.toggle("on", li.getAttribute("data-who") == i); });
    whoImgs.forEach(function (im) { im.classList.toggle("on", im.getAttribute("data-who-img") == i); });
  }
  if (whoItems.length) {
    setWho(0);
    whoItems.forEach(function (li) { li.addEventListener("mouseenter", function () { setWho(li.getAttribute("data-who")); }); });
  }

  /* ---------------- catálogo ---------------- */
  var cat = d.querySelector("[data-catalog]");
  if (cat && cat.querySelector("[data-search]")) {
    var chips = [].slice.call(cat.querySelectorAll("[data-filter]")), q = cat.querySelector("[data-search]"),
        cards = [].slice.call(cat.querySelectorAll(".stone")), countEl = cat.querySelector("[data-count]"), empty = cat.querySelector("[data-empty]"), active = "all";
    var norm = function (s) { return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); };
    var apply = function (anim) {
      var term = norm(q.value.trim()), n = 0, shown = [];
      cards.forEach(function (c) { var ok = (active === "all" || c.getAttribute("data-line") === active) && (!term || norm(c.getAttribute("data-name")).indexOf(term) > -1); c.hidden = !ok; if (ok) { n++; shown.push(c); } });
      countEl.textContent = (I.results || "{n}").replace("{n}", n); empty.hidden = n > 0;
      if (anim && hasGsap) { gsap.fromTo(shown.slice(0, 16), { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: .8, ease: "expo.out", stagger: .035, overwrite: true }); }
      if (w.ScrollTrigger) ScrollTrigger.refresh();
    };
    chips.forEach(function (ch) { ch.addEventListener("click", function () { active = ch.getAttribute("data-filter"); chips.forEach(function (c) { c.setAttribute("aria-pressed", c === ch); }); apply(true); track("catalog_filter", { line: active }); }); });
    var tmr; q.addEventListener("input", function () { clearTimeout(tmr); tmr = setTimeout(function () { apply(true); }, 140); });
    try { var p = new URLSearchParams(w.location.search); if (p.get("q")) q.value = p.get("q"); var l = p.get("linha") || p.get("line"); if (l) chips.forEach(function (c) { if (c.getAttribute("data-filter") === l) c.click(); }); } catch (e) {}
    apply(false);
  }

  /* ---------------- formulários -> WhatsApp -> obrigado ---------------- */
  d.querySelectorAll("form[data-form]").forEach(function (f) {
    var btn = f.querySelector("button[type=submit]");
    var check = function () { btn.disabled = !f.checkValidity(); };
    f.addEventListener("input", check); f.addEventListener("change", check);
    f.querySelectorAll("input,select,textarea").forEach(function (el) { el.addEventListener("blur", function () { el.classList.add("touched"); }); });
    check();
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!f.checkValidity()) { f.reportValidity(); return; }
      var lines = [f.getAttribute("data-intro"), ""];
      f.querySelectorAll("input,select,textarea").forEach(function (el) { if (el.value && el.value.trim()) lines.push("*" + el.name + ":* " + el.value.trim()); });
      var url = "https://wa.me/" + I.wa + "?text=" + encodeURIComponent(lines.join("\n"));
      track("generate_lead", { form: f.getAttribute("data-form"), lang: I.lang });
      store.set("as_wa", url, true);
      var win = w.open(url, "_blank"); if (win) { try { win.opener = null; } catch (err) {} }
      setTimeout(function () { w.location.href = I.thanks + (win ? "" : "#wa"); }, 300);
    });
  });
  var tw = d.querySelector("[data-thanks-wa]");
  if (tw) { var u = store.get("as_wa", true); if (u) { tw.href = u; if (w.location.hash === "#wa") w.location.href = u; } }

  /* ---------------- rastreamento ---------------- */
  d.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-track]");
    if (a) track(a.getAttribute("data-track"), { place: a.getAttribute("data-place") || "", lang: I.lang });
    var t = e.target.closest && e.target.closest('a[href^="tel:"],a[href^="mailto:"]');
    if (t) track(t.href.indexOf("tel:") === 0 ? "phone_click" : "email_click", { lang: I.lang });
  });

  /* ======================= MOVIMENTO ======================= */
  if (!hasGsap) { html.classList.remove("js"); return; }
  w.__motion = true;
  gsap.registerPlugin(ScrollTrigger); if (w.SplitText) gsap.registerPlugin(SplitText);
  var EASE = "expo.out";

  /* scroll suave */
  if (w.Lenis) {
    lenis = new Lenis({ duration: 1.15, easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); }, smoothWheel: true });
    lenis.on("scroll", function (e) { ScrollTrigger.update(); onScroll(e.scroll); });
    gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
    gsap.ticker.lagSmoothing(0);
    d.querySelectorAll('a[href^="#"]').forEach(function (a) { a.addEventListener("click", function (e) { var id = a.getAttribute("href"); if (id.length > 1 && d.querySelector(id)) { e.preventDefault(); lenis.scrollTo(id, { offset: -90 }); } }); });
  }

  /* textos em linhas */
  var splitAll = function () {
    var targets = d.querySelectorAll("[data-split], .h2");
    targets.forEach(function (el) {
      if (el.closest(".hero-h1") || el.__split) return; el.__split = true;
      var lines;
      if (w.SplitText) { var st = new SplitText(el, { type: "words,lines", linesClass: "sl" }); lines = st.lines; }
      else lines = [el];
      gsap.set(lines, { y: 46, opacity: 0 });
      ScrollTrigger.create({ trigger: el, start: "top 90%", once: true, onEnter: function () { gsap.to(lines, { y: 0, opacity: 1, duration: 1.3, ease: EASE, stagger: .09 }); } });
    });
  };

  /* fades */
  var fadeAll = function () {
    var sel = "[data-fade], .prose p, .spec, .ticks li, .stone, .qa, .w-block, .care-list>div, .people li, .who-list li, .contact-list li, .lines-nav li, .counters li, .form-card, .place h3, .place address, .crumbs, .faq-aside-in, .chips, .search, .ln-text > *, .tq-ctrl, .foot-col, .foot-brand";
    gsap.utils.toArray(sel).forEach(function (el) {
      if (el.closest(".hero") || el.__fade) return; el.__fade = true;
      gsap.fromTo(el, { opacity: 0, y: 34 }, { opacity: 1, y: 0, duration: 1.2, ease: EASE, scrollTrigger: { trigger: el, start: "top 92%", once: true } });
    });
    ScrollTrigger.batch(".stones .stone", { start: "top 94%", once: true, onEnter: function (b) { gsap.fromTo(b, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 1.1, ease: EASE, stagger: .06, overwrite: true }); } });
  };

  /* revelação de imagens + parallax interno */
  var mediaAll = function () {
    gsap.utils.toArray("[data-reveal]").forEach(function (el) {
      var im = el.querySelector("img");
      var tl = gsap.timeline({ scrollTrigger: { trigger: el, start: "top 90%", once: true } });
      tl.fromTo(el, { clipPath: "inset(100% 0% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 1.6, ease: "expo.inOut" });
      if (im) tl.fromTo(im, { scale: 1.35 }, { scale: 1, duration: 2, ease: EASE }, 0);
    });
    gsap.utils.toArray("[data-speed]").forEach(function (el) {
      var sp = parseFloat(el.getAttribute("data-speed")) || -.1;
      gsap.fromTo(el, { yPercent: -sp * 50 }, { yPercent: sp * 50, ease: "none", scrollTrigger: { trigger: el.parentElement, start: "top bottom", end: "bottom top", scrub: true } });
    });
  };

  /* hero: título dividido + moldura que encolhe ao rolar */
  var heroAnim = function (delay) {
    var hero = d.querySelector("[data-hero]"); if (!hero) return;
    var a = hero.querySelector("[data-hero-a]"), b = hero.querySelector("[data-hero-b]"), frame = hero.querySelector("[data-hero-frame]"), img = hero.querySelector(".hero-media img");
    var ca = [a], cb = [b];
    if (w.SplitText) { ca = new SplitText(a, { type: "words,chars" }).chars; cb = new SplitText(b, { type: "words,chars" }).chars; }
    gsap.set([a, b], { opacity: 1 });
    var tl = gsap.timeline({ delay: delay || 0 });
    tl.fromTo(img, { scale: 1.3 }, { scale: 1.08, duration: 2.6, ease: EASE }, 0)
      .fromTo(ca, { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 1.4, ease: EASE, stagger: .028 }, .15)
      .fromTo(cb, { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 1.4, ease: EASE, stagger: .028 }, .32)
      .fromTo(hero.querySelectorAll("[data-fade]"), { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 1.2, ease: EASE, stagger: .1 }, .7)
      .fromTo(header, { yPercent: -100 }, { yPercent: 0, duration: 1.2, ease: EASE, clearProps: "transform" }, .6);
    var mm = gsap.matchMedia();
    mm.add("(min-width: 761px)", function () {
      gsap.timeline({ scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: true } })
        .to(frame, { clipPath: "inset(7% 4% 7% 4% round 18px)", ease: "none" }, 0)
        .to(img, { scale: 1.22, yPercent: 8, ease: "none" }, 0)
        .to(a, { xPercent: -16, ease: "none" }, 0)
        .to(b, { xPercent: 16, ease: "none" }, 0)
        .to(hero.querySelector(".hero-foot"), { opacity: 0, y: -40, ease: "none" }, 0);
    });
    mm.add("(max-width: 760px)", function () {
      gsap.to(img, { yPercent: 12, ease: "none", scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: true } });
    });
  };

  /* statement: palavras acendem conforme a rolagem */
  var wordsAnim = function () {
    d.querySelectorAll("[data-words]").forEach(function (el) {
      var words;
      if (w.SplitText) words = new SplitText(el, { type: "words" }).words;
      else return;
      gsap.fromTo(words, { color: "rgba(255,255,255,.16)" }, { color: "rgba(255,255,255,1)", ease: "none", stagger: .1, scrollTrigger: { trigger: el, start: "top 80%", end: "bottom 40%", scrub: true } });
    });
  };

  /* contadores */
  var counters = function () {
    d.querySelectorAll("[data-count]").forEach(function (el) {
      var to = parseInt(el.getAttribute("data-count"), 10); if (isNaN(to)) return;
      var from = to > 1000 ? to - 40 : 0, o = { v: from };
      el.textContent = from;
      ScrollTrigger.create({ trigger: el, start: "top 90%", once: true, onEnter: function () { gsap.to(o, { v: to, duration: 2.2, ease: "power3.out", onUpdate: function () { el.textContent = Math.round(o.v); } }); } });
    });
  };

  /* marquee que acelera com a rolagem */
  var marquee = function () {
    d.querySelectorAll("[data-marquee] .mq-track").forEach(function (tr) {
      var x = 0, dir = -1, speed = .6, half = function () { return tr.scrollWidth / 2; };
      ScrollTrigger.create({ trigger: tr, start: "top bottom", end: "bottom top", onUpdate: function (s) { dir = s.direction === 1 ? -1 : 1; speed = .6 + Math.min(Math.abs(s.getVelocity()) / 300, 8); } });
      gsap.ticker.add(function () { x += dir * speed; speed += (.6 - speed) * .05; var h = half(); if (x <= -h) x += h; if (x > 0) x -= h; tr.style.transform = "translate3d(" + x + "px,0,0)"; });
    });
  };

  /* galeria horizontal fixa */
  var hgal = function () {
    var sec = d.querySelector("[data-hgal]"); if (!sec) return;
    var track = sec.querySelector("[data-hgal-track]"), bar = sec.querySelector("[data-hgal-bar]"), pin = sec.querySelector(".hgal-pin");
    var mm = gsap.matchMedia();
    mm.add("(min-width: 1101px)", function () {
      var dist = function () { return Math.max(0, track.scrollWidth - (w.innerWidth - track.getBoundingClientRect().left) + 40); };
      var tw = gsap.to(track, { x: function () { return -dist(); }, ease: "none", scrollTrigger: { trigger: sec, pin: pin, start: "top top", end: function () { return "+=" + dist(); }, scrub: 1, invalidateOnRefresh: true, onUpdate: function (s) { if (bar) bar.style.transform = "scaleX(" + s.progress + ")"; } } });
      track.querySelectorAll(".g-in").forEach(function (g) {
        gsap.fromTo(g, { xPercent: -6 }, { xPercent: 6, ease: "none", scrollTrigger: { trigger: g.parentElement, containerAnimation: tw, start: "left right", end: "right left", scrub: true } });
      });
      return function () { gsap.set(track, { clearProps: "transform" }); };
    });
  };

  /* rodapé: logo gigante entra */
  var footer = function () {
    return;
    gsap.fromTo(g, { yPercent: 60, opacity: 0 }, { yPercent: 0, opacity: .92, ease: "none", scrollTrigger: { trigger: ".site-footer", start: "top 90%", end: "bottom bottom", scrub: true } });
  };

  /* botões magnéticos + cursor */
  var pointer = function () {
    if (!fine) return;
    d.querySelectorAll(".btn, .ln-arrow, .tq-btn, .wa-float").forEach(function (b) {
      var xTo = gsap.quickTo(b, "x", { duration: .6, ease: "power3.out" }), yTo = gsap.quickTo(b, "y", { duration: .6, ease: "power3.out" });
      b.addEventListener("mousemove", function (e) { var r = b.getBoundingClientRect(); xTo((e.clientX - r.left - r.width / 2) * .25); yTo((e.clientY - r.top - r.height / 2) * .35); });
      b.addEventListener("mouseleave", function () { xTo(0); yTo(0); });
    });
    var c = d.createElement("div"); c.className = "cursor"; c.innerHTML = "<span></span>"; d.body.appendChild(c);
    var lab = c.querySelector("span"), cx = gsap.quickTo(c, "x", { duration: .35, ease: "power3.out" }), cy = gsap.quickTo(c, "y", { duration: .35, ease: "power3.out" });
    w.addEventListener("mousemove", function (e) { cx(e.clientX); cy(e.clientY); c.classList.add("on"); }, { passive: true });
    d.addEventListener("mouseleave", function () { c.classList.remove("on"); });
    d.addEventListener("mouseover", function (e) {
      var t = e.target.closest && e.target.closest("[data-cursor], a, button, summary, input, select, textarea");
      c.classList.remove("big", "link");
      if (!t) return;
      if (t.hasAttribute("data-cursor")) { lab.textContent = t.getAttribute("data-cursor"); c.classList.add("big"); }
      else if (!/INPUT|SELECT|TEXTAREA/.test(t.tagName)) c.classList.add("link");
    });
  };

  /* transição entre páginas */
  var transitions = function () {
    var cur = d.createElement("div"); cur.className = "curtain"; d.body.appendChild(cur);
    d.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a[href]"); if (!a) return;
      var href = a.getAttribute("href") || "";
      if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || a.target === "_blank" || a.hasAttribute("download")) return;
      if (href.charAt(0) === "#" || /^(mailto:|tel:)/.test(href) || a.origin !== w.location.origin) return;
      if (a.pathname === w.location.pathname && a.hash) return;
      e.preventDefault();
      gsap.fromTo(cur, { yPercent: 100 }, { yPercent: 0, duration: .7, ease: "expo.inOut", onComplete: function () { w.location.href = a.href; } });
    });
    w.addEventListener("pageshow", function (e) { if (e.persisted) gsap.set(cur, { yPercent: 100 }); });
  };

  /* loader (uma vez por sessão) */
  var loader = function (done) {
    if (!d.querySelector("[data-hero]") || store.get("as_seen", true)) { done(0); return; }
    store.set("as_seen", "1", true);
    var el = d.createElement("div"); el.className = "loader"; el.setAttribute("aria-hidden", "true");
    el.innerHTML = '<div class="loader-in"><img class="loader-mark" src="' + I.mark + '" alt=""><img class="loader-word" src="' + I.logo + '" alt=""><span class="loader-bar"><i></i></span></div>';
    d.body.appendChild(el); if (lenis) lenis.stop();
    var tl = gsap.timeline({ onComplete: function () { el.remove(); if (lenis) lenis.start(); } });
    tl.fromTo(el.querySelector(".loader-mark"), { rotate: -90, scale: .4, opacity: 0 }, { rotate: 0, scale: 1, opacity: 1, duration: 1.1, ease: EASE })
      .to(el.querySelector(".loader-word"), { clipPath: "inset(0 0% 0 0)", duration: 1.1, ease: "expo.inOut" }, .25)
      .to(el.querySelector(".loader-bar i"), { scaleX: 1, duration: 1.1, ease: "expo.inOut" }, .25)
      .to(el.querySelector(".loader-in"), { opacity: 0, y: -30, duration: .6, ease: "power3.in" }, 1.45)
      .to(el, { yPercent: -100, duration: 1.1, ease: "expo.inOut" }, 1.7)
      .add(function () { done(0); }, 1.85);
  };

  /* entrada de páginas internas */
  var innerEntrance = function () {
    var cur = d.createElement("div"); cur.className = "curtain"; cur.style.transform = "translateY(0)"; d.body.appendChild(cur);
    gsap.to(cur, { yPercent: -100, duration: 1, ease: "expo.inOut", delay: .05, onComplete: function () { cur.remove(); } });
  };

  var init = function () {
    splitAll(); fadeAll(); mediaAll(); wordsAnim(); counters(); marquee(); hgal(); footer(); pointer(); transitions();
    var isHome = !!d.querySelector("[data-hero]");
    if (isHome) loader(function (delay) { heroAnim(delay); html.classList.remove("js"); });
    else { innerEntrance(); html.classList.remove("js"); }
    w.addEventListener("load", function () { ScrollTrigger.refresh(); });
  };
  if (d.fonts && d.fonts.ready) d.fonts.ready.then(init); else init();
})();
