// Progressive enhancement: source pages work without JS or external services.
(() => {
  "use strict";
  const root = document.documentElement;
  const toggle = document.querySelector("#theme-toggle");

  function setTheme(theme) {
    root.dataset.theme = theme;
    if (toggle) {
      const light = theme === "light";
      toggle.setAttribute("aria-label", light ? "Switch to dark theme" : "Switch to light theme");
      toggle.textContent = light ? "☾ Dark" : "☀ Light";
    }
  }

  try {
    const saved = window.localStorage.getItem("scarp-course-theme");
    if (saved === "light" || saved === "dark") setTheme(saved);
  } catch (_) {
    // Storage may be disabled; the default dark theme is still functional.
  }

  toggle?.addEventListener("click", () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    setTheme(next);
    try { window.localStorage.setItem("scarp-course-theme", next); } catch (_) {}
  });

  const copy = document.querySelector('[data-copy="scarp-code"]');
  copy?.addEventListener("click", async () => {
    const source = document.getElementById("scarp-code");
    if (!source) return;
    try {
      if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(source.textContent);
      copy.textContent = "Copied!";
    } catch (_) {
      copy.textContent = "Select code to copy";
    }
  });

  const search = document.querySelector("#lesson-search");
  const status = document.querySelector("#search-status");
  const results = document.querySelector("#search-results");
  if (!search || !status || !results) return;
  let cached = null;
  let pending = null;

  async function loadIndex() {
    if (cached) return cached;
    if (!pending) {
      pending = fetch(search.dataset.indexUrl)
        .then(response => {
          if (!response.ok) throw new Error("Search index unavailable");
          return response.json();
        })
        .then(items => {
          if (!Array.isArray(items)) throw new Error("Invalid lesson index");
          cached = items;
          return items;
        })
        .catch(() => {
          pending = null;
          throw new Error("Search is unavailable. Browse chapter links below.");
        });
    }
    return pending;
  }

  async function update() {
    const query = search.value.trim().toLocaleLowerCase();
    results.replaceChildren();
    if (!query) {
      status.textContent = "Browse chapters below or search all 50 lessons.";
      return;
    }
    status.textContent = "Searching lessons…";
    try {
      const lessons = await loadIndex();
      if (search.value.trim().toLocaleLowerCase() !== query) return;
      const matches = lessons.filter(item =>
        [item.title, item.description, item.chapter].some(value =>
          typeof value === "string" && value.toLocaleLowerCase().includes(query)
        )
      );
      status.textContent = matches.length
        ? String(matches.length) + " matching lesson" + (matches.length === 1 ? "." : "s.")
        : "No matching lessons. Try another keyword.";
      for (const item of matches.slice(0, 30)) {
        // Site-generated paths only; never use innerHTML with fetched text.
        if (typeof item.url !== "string" ||
            !/^lessons\/[a-z0-9-]+\/[a-z0-9-]+\/index\.html$/.test(item.url)) continue;
        const li = document.createElement("li");
        const link = document.createElement("a");
        link.href = item.url;
        const name = document.createElement("strong");
        name.textContent = item.title;
        const chapter = document.createElement("small");
        chapter.textContent = item.chapter;
        link.append(name, chapter);
        li.append(link);
        results.append(li);
      }
      if (matches.length > 30) status.textContent += " Showing the first 30.";
    } catch (error) {
      status.textContent = error.message || "Search is unavailable.";
    }
  }

  search.addEventListener("input", update);
})();
