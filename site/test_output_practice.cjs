"use strict";
// Behavior tests for the actual browser script; no third-party DOM dependencies.
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

function element() {
  return {
    hidden: false, textContent: "", value: "", attributes: {}, listeners: {},
    focused: false,
    setAttribute(key, value) { this.attributes[key] = value; },
    addEventListener(key, fn) { this.listeners[key] = fn; },
    focus() { this.focused = true; }
  };
}

function boot({ output = "hello\n", missing = null } = {}) {
  const practice = element();
  practice.hidden = true;
  const verified = element();
  const expected = element();
  expected.textContent = output;
  verified.querySelector = selector => selector === "code" ? expected : null;
  const start = element(), workspace = element(), prediction = element();
  const check = element(), toggle = element(), reset = element(), feedback = element();
  workspace.hidden = true;
  const elements = {
    "[data-output-start]": start,
    "[data-output-workspace]": workspace,
    "[data-output-prediction]": prediction,
    "[data-output-check]": check,
    "[data-output-toggle]": toggle,
    "[data-output-reset]": reset,
    "[data-output-feedback]": feedback
  };
  practice.querySelector = selector => selector === missing ? null : elements[selector] || null;
  const document = {
    querySelector(selector) {
      if (selector === "[data-output-practice]") return practice;
      if (selector === "[data-verified-output]") return verified;
      return null;
    }
  };
  const script = fs.readFileSync(path.join(__dirname, "output-practice.js"), "utf8");
  vm.runInNewContext(script, {document}, {timeout: 2000});
  return {practice, verified, expected, start, workspace, prediction,
    check, toggle, reset, feedback};
}

test("normal source output is available before opting in; no-JS markup stays readable", () => {
  const ui = boot();
  assert.equal(ui.practice.hidden, false);
  assert.equal(ui.verified.hidden, false);
  assert.equal(ui.workspace.hidden, true);
  assert.equal(ui.expected.textContent, "hello\n");
});

test("start prediction hides the fixture but enables keyboard-focused entry", () => {
  const ui = boot();
  ui.start.listeners.click();
  assert.equal(ui.start.hidden, true);
  assert.equal(ui.workspace.hidden, false);
  assert.equal(ui.verified.hidden, true);
  assert.equal(ui.prediction.focused, true);
  assert.equal(ui.toggle.textContent, "Reveal verified output");
  assert.equal(ui.toggle.attributes["aria-expanded"], "false");
});

test("an empty prediction asks for input instead of claiming success", () => {
  const ui = boot();
  ui.start.listeners.click();
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /Enter your predicted output first/);
  assert.equal(ui.verified.hidden, true);
});

test("correct text matches displayed source-backed stdout, not simulated execution", () => {
  const ui = boot({output: "Hello, Scarp!\n"});
  ui.start.listeners.click();
  ui.prediction.value = "Hello, Scarp!";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /prediction matches/);
  assert.equal(ui.verified.hidden, true, "comparison never reveals the solution");
  ui.prediction.value = "Hello, Scarp!\r\n";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /prediction matches/);
});

test("wrong text preserves the private draft and allows a new attempt", () => {
  const ui = boot({output: "42\n"});
  ui.start.listeners.click();
  ui.prediction.value = "41";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /does not match/);
  assert.equal(ui.prediction.value, "41");
  assert.equal(ui.verified.hidden, true);
  ui.prediction.value = "42";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /prediction matches/);
});

test("reveal and hide operate only on visible fixture, with accurate ARIA state", () => {
  const ui = boot();
  ui.start.listeners.click();
  ui.toggle.listeners.click();
  assert.equal(ui.verified.hidden, false);
  assert.equal(ui.toggle.attributes["aria-expanded"], "true");
  assert.equal(ui.toggle.textContent, "Hide verified output");
  ui.toggle.listeners.click();
  assert.equal(ui.verified.hidden, true);
  assert.equal(ui.toggle.attributes["aria-expanded"], "false");
});

