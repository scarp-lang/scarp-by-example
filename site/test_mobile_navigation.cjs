"use strict";

// Accessible mobile navigation behavior without third-party DOM dependencies.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

function boot() {
  const links = Array.from({ length: 6 }, () => ({
    handlers: {},
    addEventListener(type, fn) { this.handlers[type] = fn; }
  }));
  const summary = { focused: false, focus() { this.focused = true; } };
  const menu = {
    open: false, handlers: {}, links,
    addEventListener(type, fn) { this.handlers[type] = fn; },
    querySelector(selector) {
      return selector === "summary" ? summary : null;
    },
    querySelectorAll(selector) {
      return selector === "a" ? links : [];
    }
  };
  const root = { classList: { add() {} }, dataset: { theme: "dark" } };
  const document = {
    documentElement: root,
    querySelector(selector) {
      return selector === "[data-mobile-nav]" ? menu : null;
    },
    querySelectorAll() { return []; }
  };
  const window = { localStorage: { getItem() { return null; } } };
  const script = fs.readFileSync(path.join(__dirname, "search.js"), "utf8");
  vm.runInNewContext(script, {document, window}, {timeout: 2000});
  return {menu, links, summary};
}

test("mobile navigation closes on Escape and restores trigger focus", () => {
  const ui = boot();
  ui.menu.open = true;
  let prevented = false;
  ui.menu.handlers.keydown({
    key: "Escape", preventDefault() { prevented = true; }
  });
  assert.equal(ui.menu.open, false);
  assert.equal(ui.summary.focused, true);
  assert.equal(prevented, true);
});

test("other keys and a closed menu are not intercepted", () => {
  const ui = boot();
  ui.menu.open = true;
  let prevented = false;
  ui.menu.handlers.keydown({
    key: "Enter", preventDefault() { prevented = true; }
  });
  assert.equal(ui.menu.open, true);
  ui.menu.open = false;
  ui.menu.handlers.keydown({
    key: "Escape", preventDefault() { prevented = true; }
  });
  assert.equal(ui.summary.focused, false);
  assert.equal(prevented, false);
});

test("menu links close the disclosure after activation", () => {
  const ui = boot();
  assert.equal(ui.links.length, 6);
  for (const link of ui.links) {
    assert.equal(typeof link.handlers.click, "function");
    ui.menu.open = true;
    link.handlers.click();
    assert.equal(ui.menu.open, false);
  }
});
