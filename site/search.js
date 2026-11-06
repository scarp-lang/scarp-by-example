// Progressive enhancement: source pages work without JS or external services.
(() => {
  "use strict";
  const root = document.documentElement;
  root.classList.add("js-ready");
  const toggle = document.querySelector("#theme-toggle");
  const mobileMenu = document.querySelector("[data-mobile-nav]");
  if (mobileMenu) {
    // Escape closes the menu and returns keyboard focus to its trigger.
    // Native <details> remains fully usable when JavaScript is disabled.
    mobileMenu.addEventListener("keydown", event => {
      if (event.key !== "Escape" || !mobileMenu.open) return;
      mobileMenu.open = false;
      mobileMenu.querySelector("summary")?.focus();
      event.preventDefault();
    });
    for (const link of mobileMenu.querySelectorAll("a")) {
      link.addEventListener("click", () => { mobileMenu.open = false; });
    }
  }

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

  // Language switch is optional. With JavaScript disabled, both notes remain
  // visible in document order for keyboard, screen-reader and print access.
  const english = document.querySelector("#en-notes");
  const hindi = document.querySelector("#hi-notes");
  const languageButtons = [...document.querySelectorAll("[data-note-switch]")];

  if (english && hindi && languageButtons.length === 2) {
    function showLanguage(lang) {
      const showHindi = lang === "hi";
      english.hidden = showHindi;
      hindi.hidden = !showHindi;
      for (const span of document.querySelectorAll("[data-checkpoint-lang]")) {
        span.hidden = span.dataset.checkpointLang !== lang;
      }
      languageButtons.forEach(button => {
        const selected = button.dataset.noteSwitch === lang;
        button.setAttribute("aria-pressed", String(selected));
      });
    }

    showLanguage(window.location.hash === "#hi-notes" ? "hi" : "en");
    languageButtons.forEach(button => {
      button.addEventListener("click", () => showLanguage(button.dataset.noteSwitch));
    });
    window.addEventListener("hashchange", () => {
      if (window.location.hash === "#hi-notes") showLanguage("hi");
      if (window.location.hash === "#en-notes") showLanguage("en");
    });
  }

  const search = document.querySelector("#lesson-search");
  const status = document.querySelector("#search-status");
  const results = document.querySelector("#search-results");
  const chapterFilter = document.querySelector("#lesson-chapter");
  if (!search || !status || !results || !chapterFilter || !window.ScarpLessonSearch) return;
  const searchHint = "Browse chapters below or search all " + search.dataset.lessonCount + " lessons.";
  status.textContent = searchHint;
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
    const query = search.value.trim(), section = chapterFilter.value;
    results.replaceChildren();
    if (!query && !section) {
      status.textContent = searchHint;
      return;
    }
    status.textContent = "Searching lessons…";
    try {
      const lessons = await loadIndex();
      // Discard responses from searches that have already changed.
      if (search.value.trim() !== query || chapterFilter.value !== section) return;
      const matches = window.ScarpLessonSearch.searchLessons(lessons, query, section);
      status.textContent = matches.length
        ? String(matches.length) + " matching lesson" + (matches.length === 1 ? "." : "s.")
        : "No matching lessons. Try another keyword or chapter.";
      for (const { item, sourceOnly } of matches.slice(0, 30)) {
        // Use only site-generated paths. Never inject fetched text as HTML.
        if (typeof item.url !== "string" ||
            !/^lessons\/[a-z0-9-]+\/[a-z0-9-]+\/index\.html$/.test(item.url)) continue;
        const li = document.createElement("li"), link = document.createElement("a");
        link.href = item.url;
        const name = document.createElement("strong");
        name.textContent = item.title;
        const chapter = document.createElement("small");
        chapter.textContent = item.chapter + " · " + item.hindi_title;
        link.append(name, chapter);
        if (sourceOnly) {
          const hint = document.createElement("small");
          hint.textContent = "Matched Scarp source · स्रोत कोड में मिला";
          link.append(hint);
        }
        if (item.has_checkpoint === true) {
          const quiz = document.createElement("small");
          quiz.textContent = "Quick check available · अभ्यास प्रश्न";
          link.append(quiz);
        }
        li.append(link);
        results.append(li);
      }
      if (matches.length > 30) status.textContent += " Showing the first 30.";
    } catch (error) {
      status.textContent = error.message || "Search is unavailable.";
    }
  }

  search.addEventListener("input", update);
  chapterFilter.addEventListener("change", update);
})();
