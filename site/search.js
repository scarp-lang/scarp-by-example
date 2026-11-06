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
  const shareLink = document.querySelector("#share-search-link");
  if (!search || !status || !results || !chapterFilter || !window.ScarpLessonSearch) return;
  const searchHint = "Browse chapters below or search all " + search.dataset.lessonCount + " lessons.";
  status.textContent = searchHint;
  let cached = null;
  let pending = null;
  let revision = 0;

  // Share links are explicit rather than silently adding each keystroke to the
  // browser URL. Anyone opening the link sees the chosen text and chapter.
  function updateShareLink() {
    if (!shareLink) return;
    const query = search.value.trim(), section = chapterFilter.value;
    shareLink.hidden = !query && !section;
    if (shareLink.hidden) {
      shareLink.removeAttribute("href");
      return;
    }
    const params = new URLSearchParams();
    if (query) params.set("q", query);
    if (section) params.set("chapter", section);
    shareLink.href = "index.html?" + params.toString() + "#search-area";
  }

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
    const request = ++revision;
    const query = search.value.trim(), section = chapterFilter.value;
    updateShareLink();
    results.replaceChildren();
    if (!query && !section) {
      status.textContent = searchHint;
      return;
    }
    status.textContent = "Searching lessons…";
    try {
      const lessons = await loadIndex();
      // Discard responses from searches that have already changed.
      if (request !== revision || search.value.trim() !== query ||
          chapterFilter.value !== section) return;
      // Only count links that can actually be rendered as site-local lessons.
      const matches = window.ScarpLessonSearch.searchLessons(lessons, query, section)
        .filter(({ item }) => typeof item.url === "string" &&
          /^lessons\/[a-z0-9-]+\/[a-z0-9-]+\/index\.html$/.test(item.url));
      status.textContent = matches.length
        ? String(matches.length) + " matching lesson" + (matches.length === 1 ? "." : "s.")
        : "No matching lessons. Try another keyword or chapter.";
      for (const { item, sourceOnly, sourcePreview } of matches.slice(0, 30)) {
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
        if (sourcePreview) {
          // Render real compiler-verified source as plain text, never HTML.
          const preview = document.createElement("span");
          preview.className = "search-code-preview";
          const label = document.createElement("small");
          label.textContent = (sourcePreview.matched
            ? "Scarp source match" : "Scarp source preview") +
            " · line " + sourcePreview.line;
          const code = document.createElement("code");
          code.textContent = sourcePreview.text;
          preview.append(label, code);
          link.append(preview);
        }
        li.append(link);
        results.append(li);
      }
      if (matches.length > 30) status.textContent += " Showing the first 30.";
    } catch (error) {
      if (request !== revision) return;
      status.textContent = error.message || "Search is unavailable.";
    }
  }

  search.addEventListener("input", update);
  chapterFilter.addEventListener("change", update);

  // Escape clears the entire search while keeping focus in the input.
  search.addEventListener("keydown", event => {
    if (event.key !== "Escape" || event.isComposing ||
        (!search.value && !chapterFilter.value)) return;
    event.preventDefault();
    search.value = "";
    chapterFilter.value = "";
    void update();
  });

  // "/" focuses the search only when not typing in another field.
  document.addEventListener?.("keydown", event => {
    if (event.key !== "/" || event.altKey || event.ctrlKey ||
        event.metaKey || event.defaultPrevented || event.isComposing) return;
    const focused = document.activeElement;
    if (focused && (focused.isContentEditable ||
        ["INPUT", "TEXTAREA", "SELECT"].includes(focused.tagName))) return;
    event.preventDefault();
    search.focus();
  });

  // Only recognized chapter options are accepted from externally shared URLs.
  // A malformed query never changes source files, local progress, or the URL.
  function restoreSharedSearch() {
    const params = new URLSearchParams(window.location?.search || "");
    search.value = (params.get("q") || "").slice(0, 160);
    const section = params.get("chapter") || "";
    const valid = Array.from(chapterFilter.options || [])
      .some(option => option.value === section);
    chapterFilter.value = valid ? section : "";
    if (search.value || chapterFilter.value) {
      void update();
    } else {
      ++revision;
      results.replaceChildren();
      status.textContent = searchHint;
      updateShareLink();
    }
  }

  restoreSharedSearch();
  window.addEventListener?.("popstate", restoreSharedSearch);
})();
