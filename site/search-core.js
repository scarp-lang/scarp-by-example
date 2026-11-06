/* Offline source-aware lesson search; no external services or dependencies. */
(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.ScarpLessonSearch = api;
})(typeof globalThis === "object" ? globalThis : this, function () {
  "use strict";
  function normalized(value) {
    return typeof value === "string" ? value.normalize("NFKC").toLocaleLowerCase() : "";
  }
  // Show context from the exact indexed .srp source, not a generated example.
  // The first line with the most matching query terms wins; ties use line order.
  function sourcePreview(source, terms) {
    if (typeof source !== "string") return null;
    let selected = null;
    source.split(/\r?\n/).forEach((raw, index) => {
      const line = raw.trim();
      if (!line) return;
      const normalizedLine = normalized(line);
      const hits = terms.filter(term => normalizedLine.includes(term)).length;
      if (!selected || hits > selected.hits) {
        selected = { line: index + 1, text: line, hits };
      }
    });
    if (!selected) return null;
    // Preserve the original source characters, including quotes and markup.
    // Limit very long lines to a compact window around the first source hit.
    const characters = Array.from(selected.text);
    const limit = 140;
    if (characters.length > limit) {
      const normalizedLine = normalized(selected.text);
      const offsets = terms.map(term => normalizedLine.indexOf(term))
        .filter(offset => offset >= 0);
      const offset = offsets.length ? Math.min(...offsets) : 0;
      const start = Math.min(Math.max(0, offset - 35), characters.length - limit);
      selected.text = (start ? "…" : "") +
        characters.slice(start, start + limit).join("") +
        (start + limit < characters.length ? "…" : "");
    }
    return { line: selected.line, text: selected.text, matched: selected.hits > 0 };
  }

  function searchLessons(items, query, section = "") {
    if (!Array.isArray(items)) return [];
    const terms = normalized(query).trim().split(/\s+/u).filter(Boolean);
    if (!terms.length && !section) return [];
    const found = [];
    items.forEach((item, index) => {
      if (!item || typeof item.id !== "string") return;
      if (section && !item.id.startsWith(section + "/")) return;
      const fields = [item.title, item.description, item.chapter,
        item.hindi_title, item.hindi_summary, item.source].map(normalized);
      const weights = [110, 70, 35, 105, 65, 10];
      let score = 0;
      let metadataMatch = false;
      for (const term of terms) {
        let best = 0;
        fields.forEach((field, i) => {
          if (!field.includes(term)) return;
          if (i < 5) metadataMatch = true;
          best = Math.max(best, weights[i] + (i === 0 && field.startsWith(term) ? 20 : 0));
        });
        if (!best) return; // All query terms must occur, possibly in different fields.
        score += best;
      }
      found.push({
        item, index, score, sourceOnly: terms.length > 0 && !metadataMatch,
        sourcePreview: sourcePreview(item.source, terms)
      });
    });
    found.sort((a, b) => b.score - a.score || a.index - b.index);
    return found.map(({ item, sourceOnly, sourcePreview }) =>
      ({ item, sourceOnly, sourcePreview }));
  }
  return { searchLessons };
});
