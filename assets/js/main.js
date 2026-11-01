(() => {
  "use strict";
  const doc = document.documentElement;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  const finePointer = window.matchMedia("(pointer: fine)");
  const fmt = new Intl.NumberFormat("sv-SE");
  const kr = (n) => `${fmt.format(n)} kr`;

  /* ---------- Header state ---------- */
  const header = document.querySelector(".site-header");
  const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 8);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* Replay the wordmark stitch on hover is CSS; mobile menu: */
  const menuBtn = document.querySelector(".menu-toggle");
  const mobileNav = document.getElementById("mobilmeny");
  menuBtn?.addEventListener("click", () => {
    const open = menuBtn.getAttribute("aria-expanded") === "true";
    menuBtn.setAttribute("aria-expanded", String(!open));
    menuBtn.setAttribute("aria-label", open ? "Öppna meny" : "Stäng meny");
    mobileNav.classList.toggle("is-open", !open);
  });
  mobileNav?.addEventListener("click", (e) => {
    if (e.target.closest("a")) { mobileNav.classList.remove("is-open"); menuBtn.setAttribute("aria-expanded", "false"); menuBtn.setAttribute("aria-label", "Öppna meny"); }
  });

  /* ---------- Hero video ---------- */
  const video = document.querySelector(".hero__frame video");
  const toggle = document.querySelector(".media-toggle");
  if (video && toggle) {
    const label = toggle.querySelector("[data-label]");
    const iconPause = toggle.querySelector("[data-icon=pause]");
    const iconPlay = toggle.querySelector("[data-icon=play]");
    const setUi = (playing) => {
      label.textContent = playing ? "Pausa" : "Spela";
      toggle.setAttribute("aria-label", playing ? "Pausa filmen" : "Spela filmen");
      iconPause.toggleAttribute("hidden", !playing);
      iconPlay.toggleAttribute("hidden", playing);
    };
    const play = () => {
      if (video.preload === "none") video.preload = "auto";
      const p = video.play();
      if (p) p.then(() => { video.classList.add("is-playing"); setUi(true); }).catch(() => setUi(false));
    };
    const pause = () => { video.pause(); setUi(false); };
    toggle.hidden = false;
    toggle.addEventListener("click", () => (video.paused ? play() : pause()));
    const start = () => { if (!reduce.matches) play(); else setUi(false); };
    if (document.readyState === "complete") start(); else window.addEventListener("load", start, { once: true });
    reduce.addEventListener("change", (e) => (e.matches ? pause() : play()));
    // Save resources when the hero is off screen
    new IntersectionObserver(([entry]) => {
      if (reduce.matches || !video.classList.contains("is-playing")) return;
      if (entry.isIntersecting && video.dataset.userPaused !== "1") video.play().catch(() => {});
      else if (!entry.isIntersecting) video.pause();
    }).observe(video);
    toggle.addEventListener("click", () => { video.dataset.userPaused = video.paused ? "1" : "0"; });
  }

  /* ---------- Scroll reveals ---------- */
  const revealables = document.querySelectorAll("[data-reveal], .stitch-divider");
  if ("IntersectionObserver" in window && !reduce.matches) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    revealables.forEach((el) => io.observe(el));
  } else {
    revealables.forEach((el) => el.classList.add("is-in"));
  }

  /* ---------- Magnetic buttons ---------- */
  if (finePointer.matches && !reduce.matches) {
    document.querySelectorAll("[data-magnetic]").forEach((el) => {
      const strength = 0.22;
      el.addEventListener("pointermove", (e) => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - (r.left + r.width / 2)) * strength;
        const y = (e.clientY - (r.top + r.height / 2)) * strength;
        el.style.translate = `${x.toFixed(1)}px ${y.toFixed(1)}px`;
      });
      el.addEventListener("pointerleave", () => { el.style.translate = "0 0"; });
    });
  }

  /* ---------- Cart (localStorage, demo only) ---------- */
  const KEY = "strumpverket-cart-v1";
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch { return []; } };
  let cart = load();
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch { /* storage blocked, keep in memory */ } };

  const dialog = document.getElementById("varukorg");
  const itemsEl = dialog.querySelector(".cart__items");
  const sumEl = dialog.querySelector("[data-sum]");
  const notice = dialog.querySelector(".cart__notice");
  const checkout = dialog.querySelector("[data-checkout]");
  const countEls = document.querySelectorAll(".cart-count");
  const cartBtn = document.querySelector("[data-open-cart]");
  const toast = document.querySelector(".toast");
  const live = document.getElementById("live");

  const totalQty = () => cart.reduce((n, i) => n + i.qty, 0);
  const totalSum = () => cart.reduce((n, i) => n + i.qty * i.price, 0);

  const render = () => {
    const q = totalQty();
    countEls.forEach((el) => { el.textContent = q; el.dataset.count = q; });
    cartBtn.setAttribute("aria-label", `Varukorg, ${q} ${q === 1 ? "vara" : "varor"}`);
    sumEl.textContent = kr(totalSum());
    checkout.disabled = q === 0;
    if (!cart.length) {
      itemsEl.innerHTML = '<p class="cart__empty">Varukorgen är tom. Välj en modell och en storlek för att börja.</p>';
      return;
    }
    itemsEl.innerHTML = "";
    cart.forEach((item, idx) => {
      const row = document.createElement("div");
      row.className = "cart-item";
      row.innerHTML = `
        <img src="${item.img}" alt="" width="72" height="96" loading="lazy" decoding="async">
        <div>
          <p class="cart-item__name"></p>
          <p class="label">Storlek ${item.size}</p>
          <div class="qty" role="group" aria-label="Antal">
            <button type="button" data-act="dec" aria-label="Minska antal">&minus;</button>
            <output aria-live="polite">${item.qty}</output>
            <button type="button" data-act="inc" aria-label="Öka antal">+</button>
          </div>
          <div><button type="button" class="remove u-link" data-act="rm">Ta bort</button></div>
        </div>
        <p class="cart-item__price">${kr(item.price * item.qty)}</p>`;
      row.querySelector(".cart-item__name").textContent = item.name;
      row.addEventListener("click", (e) => {
        const act = e.target.closest("[data-act]")?.dataset.act;
        if (!act) return;
        if (act === "inc") item.qty += 1;
        if (act === "dec") item.qty -= 1;
        if (act === "rm" || item.qty < 1) cart.splice(idx, 1);
        save(); render();
        if (act === "rm") dialog.querySelector(".cart__head button").focus();
      });
      itemsEl.append(row);
    });
  };

  const bump = () => countEls.forEach((el) => { el.classList.remove("is-bumping"); void el.offsetWidth; el.classList.add("is-bumping"); });
  let toastTimer;
  const showToast = (msg) => {
    toast.textContent = msg;
    toast.classList.add("is-on");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("is-on"), 2400);
    live.textContent = msg;
  };

  document.querySelectorAll("form[data-product]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const d = form.dataset;
      const fd = new FormData(form);
      const size = fd.get("storlek") || "41-45";
      const interval = fd.get("intervall");
      const name = interval ? `${d.name}, ${interval}` : d.name;
      const id = `${d.product}|${size}|${interval || ""}`;
      const existing = cart.find((i) => i.id === id);
      if (existing) existing.qty += 1;
      else cart.push({ id, name, size, price: Number(d.price), img: d.img, qty: 1 });
      save(); render(); bump();
      const btn = form.querySelector(".add-btn");
      btn.classList.add("is-added");
      setTimeout(() => btn.classList.remove("is-added"), 1700);
      showToast(`${name} (${size}) lades i varukorgen`);
    });
  });

  const openCart = () => {
    notice.hidden = true;
    dialog.showModal();
  };
  cartBtn.addEventListener("click", openCart);
  dialog.querySelector(".cart__head button").addEventListener("click", () => dialog.close());
  // Light dismiss fallback for browsers without closedby
  if (!("closedBy" in HTMLDialogElement.prototype)) {
    dialog.addEventListener("click", (e) => {
      if (e.target !== dialog) return;
      const r = dialog.getBoundingClientRect();
      const inside = r.top <= e.clientY && e.clientY <= r.bottom && r.left <= e.clientX && e.clientX <= r.right;
      if (!inside) dialog.close();
    });
  }
  checkout.addEventListener("click", () => { notice.hidden = false; notice.focus(); });
  window.addEventListener("storage", (e) => { if (e.key === KEY) { cart = load(); render(); } });
  render();

  /* ---------- Newsletter (demo, sends nothing) ---------- */
  const news = document.querySelector(".news__form");
  news?.addEventListener("submit", (e) => {
    e.preventDefault();
    const input = news.querySelector("input[type=email]");
    const status = news.querySelector(".news__status");
    if (!input.checkValidity()) { status.textContent = "Skriv en giltig e-postadress."; input.focus(); return; }
    status.textContent = "Tack. Det här är en demo, så ingen adress har sparats eller skickats.";
    news.reset();
  });

  /* Footer year */
  document.querySelectorAll("[data-year]").forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
