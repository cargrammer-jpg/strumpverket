(() => {
  "use strict";
  const doc = document.documentElement;
  const root = doc.dataset.root || "";
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

  /* ---------- Hero video ----------
     The still is the <picture> behind the video. No poster attribute, so the
     browser does not fetch hero-1280.jpg on top of the AVIF. Sources stay off
     the element until playback starts: saveData, slow-2g/2g/3g and reduced
     motion therefore never download the file. A tap on the button still loads
     it, because the pause/play control has to work. */
  const video = document.querySelector(".hero__frame video");
  const toggle = document.querySelector(".media-toggle");
  if (video && toggle) {
    const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    const slowNet = () => {
      if (!conn) return false;
      if (conn.saveData) return true;
      const kind = conn.effectiveType;
      return kind === "slow-2g" || kind === "2g" || kind === "3g";
    };
    const label = toggle.querySelector("[data-label]");
    const iconPause = toggle.querySelector("[data-icon=pause]");
    const iconPlay = toggle.querySelector("[data-icon=play]");
    const setUi = (playing) => {
      label.textContent = playing ? "Pausa" : "Spela";
      toggle.setAttribute("aria-label", playing ? "Pausa filmen" : "Spela filmen");
      iconPause.toggleAttribute("hidden", !playing);
      iconPlay.toggleAttribute("hidden", playing);
    };
    const attachSources = () => {
      if (video.dataset.armed === "1") return;
      video.dataset.armed = "1";
      [["video/webm", video.dataset.srcWebm], ["video/mp4", video.dataset.srcMp4]].forEach(([type, url]) => {
        if (!url) return;
        const source = document.createElement("source");
        source.type = type;
        source.src = url;
        video.append(source);
      });
      video.preload = "auto";
      video.load();
    };
    const play = () => {
      attachSources();
      const pending = video.play();
      if (pending) pending.then(() => { video.classList.add("is-playing"); setUi(true); }).catch(() => setUi(false));
    };
    const pause = () => { video.pause(); setUi(false); };
    toggle.hidden = false;
    setUi(false);
    toggle.addEventListener("click", () => {
      if (video.paused) { video.dataset.userStarted = "1"; video.dataset.userPaused = "0"; play(); }
      else { video.dataset.userPaused = "1"; pause(); }
    });
    const start = () => { if (!reduce.matches && !slowNet()) play(); };
    if (document.readyState === "complete") start(); else window.addEventListener("load", start, { once: true });
    reduce.addEventListener("change", (e) => {
      if (e.matches) pause();
      else if (!slowNet() && video.dataset.userPaused !== "1") play();
    });
    if (conn && conn.addEventListener) {
      conn.addEventListener("change", () => {
        if (slowNet() && video.dataset.userStarted !== "1") pause();
      });
    }
    new IntersectionObserver(([entry]) => {
      if (video.dataset.armed !== "1" || video.dataset.userPaused === "1") return;
      if (reduce.matches && video.dataset.userStarted !== "1") return;
      if (entry.isIntersecting) video.play().catch(() => {});
      else video.pause();
    }).observe(video);
  }

  /* ---------- Scroll reveals ---------- */
  const revealables = document.querySelectorAll("[data-reveal], [data-mark], .stitch-divider");
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

  /* ---------- Cart (localStorage only, checkout not open yet) ----------
     Nothing is sent anywhere. v2: the range is now 5-pack, 10-pack and two
     subscriptions, so carts from the old four-model range are not reused. */
  const KEY = "strumpverket-cart-v2";
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch { return []; } };
  let cart = load();
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch { /* storage blocked, keep in memory */ } };

  const dialog = document.getElementById("varukorg");
  const itemsEl = dialog.querySelector(".cart__items");
  const sumEl = dialog.querySelector("[data-sum]");
  const subEl = dialog.querySelector("[data-subtotal]");
  const shipEl = dialog.querySelector("[data-ship-total]");
  const SHIPPING = Number(dialog.dataset.shipping || 0);
  const notice = dialog.querySelector(".cart__notice");
  const checkout = dialog.querySelector("[data-checkout]");
  const countEls = document.querySelectorAll(".cart-count");
  const cartBtn = document.querySelector("[data-open-cart]");
  const toast = document.querySelector(".toast");
  const live = document.getElementById("live");

  const totalQty = () => cart.reduce((n, i) => n + i.qty, 0);
  const subtotal = () => cart.reduce((n, i) => n + i.qty * i.price, 0);
  /* One shipping fee per order when it holds a one-off pack. Subscriptions include shipping. */
  const shipping = () => (cart.some((i) => i.ship) ? SHIPPING : 0);

  const render = () => {
    const q = totalQty();
    countEls.forEach((el) => { el.textContent = q; el.dataset.count = q; });
    cartBtn.setAttribute("aria-label", `Varukorg, ${q} ${q === 1 ? "vara" : "varor"}`);
    if (subEl) subEl.textContent = kr(subtotal());
    if (shipEl) shipEl.textContent = cart.some((i) => i.ship) ? kr(shipping()) : (cart.length ? "Ingår" : kr(0));
    sumEl.textContent = kr(subtotal() + shipping());
    checkout.disabled = q === 0;
    if (!cart.length) {
      itemsEl.innerHTML = '<p class="cart__empty">Varukorgen är tom. Välj 5-pack, 10-pack eller en prenumeration för att börja.</p>';
      return;
    }
    itemsEl.innerHTML = "";
    cart.forEach((item, idx) => {
      const row = document.createElement("div");
      row.className = "cart-item";
      const imgSrc = item.img.startsWith("assets/") ? root + item.img : item.img;
      row.innerHTML = `
        <img src="${imgSrc}" alt="" width="72" height="96" loading="lazy" decoding="async">
        <div>
          <p class="cart-item__name"></p>
          <p class="label">Storlek ${item.size}${item.ship ? "" : " · Frakt ingår"}</p>
          <div class="qty" role="group" aria-label="Antal">
            <button type="button" data-act="dec" aria-label="Minska antal">&minus;</button>
            <output aria-live="polite">${item.qty}</output>
            <button type="button" data-act="inc" aria-label="Öka antal">+</button>
          </div>
          <div><button type="button" class="remove u-link hit" data-act="rm">Ta bort</button></div>
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
      else cart.push({ id, name, size, price: Number(d.price), img: d.img, ship: d.ship === "1", qty: 1 });
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

  /* ---------- Newsletter (not live yet, sends nothing) ---------- */
  const news = document.querySelector(".news__form");
  news?.addEventListener("submit", (e) => {
    e.preventDefault();
    const input = news.querySelector("input[type=email]");
    const status = news.querySelector(".news__status");
    if (!input.checkValidity()) { status.textContent = "Skriv en giltig e-postadress."; input.focus(); return; }
    status.textContent = "Tack. Nyhetsbrevet är inte igång än, så ingen adress har sparats eller skickats.";
    news.reset();
  });


  /* ---------- Stars invite carousel ----------
     No real customers yet: cards are invitations, never fake reviews.
     When real reviews arrive, replace STAR_INVITES items with e.g.
       { kind: "review", text: "...", name: "...", rating: 5 }
     and extend renderStarsCard(). Do NOT emit schema.org Review or
     AggregateRating markup until reviews are genuine. */
  const STAR_INVITES = [
    { kind: "invite", text: "Här kan din recension stå.", cta: "Prenumerera", href: "#prenumeration" },
    { kind: "invite", text: "Fem stjärnor? Vi tror det.", cta: "Prenumerera", href: "#prenumeration" },
    { kind: "invite", text: "Ska du köpa igen? Vi håller tummarna.", cta: "Prenumerera", href: "#prenumeration" },
    { kind: "invite", text: "Bästa kvalitén, bedöm själv.", cta: "Prenumerera", href: "#prenumeration" },
    { kind: "invite", text: "Bli först med fem stjärnor.", cta: "Prenumerera", href: "#prenumeration" },
  ];

  const renderStarsCard = (item, index) => {
    const li = document.createElement("li");
    li.className = "stars-card";
    li.setAttribute("role", "listitem");
    li.style.setProperty("--tw", `${(index % 3) * 0.25}s`);

    const badge = document.createElement("p");
    badge.className = "stars-card__badge label";
    badge.textContent = item.kind === "review" ? "Recension" : "Inbjudan";
    li.appendChild(badge);

    const row = document.createElement("div");
    row.className = "stars-row";
    row.setAttribute("aria-hidden", "true");
    for (let i = 0; i < 5; i++) {
      const s = document.createElement("span");
      s.className = "star";
      s.style.setProperty("--i", String(i));
      row.appendChild(s);
    }
    li.appendChild(row);

    const text = document.createElement("p");
    text.className = "stars-card__text";
    text.textContent = item.text;
    li.appendChild(text);

    if (item.kind === "invite") {
      const a = document.createElement("a");
      a.className = "btn btn--ghost stars-card__cta";
      a.href = item.href || "#prenumeration";
      a.textContent = item.cta || "Prenumerera";
      li.appendChild(a);
    }
    return li;
  };

  const starsRoot = document.querySelector("[data-stars-carousel]");
  if (starsRoot) {
    const track = starsRoot.querySelector("[data-stars-track]");
    const prev = starsRoot.querySelector("[data-stars-prev]");
    const next = starsRoot.querySelector("[data-stars-next]");
    if (track) {
      track.replaceChildren(...STAR_INVITES.map(renderStarsCard));

      const cardStep = () => {
        const card = track.querySelector(".stars-card");
        if (!card) return 280;
        const styles = getComputedStyle(track);
        const gap = parseFloat(styles.columnGap || styles.gap || "16") || 16;
        return card.getBoundingClientRect().width + gap;
      };
      const syncNav = () => {
        if (!prev || !next) return;
        const max = track.scrollWidth - track.clientWidth - 2;
        prev.disabled = track.scrollLeft <= 2;
        next.disabled = track.scrollLeft >= max;
      };
      const scrollByDir = (dir) => {
        track.scrollBy({ left: dir * cardStep(), behavior: reduce.matches ? "auto" : "smooth" });
      };
      prev?.addEventListener("click", () => scrollByDir(-1));
      next?.addEventListener("click", () => scrollByDir(1));
      track.addEventListener("scroll", syncNav, { passive: true });
      track.addEventListener("keydown", (e) => {
        if (e.key === "ArrowRight") { e.preventDefault(); scrollByDir(1); }
        else if (e.key === "ArrowLeft") { e.preventDefault(); scrollByDir(-1); }
        else if (e.key === "Home") { e.preventDefault(); track.scrollTo({ left: 0, behavior: reduce.matches ? "auto" : "smooth" }); }
        else if (e.key === "End") { e.preventDefault(); track.scrollTo({ left: track.scrollWidth, behavior: reduce.matches ? "auto" : "smooth" }); }
      });
      window.addEventListener("resize", syncNav, { passive: true });
      syncNav();
    }
  }

  /* Footer year */
  document.querySelectorAll("[data-year]").forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
