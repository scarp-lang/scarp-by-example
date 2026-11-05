"use strict";

// Progressive enhancement only: without JavaScript, source links still jump
// to their checked, bilingual explanations. No storage, fetch or code execution.
(() => {
  const explorer = document.querySelector("[data-reference-explorer]");
  if (!explorer) return;

  const links = Array.from(explorer.querySelectorAll("a[data-ref-symbol]"));
  const cards = Array.from(explorer.querySelectorAll("[data-ref-card]"));
  const status = explorer.querySelector("[data-ref-status]");
  if (!links.length || !cards.length || !status) return;

  function select(key) {
    const card = cards.find(item => item.dataset.refCard === key);
    if (!card) return false;
    for (const link of links) {
      link.classList.toggle("is-active", link.dataset.refSymbol === key);
    }
    for (const item of cards) {
      item.classList.toggle("is-active", item === card);
    }
    status.textContent = card.dataset.refSummary;
    return true;
  }

  explorer.addEventListener("click", event => {
    const anchor = event.target.closest?.("a[data-ref-symbol]");
    if (!anchor || !explorer.contains(anchor)) return;
    if (select(anchor.dataset.refSymbol)) event.preventDefault();
  });

  // Deep links work with or without scripting. A user may open a saved
  // #ref-card-id URL; highlighting it does not depend on local storage.
  function highlightHash() {
    const prefix = "#ref-card-";
    if (window.location.hash.startsWith(prefix)) {
      select(decodeURIComponent(window.location.hash.slice(prefix.length)));
    }
  }
  highlightHash();
  window.addEventListener("hashchange", highlightHash);
})();
