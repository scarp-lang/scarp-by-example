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
      found.push({ item, index, score, sourceOnly: terms.length > 0 && !metadataMatch });
    });
    found.sort((a, b) => b.score - a.score || a.index - b.index);
    return found.map(({ item, sourceOnly }) => ({ item, sourceOnly }));
  }
  return { searchLessons };
});
