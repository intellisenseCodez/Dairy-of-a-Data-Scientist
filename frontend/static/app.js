(function () {
  const $ = (s) => document.querySelector(s);

  /* mobile menu */
  const nav = $("#nav"), menu = $("#menu");
  menu.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    menu.setAttribute("aria-expanded", String(open));
    menu.textContent = open ? "✕" : "☰";
  });
  nav.addEventListener("click", (e) => {
    if (e.target.tagName === "A") {
      nav.classList.remove("open");
      menu.setAttribute("aria-expanded", "false");
      menu.textContent = "☰";
    }
  });

  /* theme toggle */
  $("#theme").addEventListener("click", () => {
    const r = document.documentElement;
    const dark = r.dataset.theme ? r.dataset.theme === "dark" : matchMedia("(prefers-color-scheme:dark)").matches;
    r.dataset.theme = dark ? "light" : "dark";
  });

  /* signup */
  const form = $("#signup");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const msg = $("#msg");
      try {
        const res = await fetch(form.action, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: $("#email").value }),
        });
        const data = await res.json();
        msg.textContent = data.message;
        if (data.ok) form.reset();
      } catch (err) {
        msg.textContent = "Something went wrong. Please try again.";
      }
    });
  }

  /* glossary: live search, level filter, related links, letter highlight */
  const list = $("#list");
  if (!list) return;
  const items = [...list.querySelectorAll("details.term")];
  const heads = [...list.querySelectorAll(".letter")];
  const chips = [...document.querySelectorAll(".chip")];
  const count = $("#count"), empty = $("#empty"), q = $("#q");
  let level = "All";

  function apply() {
    const needle = q.value.trim().toLowerCase();
    let shown = 0;
    const lettersShown = new Set();
    items.forEach((d) => {
      const ok = (level === "All" || d.dataset.level === level) && (!needle || d.dataset.text.includes(needle));
      d.hidden = !ok;
      if (ok) { shown++; lettersShown.add(d.dataset.letter); }
    });
    heads.forEach((h) => (h.hidden = !lettersShown.has(h.dataset.letter)));
    const total = count.dataset.total;
    count.textContent = shown + " of " + total + " terms";
    empty.hidden = shown > 0;
  }
  q.addEventListener("input", apply);
  chips.forEach((c) => c.addEventListener("click", () => {
    level = c.dataset.l;
    chips.forEach((x) => x.setAttribute("aria-pressed", String(x === c)));
    apply();
  }));

  list.addEventListener("click", (e) => {
    const a = e.target.closest("a.relink");
    if (!a) return;
    e.preventDefault();
    if (level !== "All" || q.value) {
      level = "All"; q.value = "";
      chips.forEach((x) => x.setAttribute("aria-pressed", String(x.dataset.l === "All")));
      apply();
    }
    const d = document.getElementById(a.getAttribute("href").slice(1));
    if (d) {
      d.open = true;
      d.scrollIntoView({ behavior: "smooth", block: "center" });
      d.querySelector("summary").focus({ preventScroll: true });
    }
  });

  const io = new IntersectionObserver((entries) => entries.forEach((en) => {
    if (en.isIntersecting) {
      document.querySelectorAll("#az a").forEach((a) =>
        a.classList.toggle("active", a.getAttribute("href") === "#" + en.target.id));
    }
  }), { rootMargin: "-30% 0px -60% 0px" });
  heads.forEach((h) => io.observe(h));
})();
