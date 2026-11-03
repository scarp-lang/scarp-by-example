"use strict";

// Behavior tests for the browser UI, with a small fake DOM and no third-party packages.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { KEY } = require("./progress.js");

const lessons = [
  {id:"01-basics/01-hello",url:"lessons/01-basics/01-hello/index.html"},
  {id:"01-basics/02-bindings",url:"lessons/01-basics/02-bindings/index.html"},
  {id:"02-control-flow/01-decisions",url:"lessons/02-control-flow/01-decisions/index.html"}
];

function element(attrs = {}) {
  const listeners = {};
  return {
    hidden: true, textContent: "", dataset: {}, href: "", value: 0, max: 0,
    attributes: { ...attrs }, listeners,
    setAttribute(key, value) { this.attributes[key] = value; },
    getAttribute(key) { return this.attributes[key] ?? null; },
    addEventListener(key, fn) { listeners[key] = fn; }
  };
}

async function boot({ blocked = false, chapter = null } = {}) {
  const entries = new Map();
  const writeKeys = [];
  const storage = {
    getItem(key) { return entries.get(key) ?? null; },
    setItem(key, value) {
      if (blocked) throw new Error("storage disabled");
      entries.set(key, value);
      writeKeys.push(key);
    },
    removeItem(key) {
      if (blocked) throw new Error("storage disabled");
      entries.delete(key);
    }
  };
  const toggle = element();
  const clear = element();
  const count = element({"data-progress-count": chapter || "all"});
  const bar = element();
  const badge = element();
  badge.dataset.progressComplete = lessons[0].id;
  const resume = element();
  const status = element();
  const error = element();
  const panel = element();
  panel.dataset = {
    progressIndex: "search-index.json",
    progressRoot: "index.html",
    progressCurrent: lessons[0].id,
    progressScope: chapter
  };
  panel.querySelector = selector => ({
    "[data-progress-toggle]": toggle,
    "[data-progress-clear]": clear,
    "[data-progress-message]": error
  })[selector] || null;
  const selectors = {
    "[data-progress-count]": [count],
    "progress[data-progress-bar]": [bar],
    "[data-progress-complete]": [badge],
    "[data-progress-status]": [status],
    "[data-progress-resume]": [resume],
    "[data-progress-chapter]": []
  };
  const document = {
    querySelector(selector) {
      if (selector === "[data-progress-index]") return panel;
      return null;
    },
    querySelectorAll(selector) { return selectors[selector] || []; }
  };
  const events = {};
  const window = {
    localStorage: storage,
    confirm() { return true; },
    addEventListener(key, fn) { events[key] = fn; }
  };
  const context = { document, window, fetch: async () => ({
    ok: true, json: async () => lessons
  }) };
  const script = fs.readFileSync(path.join(__dirname, "progress.js"), "utf8");
  vm.runInNewContext(script, context, { timeout: 2000 });
  await new Promise(resolve => setImmediate(resolve));
  return { panel, toggle, clear, count, bar, badge, resume, status, error,
    entries, storage, writeKeys, events };
}

test("does not save completion until explicit user click", async () => {
  const ui = await boot();
  assert.equal(ui.panel.hidden, false);
  assert.equal(ui.count.textContent, "0 of 3 completed");
  assert.equal(ui.bar.max, 3);
  assert.equal(ui.bar.value, 0);
  assert.equal(ui.toggle.textContent, "Mark lesson complete");
  assert.equal(ui.badge.hidden, true);
  assert.equal(ui.entries.has(KEY), false);
  assert.equal(ui.resume.href, "lessons/01-basics/01-hello/");
  ui.toggle.listeners.click();
  assert.equal(ui.entries.has(KEY), true);
  assert.equal(ui.count.textContent, "1 of 3 completed");
  assert.equal(ui.bar.value, 1);
  assert.equal(ui.badge.hidden, false);
  assert.equal(ui.toggle.attributes["aria-pressed"], "true");
  assert.equal(ui.resume.href, "lessons/01-basics/02-bindings/");
  ui.toggle.listeners.click();
  assert.equal(ui.count.textContent, "0 of 3 completed");
  assert.equal(ui.toggle.attributes["aria-pressed"], "false");
});

test("clearing requires browser confirmation and removes completion key", async () => {
  const ui = await boot();
  ui.toggle.listeners.click();
  assert.equal(ui.entries.has(KEY), true);
  ui.clear.listeners.click();
  assert.equal(ui.entries.has(KEY), false);
  assert.equal(ui.count.textContent, "0 of 3 completed");
  assert.equal(ui.bar.value, 0);
});

test("storage-disabled browsers never show non-functional controls", async () => {
  const ui = await boot({ blocked: true });
  assert.equal(ui.panel.hidden, true);
  assert.equal(ui.entries.has(KEY), false);
});

test("chapter scope counts only its own lessons", async () => {
  const ui = await boot({ chapter: "01-basics" });
  assert.equal(ui.count.textContent, "0 of 2 completed");
  assert.equal(ui.bar.max, 2);
  ui.toggle.listeners.click();
  assert.equal(ui.count.textContent, "1 of 2 completed");
  assert.equal(ui.bar.value, 1);
});
