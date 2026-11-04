/* Optional, local-only Scarp learning progress. No analytics, accounts or cookies.
   Pure helpers are exported for Node's built-in test runner. */
(function (scope) {
  "use strict";

  const KEY = "scarp-by-example:completed:v1";
  const SCHEMA = 1;
  const MAX_BACKUP_BYTES = 64 * 1024;
  const ID_RE = /^[0-9]{2}-[a-z0-9-]+\/[0-9]{2}-[a-z0-9-]+$/;
  const URL_RE = /^lessons\/[0-9]{2}-[a-z0-9-]+\/[0-9]{2}-[a-z0-9-]+\/index\.html$/;

  function validLesson(item) {
    if (!item || typeof item !== "object" || Array.isArray(item)) return false;
    if (typeof item.id !== "string" || !ID_RE.test(item.id)) return false;
    if (typeof item.url !== "string" || !URL_RE.test(item.url)) return false;
    return item.url === "lessons/" + item.id + "/index.html";
  }

  function normalizeManifest(input) {
    if (!Array.isArray(input) || input.length === 0) return [];
    const seen = new Set();
    return input.filter(item => {
      if (!validLesson(item) || seen.has(item.id)) return false;
      seen.add(item.id);
      return true;
    }).map(item => ({ id: item.id, url: item.url }));
  }

  function readCompleted(raw, manifest) {
    if (typeof raw !== "string") return new Set();
    try {
      const payload = JSON.parse(raw);
      if (!payload || payload.version !== SCHEMA || !Array.isArray(payload.completed)) {
        return new Set();
      }
      const allowed = new Set(manifest.map(item => item.id));
      return new Set(payload.completed.filter(id => typeof id === "string" && allowed.has(id)));
    } catch (_) {
      return new Set();
    }
  }

  function serializeCompleted(completed, manifest) {
    return JSON.stringify({
      version: SCHEMA,
      completed: manifest.filter(item => completed.has(item.id)).map(item => item.id)
    });
  }

  // Reject malformed backups instead of silently treating them as empty progress.
  // Unknown lesson IDs from a different course revision are safely ignored.
  function parseProgressBackup(raw, manifest) {
    if (typeof raw !== "string" || raw.length > MAX_BACKUP_BYTES) return null;
    try {
      const payload = JSON.parse(raw);
      if (!payload || payload.version !== SCHEMA ||
          !Array.isArray(payload.completed) || payload.completed.length > 2000 ||
          !payload.completed.every(id => typeof id === "string" && ID_RE.test(id))) {
        return null;
      }
      const allowed = new Set(manifest.map(item => item.id));
      return new Set(payload.completed.filter(id => allowed.has(id)));
    } catch (_) {
      return null;
    }
  }

  function firstIncomplete(manifest, completed, chapter = null) {
    return manifest.find(item =>
      (!chapter || item.id.startsWith(chapter + "/")) && !completed.has(item.id)
    ) || null;
  }

  function completedCount(manifest, completed, chapter = null) {
    return manifest.filter(item =>
      (!chapter || item.id.startsWith(chapter + "/")) && completed.has(item.id)
    ).length;
  }

  const helpers = Object.freeze({
    KEY, validLesson, normalizeManifest, readCompleted, serializeCompleted,
    parseProgressBackup, firstIncomplete, completedCount
  });
  if (typeof module !== "undefined" && module.exports) module.exports = helpers;
  if (typeof document === "undefined") return;

  const panel = document.querySelector("[data-progress-index]");
  if (!panel) return;
  const indexPath = panel.dataset.progressIndex;
  const rootPath = panel.dataset.progressRoot || "index.html";
  const currentId = panel.dataset.progressCurrent || null;
  const chapterId = panel.dataset.progressScope || null;

  function fullPath(item) {
    const prefix = rootPath.replace(/index\.html$/, "");
    return prefix + item.url.replace(/index\.html$/, "");
  }

  async function init() {
    // Static site remains fully usable if index fetch or storage fails.
    const response = await fetch(indexPath, { credentials: "same-origin" });
    if (!response.ok) throw new Error("Lesson index unavailable");
    const original = await response.json();
    const manifest = normalizeManifest(original);
    if (!manifest.length || manifest.length !== original.length) throw new Error("Lesson index is invalid");
    if (currentId && !manifest.some(item => item.id === currentId)) {
      throw new Error("Current lesson is missing from index");
    }

    let storage;
    try {
      storage = window.localStorage;
      const probe = "scarp-progress-storage-check";
      storage.setItem(probe, "1");
      storage.removeItem(probe);
    } catch (_) {
      throw new Error("Browser storage is unavailable");
    }

    let completed = readCompleted(storage.getItem(KEY), manifest);
    const toggle = panel.querySelector("[data-progress-toggle]");
    const clear = panel.querySelector("[data-progress-clear]");
    const exportButton = panel.querySelector("[data-progress-export]");
    const importButton = panel.querySelector("[data-progress-import]");
    const fileInput = panel.querySelector("[data-progress-file]");
    const feedback = panel.querySelector("[data-progress-message]");
    const say = message => { if (feedback) feedback.textContent = message; };

    function render() {
      const total = manifest.filter(item => !chapterId || item.id.startsWith(chapterId + "/")).length;
      const count = completedCount(manifest, completed, chapterId);
      for (const element of document.querySelectorAll("[data-progress-count]")) {
        const target = element.getAttribute("data-progress-count");
        const targetChapter = target && target !== "all" ? target : null;
        const matching = manifest.filter(item => !targetChapter || item.id.startsWith(targetChapter + "/"));
        element.textContent = completedCount(manifest, completed, targetChapter) +
          " of " + matching.length + " completed";
      }
      for (const bar of document.querySelectorAll("progress[data-progress-bar]")) {
        bar.max = total;
        bar.value = count;
      }
      for (const mark of document.querySelectorAll("[data-progress-complete]")) {
        mark.hidden = !completed.has(mark.dataset.progressComplete);
      }
      const currentDone = currentId && completed.has(currentId);
      if (toggle) {
        toggle.textContent = currentDone ? "Mark as incomplete" : "Mark lesson complete";
        toggle.setAttribute("aria-pressed", String(Boolean(currentDone)));
      }
      for (const status of document.querySelectorAll("[data-progress-status]")) {
        if (currentId) {
          status.textContent = currentDone
            ? "This lesson is marked complete on this device."
            : "Mark this lesson complete when you are ready.";
        } else {
          status.textContent = "Saved only in this browser. No account or tracking.";
        }
      }
      for (const link of document.querySelectorAll("[data-progress-resume]")) {
        const next = firstIncomplete(manifest, completed, chapterId);
        if (next) {
          link.href = fullPath(next);
          link.textContent = count ? "Continue learning →" : "Start learning →";
          link.hidden = false;
        } else {
          link.hidden = true;
        }
      }
      for (const badge of document.querySelectorAll("[data-progress-chapter]")) {
        const chapter = badge.dataset.progressChapter;
        const howMany = manifest.filter(item => item.id.startsWith(chapter + "/")).length;
        const done = completedCount(manifest, completed, chapter);
        badge.textContent = done + " / " + howMany + " complete";
      }
      // A chapter path reflects only explicitly saved lesson completions.
      // Quiz and coding-lab results are deliberately not claimed or tracked.
      for (const step of document.querySelectorAll("[data-path-lesson-status]")) {
        const chapter = step.dataset.pathLessonStatus;
        const howMany = manifest.filter(item => item.id.startsWith(chapter + "/")).length;
        const done = completedCount(manifest, completed, chapter);
        step.textContent = done + " / " + howMany + " lessons marked complete on this device.";
      }
    }

    function persist(next) {
      try {
        storage.setItem(KEY, serializeCompleted(next, manifest));
        completed = next;
        render();
        return true;
      } catch (_) {
        say("Progress could not be saved in this browser.");
        return false;
      }
    }

    if (toggle) toggle.addEventListener("click", () => {
      const next = new Set(completed);
      if (next.has(currentId)) next.delete(currentId);
      else next.add(currentId);
      persist(next);
    });

    if (clear) clear.addEventListener("click", () => {
      if (!window.confirm("Clear all saved Scarp lesson progress on this device?")) return;
      try {
        storage.removeItem(KEY);
        completed = new Set();
        render();
      } catch (_) {
        say("Progress could not be cleared.");
      }
    });

    // Backups never leave the browser. They contain lesson IDs only, no account data.
    if (exportButton) {
      if (typeof Blob === "undefined" || !window.URL ||
          typeof window.URL.createObjectURL !== "function") {
        exportButton.hidden = true;
      } else {
        exportButton.addEventListener("click", () => {
          const readable = JSON.stringify(JSON.parse(serializeCompleted(completed, manifest)), null, 2) + "\n";
          let url;
          try {
            url = window.URL.createObjectURL(new Blob([readable], {type: "application/json"}));
            const link = document.createElement("a");
            link.href = url;
            link.download = "scarp-by-example-progress.json";
            link.click();
            say("Backup downloaded to this device. Keep the JSON file somewhere safe.");
          } catch (_) {
            say("Could not export the backup in this browser.");
          } finally {
            if (url) window.setTimeout(() => window.URL.revokeObjectURL(url), 1000);
          }
        });
      }
    }

    if (importButton) {
      if (!fileInput || typeof fileInput.click !== "function") {
        importButton.hidden = true;
      } else {
        importButton.addEventListener("click", () => fileInput.click());
        fileInput.addEventListener("change", async () => {
          const file = fileInput.files && fileInput.files[0];
          fileInput.value = "";
          if (!file) return;
          if (file.size > MAX_BACKUP_BYTES) {
            say("Backup is too large. Choose a Scarp progress JSON file under 64 KB.");
            return;
          }
          try {
            const imported = parseProgressBackup(await file.text(), manifest);
            if (imported === null) {
              say("Invalid or unsupported backup. Your current progress was not changed.");
              return;
            }
            const next = new Set([...completed, ...imported]);
            const added = next.size - completed.size;
            if (added === 0) {
              say("Backup read successfully. No new completed lessons to restore.");
              return;
            }
            if (persist(next)) {
              say("Restored " + added + " completed lesson" + (added === 1 ? "" : "s") +
                  ". Existing progress was preserved.");
            }
          } catch (_) {
            say("Could not read that backup. Your current progress was not changed.");
          }
        });
      }
    }

    window.addEventListener("storage", event => {
      if (event.key !== KEY && event.key !== null) return;
      try {
        completed = readCompleted(storage.getItem(KEY), manifest);
        render();
      } catch (_) {
        // The current page's content stays available even if storage is blocked.
      }
    });

    // Never show buttons that cannot save or a progress bar without valid data.
    panel.hidden = false;
    render();
  }

  init().catch(() => {
    // Progressive enhancement: do not obstruct lesson reading when offline or
    // when browser storage is unavailable.
  });
})(typeof globalThis !== "undefined" ? globalThis : this);
