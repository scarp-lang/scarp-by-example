"use strict";
const assert = require("node:assert/strict");
const { test } = require("node:test");
const { searchLessons } = require("./search-core.js");
const lessons = [
  { id: "01-basics/01-hello", title: "Hello", chapter: "Basics",
    description: "Write text", hindi_title: "पहला प्रोग्राम",
    hindi_summary: "स्क्रीन पर लिखना", source: 'print("Hello");' },
  { id: "03-functions/01-typed", title: "Typed Functions", chapter: "Functions",
    description: "Declare functions", hindi_title: "टाइप वाले फ़ंक्शन",
    hindi_summary: "मान लौटाना", source: "funcra add(a: integer) { return a; }" },
  { id: "04-collections/01-numeric", title: "Numerical vectors",
    chapter: "Collections", description: "Add numbers",
    hindi_title: "संख्यात्मक वेक्टर", hindi_summary: "गणना",
    source: "bind matrix = vector([1, 2]);" },
  { id: "04-collections/02-matrix", title: "Matrix calculations",
    chapter: "Collections", description: "Matrix expressions",
    hindi_title: "मैट्रिक्स", hindi_summary: "गणना",
    source: "bind data = vector([1, 2]);" },
];
test("empty query and chapter-only filters", () => {
  assert.deepEqual(searchLessons(lessons, ""), []);
  assert.equal(searchLessons(lessons, "", "04-collections").length, 2);
});
test("title ranks ahead of source-only matches; Hindi search works", () => {
  const hits = searchLessons(lessons, "matrix");
  assert.deepEqual(hits.map(x => x.item.id),
    ["04-collections/02-matrix", "04-collections/01-numeric"]);
  assert.equal(hits[1].sourceOnly, true);
  assert.equal(searchLessons(lessons, "फ़ंक्शन")[0].item.id, "03-functions/01-typed");
});
test("search source with multi-term AND matching", () => {
  assert.deepEqual(searchLessons(lessons, "funcra").map(x => x.item.id),
    ["03-functions/01-typed"]);
  assert.equal(searchLessons(lessons, "funcra")[0].sourceOnly, true);
  assert.deepEqual(searchLessons(lessons, "typed return").map(x => x.item.id),
    ["03-functions/01-typed"]);
  assert.deepEqual(searchLessons(lessons, "typed matrix"), []);
});
test("chapter filters and original-order tie breaking", () => {
  assert.deepEqual(searchLessons(lessons, "vector", "04-collections").map(x => x.item.id),
    ["04-collections/01-numeric", "04-collections/02-matrix"]);
  assert.deepEqual(searchLessons(lessons, "vector", "03-functions"), []);
  assert.deepEqual(searchLessons(lessons, "", "04-collections").map(x => x.item.id),
    ["04-collections/01-numeric", "04-collections/02-matrix"]);
});
test("case, malformed data and immutable inputs", () => {
  const before = JSON.stringify(lessons);
  assert.equal(searchLessons(lessons, "  MATRIX ").length, 2);
  assert.deepEqual(searchLessons(null, "x"), []);
  assert.deepEqual(searchLessons([null, {}, { id: "a", title: null }], "x"), []);
  assert.equal(JSON.stringify(lessons), before);
});


test("every result previews a real source line with line numbering", () => {
  const sourceHit = searchLessons(lessons, "funcra")[0].sourcePreview;
  assert.deepEqual(sourceHit,
    { line: 1, text: "funcra add(a: integer) { return a; }", matched: true });
  const metadataHit = searchLessons(lessons, "typed")[0].sourcePreview;
  assert.equal(metadataHit.matched, false);
  assert.equal(metadataHit.line, 1);
  assert.equal(metadataHit.text, lessons[1].source);
  const chapterHit = searchLessons(lessons, "", "04-collections")[0].sourcePreview;
  assert.equal(chapterHit.matched, false);
});

test("preview selects the earliest real line containing most query terms", () => {
  const item = {
    id: "01-basics/03-preview", title: "Preview", chapter: "Basics",
    source: "\n  bind first = vector([1]);\n\nprint(first);\n  bind second = vector([2]);\n"
  };
  const matches = searchLessons([item], "vector second");
  assert.equal(matches.length, 1);
  assert.deepEqual(matches[0].sourcePreview,
    { line: 5, text: "bind second = vector([2]);", matched: true });
  const tie = searchLessons([item], "vector");
  assert.equal(tie[0].sourcePreview.line, 2);
});

test("very long source lines show the relevant source token in bounded context", () => {
  const code = "bind data = " + "a".repeat(250) + " Needle " + "b".repeat(150);
  const item = { id: "04-collections/03-long", source: code };
  const preview = searchLessons([item], "needle")[0].sourcePreview;
  assert.equal(preview.matched, true);
  assert.ok(preview.text.includes("Needle"), "matching code remains visible");
  assert.ok(Array.from(preview.text).length <= 142);
  assert.ok(preview.text.startsWith("…"));
  assert.ok(preview.text.endsWith("…"));
});

test("source excerpts keep Unicode and markup as literal text", () => {
  const code = '  print("<img src=x onerror=alert(1)> नमस्ते");';
  const item = { id: "01-basics/04-unicode", source: code };
  const preview = searchLessons([item], "नमस्ते")[0].sourcePreview;
  assert.equal(preview.line, 1);
  assert.equal(preview.text, code.trim());
  assert.equal(preview.matched, true);
});

test("missing and blank code produce no preview without breaking search", () => {
  const noSource = { id: "01-basics/05-empty", title: "Hello" };
  assert.equal(searchLessons([noSource], "hello")[0].sourcePreview, null);
  const blank = { id: "01-basics/06-blank", title: "Hello", source: "  \n\r\n " };
  assert.equal(searchLessons([blank], "hello")[0].sourcePreview, null);
});
