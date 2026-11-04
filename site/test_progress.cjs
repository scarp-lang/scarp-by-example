"use strict";
// No dependencies: node --test site/test_progress.cjs
const test = require("node:test");
const assert = require("node:assert/strict");
const progress = require("./progress.js");

const source = [
  { id: "01-basics/01-hello", url: "lessons/01-basics/01-hello/index.html" },
  { id: "01-basics/02-bindings", url: "lessons/01-basics/02-bindings/index.html" },
  { id: "02-control-flow/01-decisions", url: "lessons/02-control-flow/01-decisions/index.html" }
];

test("accepts stable source-derived lesson IDs and rejects unsafe paths", () => {
  assert.deepEqual(progress.normalizeManifest(source), source);
  assert.equal(progress.validLesson({id: "../evil", url: "https://evil.example"}), false);
  assert.equal(progress.validLesson({id: "01-basics/01-hello", url: "https://evil.example/"}), false);
  assert.equal(progress.validLesson({id: "01-basics/01-hello", url: "lessons/01-basics/02-bindings/index.html"}), false);
  assert.equal(progress.validLesson({id: "01-basics/01-hello", url: "lessons/01-basics/01-hello/index.html?x=1"}), false);
  assert.deepEqual(progress.normalizeManifest([...source, source[0]]), source);
});

test("round-trips completed lessons in deterministic course order", () => {
  const set = new Set([source[2].id, source[0].id, "not-an-example"]);
  const json = progress.serializeCompleted(set, source);
  assert.deepEqual(JSON.parse(json), {
    version: 1,
    completed: [source[0].id, source[2].id]
  });
  assert.deepEqual(progress.readCompleted(json, source), new Set([source[0].id, source[2].id]));
});

test("invalid JSON and future incompatible schema safely start empty", () => {
  assert.deepEqual(progress.readCompleted("{", source), new Set());
  assert.deepEqual(progress.readCompleted(null, source), new Set());
  assert.deepEqual(progress.readCompleted("[]", source), new Set());
  assert.deepEqual(progress.readCompleted(JSON.stringify({version: 2, completed: [source[0].id]}), source), new Set());
  assert.deepEqual(progress.readCompleted(JSON.stringify({version: 1, completed: "hello"}), source), new Set());
});

test("drops stale and malformed IDs without affecting newer lessons", () => {
  const raw = JSON.stringify({version: 1, completed: [
    source[0].id, source[0].id, "../../admin", "__proto__", 42, "09-old/01-gone"
  ]});
  assert.deepEqual(progress.readCompleted(raw, source), new Set([source[0].id]));
});

test("resuming skips only lessons explicitly marked complete", () => {
  assert.equal(progress.firstIncomplete(source, new Set()).id, source[0].id);
  assert.equal(progress.firstIncomplete(source, new Set([source[0].id])).id, source[1].id);
  assert.equal(progress.firstIncomplete(source, new Set([source[0].id]), "02-control-flow").id, source[2].id);
  assert.equal(progress.firstIncomplete(source, new Set(source.map(x => x.id))), null);
});

test("chapter and course counts derive from the actual manifest", () => {
  const done = new Set([source[0].id, source[2].id]);
  assert.equal(progress.completedCount(source, done), 2);
  assert.equal(progress.completedCount(source, done, "01-basics"), 1);
  assert.equal(progress.completedCount(source, done, "02-control-flow"), 1);
  assert.equal(progress.completedCount(source, done, "03-functions"), 0);
});

test("backups restore only known lesson IDs and preserve version compatibility", () => {
  const backup = progress.serializeCompleted(new Set([source[0].id, source[2].id]), source);
  assert.deepEqual(progress.parseProgressBackup(backup, source),
    new Set([source[0].id, source[2].id]));
  const fromOlderCourse = JSON.stringify({
    version: 1, completed: [source[1].id, "09-old/01-retired"]
  });
  assert.deepEqual(progress.parseProgressBackup(fromOlderCourse, source),
    new Set([source[1].id]));
});

test("corrupt and oversized imports fail closed, never becoming empty restores", () => {
  assert.equal(progress.parseProgressBackup("not json", source), null);
  assert.equal(progress.parseProgressBackup(JSON.stringify({version: 2, completed: []}), source), null);
  assert.equal(progress.parseProgressBackup(JSON.stringify({version: 1, completed: "bad"}), source), null);
  assert.equal(progress.parseProgressBackup(JSON.stringify({version: 1, completed: [null]}), source), null);
  assert.equal(progress.parseProgressBackup(JSON.stringify({version: 1, completed: ["../evil"]}), source), null);
  assert.equal(progress.parseProgressBackup(JSON.stringify({version: 1, completed: Array(2001).fill(source[0].id)}), source), null);
  assert.equal(progress.parseProgressBackup(" ".repeat(65537), source), null);
  assert.deepEqual(progress.parseProgressBackup(JSON.stringify({version: 1, completed: []}), source), new Set());
});