test("reset restores original output and clears prediction without persistence", () => {
  const ui = boot();
  ui.start.listeners.click();
  ui.prediction.value = "private draft";
  ui.check.listeners.click();
  ui.reset.listeners.click();
  assert.equal(ui.verified.hidden, false);
  assert.equal(ui.start.hidden, false);
  assert.equal(ui.workspace.hidden, true);
  assert.equal(ui.prediction.value, "");
  assert.equal(ui.feedback.textContent, "");
  assert.equal(ui.expected.textContent, "hello\n", "fixture is never rewritten");
});

test("Unicode and visible carriage-return representations compare as text", () => {
  const ui = boot({output: "नमस्ते\n\u03bb\\rअंत\n"});
  ui.start.listeners.click();
  ui.prediction.value = "नमस्ते\n\u03bb\\rअंत";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /prediction matches/);
});

test("malformed or missing control keeps the original output visible", () => {
  const ui = boot({missing: "[data-output-check]"});
  assert.equal(ui.practice.hidden, true);
  assert.equal(ui.verified.hidden, false);
  assert.equal(ui.start.listeners.click, undefined);
});


test("multi-line mismatches report first differing line without spoiling stdout", () => {
  const output = "begin\nsecret answer here\nfinish\n";
  const ui = boot({output});
  ui.start.listeners.click();
  ui.prediction.value = "begin\nwrong guess here\nfinish";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /does not match/);
  assert.match(ui.feedback.textContent, /First difference at line 2/);
  assert.match(ui.feedback.textContent, /पहली अलग पंक्ति: 2/);
  assert.equal(ui.feedback.textContent.includes("secret answer here"), false);
  assert.equal(ui.verified.hidden, true);
});

test("missing or extra lines report counts and the correct first difference", () => {
  const ui = boot({output: "one\ntwo\nthree\n"});
  ui.start.listeners.click();
  ui.prediction.value = "one\ntwo";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /First difference at line 3/);
  assert.match(ui.feedback.textContent, /You entered 2 lines; the verified output has 3/);
  assert.equal(ui.verified.hidden, true);

  ui.prediction.value = "one\ntwo\nthree\nextra";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /First difference at line 4/);
  assert.match(ui.feedback.textContent, /You entered 4 lines; the verified output has 3/);
  assert.equal(ui.verified.hidden, true);
});

test("spacing-only differences receive a precise whitespace hint", () => {
  const ui = boot({output: "value: 3\n"});
  ui.start.listeners.click();
  ui.prediction.value = " value: 3 ";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /First difference at line 1/);
  assert.match(ui.feedback.textContent, /Check leading or trailing spaces/);
  assert.equal(ui.verified.hidden, true);
});

test("capitalization differences are distinguished from missing characters", () => {
  const ui = boot({output: "Hello World\n"});
  ui.start.listeners.click();
  ui.prediction.value = "hello world";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /Check capitalization/);
  ui.prediction.value = "Hello, World";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /Check the text, spaces, or punctuation/);
  assert.equal(ui.feedback.textContent.includes("Hello World"), false);
});

test("the hint respects line-ending normalization and Unicode text", () => {
  const ui = boot({output: "नमस्ते\nदूसरी पंक्ति\n"});
  ui.start.listeners.click();
  ui.prediction.value = "नमस्ते\r\nदूसरी पंक्ति\r\n";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /prediction matches/);
  ui.prediction.value = "नमस्ते\r\nअन्य पंक्ति";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /First difference at line 2/);
  assert.equal(ui.feedback.textContent.includes("दूसरी पंक्ति"), false);
});

test("reset clears mismatch hints as well as prediction", () => {
  const ui = boot({output: "first\nsecond\n"});
  ui.start.listeners.click();
  ui.prediction.value = "first\nwrong";
  ui.check.listeners.click();
  assert.match(ui.feedback.textContent, /First difference at line 2/);
  ui.reset.listeners.click();
  assert.equal(ui.feedback.textContent, "");
  assert.equal(ui.prediction.value, "");
  assert.equal(ui.verified.hidden, false);
});
