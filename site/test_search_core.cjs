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
