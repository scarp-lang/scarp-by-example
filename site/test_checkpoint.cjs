"use strict";
// Dependency-free browser behavior tests for the progressive lesson checkpoint.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

function element() {
  return {
    hidden: true,
    textContent: "",
    dataset: {},
    listeners: {},
    addEventListener(type, handler) { this.listeners[type] = handler; }
  };
}

function boot({ expected = "1" } = {}) {
  const selected = element();
  selected.value = "1";
  const form = element();
  form.querySelector = selector => selector ===
    'input[name="checkpoint-choice"]:checked' ? selected : null;
  const interactive = element();
  const fallback = element();
  fallback.hidden = false;
  const feedback = element();
  const explanation = element();
  const card = element();
  card.dataset.checkpointAnswer = expected;
  const elements = {
    "[data-checkpoint-form]": form,
    "[data-checkpoint-interactive]": interactive,
    "[data-checkpoint-fallback]": fallback,
    "[data-checkpoint-feedback]": feedback,
    "[data-checkpoint-explanation]": explanation
  };
  card.querySelector = selector => elements[selector] || null;
  const document = { querySelectorAll: selector => selector === "[data-checkpoint]" ? [card] : [] };
  const script = fs.readFileSync(path.join(__dirname, "checkpoint.js"), "utf8");
  vm.runInNewContext(script, {document}, {timeout: 2000});
  return {card, form, selected, interactive, fallback, feedback, explanation};
}

test("enhances valid checkpoint while hiding no-JavaScript answer reveal", () => {
  const ui = boot();
  assert.equal(ui.interactive.hidden, false);
  assert.equal(ui.fallback.hidden, true);
  assert.ok(ui.form.listeners.submit);
  assert.ok(ui.form.listeners.reset);
});

test("correct answers provide immediate bilingual feedback and explanation", () => {
  const ui = boot();
  let prevented = false;
  ui.form.listeners.submit({preventDefault() { prevented = true; }});
  assert.equal(prevented, true);
  assert.match(ui.feedback.textContent, /Correct!/);
  assert.match(ui.feedback.textContent, /सही उत्तर/);
  assert.equal(ui.explanation.hidden, false);
});

test("wrong answers reveal source-backed explanation and support retry", () => {
  const ui = boot();
  ui.selected.value = "2";
  ui.form.listeners.submit({preventDefault() {}});
  assert.match(ui.feedback.textContent, /Not quite/);
  assert.equal(ui.explanation.hidden, false);
  ui.form.listeners.reset();
  assert.equal(ui.feedback.textContent, "");
  assert.equal(ui.explanation.hidden, true);
});

test("malformed answer metadata leaves the static fallback accessible", () => {
  const ui = boot({expected: "../bad"});
  assert.equal(ui.fallback.hidden, false);
  assert.equal(ui.interactive.hidden, true);
  assert.equal(ui.form.listeners.submit, undefined);
});

test("missing selection is announced without exposing the correct answer", () => {
  const ui = boot();
  ui.form.querySelector = () => null;
  ui.form.listeners.submit({preventDefault() {}});
  assert.match(ui.feedback.textContent, /Choose an answer first/);
  assert.equal(ui.explanation.hidden, true);
});
