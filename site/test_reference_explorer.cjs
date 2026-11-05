"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const script = fs.readFileSync(path.join(__dirname, "reference-explorer.js"), "utf8");

function item(key, extra = {}) {
  const tags = new Set();
  const attributes = {};
  return {
    dataset: { ...extra },
    classList: {
      toggle(cls, active) { active ? tags.add(cls) : tags.delete(cls); },
      contains(cls) { return tags.has(cls); }
    },
    setAttribute(name, value) { attributes[name] = value; },
    getAttribute(name) { return attributes[name]; },
    closest(selector) { return selector === "a[data-ref-symbol]" ? this : null; }
  };
}

function boot(hash = "") {
  const links = [
    item("outer-use", { refSymbol: "base-outer" }),
    item("outer-definition", { refSymbol: "base-outer" }),
    item("inner-use", { refSymbol: "base-inner" }),
    item("inner-definition", { refSymbol: "base-inner" }),
  ];
  const cards = [
    item("outer-card", { refCard: "base-outer", refSummary: "Outer base and one reference" }),
    item("inner-card", { refCard: "base-inner", refSummary: "Inner base and one reference" })
  ];
  const status = { textContent: "Choose an annotation" };
  const listeners = {};
  const events = {};
  const explorer = {
    querySelectorAll(selector) {
      if (selector === "a[data-ref-symbol]") return links;
      if (selector === "[data-ref-card]") return cards;
      return [];
    },
    querySelector(selector) {
      if (selector === "[data-ref-status]") return status;
      return null;
    },
    contains(node) { return links.includes(node); },
    addEventListener(name, callback) { listeners[name] = callback; }
  };
  const context = {
    document: { querySelector(selector) {
      return selector === "[data-reference-explorer]" ? explorer : null;
    }},
    window: {
      location: { hash },
      addEventListener(name, callback) { events[name] = callback; }
    },
  };
  vm.runInNewContext(script, context, { timeout: 1000 });
  return { links, cards, status, listeners, events, context };
}

test("clicking either binding highlights only its declarations and references", () => {
  const ui = boot();
  let prevented = false;
  ui.listeners.click({
    target: ui.links[0],
    preventDefault() { prevented = true; },
  });
  assert.equal(prevented, true);
  assert.equal(ui.links[0].classList.contains("is-active"), true);
  assert.equal(ui.links[1].classList.contains("is-active"), true);
  assert.equal(ui.links[2].classList.contains("is-active"), false);
  assert.equal(ui.cards[0].classList.contains("is-active"), true);
  assert.equal(ui.cards[1].classList.contains("is-active"), false);
  assert.match(ui.status.textContent, /Outer base/);

  ui.listeners.click({ target: ui.links[2], preventDefault() {} });
  assert.equal(ui.links[0].classList.contains("is-active"), false);
  assert.equal(ui.links[2].classList.contains("is-active"), true);
  assert.equal(ui.cards[1].classList.contains("is-active"), true);
  assert.match(ui.status.textContent, /Inner base/);
});

test("deep links highlight without saving state", () => {
  const ui = boot("#ref-card-base-inner");
  assert.equal(ui.cards[1].classList.contains("is-active"), true);
  ui.context.window.location.hash = "#ref-card-base-outer";
  ui.events.hashchange();
  assert.equal(ui.cards[0].classList.contains("is-active"), true);
  assert.equal(ui.cards[1].classList.contains("is-active"), false);
});

test("unrelated clicks are left alone and static anchors remain usable", () => {
  const ui = boot();
  let prevented = false;
  ui.listeners.click({
    target: { closest() { return null; } },
    preventDefault() { prevented = true; },
  });
  assert.equal(prevented, false);
  assert.equal(ui.status.textContent, "Choose an annotation");
  assert.equal(script.includes("localStorage"), false);
  assert.equal(script.includes("fetch("), false);
});
