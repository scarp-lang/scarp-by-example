"use strict";

// Dependency-free interaction tests for the real homepage search script.
// Fake DOM nodes deliberately reject innerHTML to detect unsafe rendering.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { searchLessons } = require("./search-core.js");

const lessons = [
  {
    id: "01-basics/01-hello", title: "Hello", chapter: "Scarp basics",
    description: "Display a greeting", hindi_title: "पहला प्रोग्राम",
    hindi_summary: "नमस्ते लिखें", source: 'print("hello");',
    url: "lessons/01-basics/01-hello/index.html", has_checkpoint: true
  },
  {
    id: "03-functions/01-typed-functions", title: "Typed functions", chapter: "Functions",
    description: "Named arguments", hindi_title: "टाइप वाले फ़ंक्शन",
    hindi_summary: "मान लौटाना", source: "funcra sum(a: integer) { return a; }",
    url: "lessons/03-functions/01-typed-functions/index.html", has_checkpoint: false
  },
  {
    id: "04-collections/01-vectors", title: "Vectors", chapter: "Collections",
    description: "Numbers and collections", hindi_title: "वेक्टर",
    hindi_summary: "संख्या संग्रह", source: "bind values = vector([1, 2]);",
    url: "lessons/04-collections/01-vectors/index.html", has_checkpoint: false
  }
];

function node(tag = "div") {
  const item = {
    tag, children: [], listeners: {}, dataset: {}, value: "", textContent: "",
    href: "", attributes: {}, classes: new Set(),
    append(...elements) { this.children.push(...elements); },
    replaceChildren(...elements) { this.children = [...elements]; },
    addEventListener(event, callback) { this.listeners[event] = callback; },
    setAttribute(name, value) { this.attributes[name] = value; }
  };
  item.classList = { add(name) { item.classes.add(name); } };
  Object.defineProperty(item, "innerHTML", {
    set() { throw new Error("Unsafe innerHTML assignment"); }
  });
  return item;
}

function boot({ data = lessons, fetchImpl = null } = {}) {
  const root = node("html");
  root.dataset.theme = "dark";
  const search = node("input");
  search.dataset = { indexUrl: "search-index.json", lessonCount: "51" };
  const chapter = node("select");
  const status = node("p");
  const results = node("ul");
  const lookup = {
    "#lesson-search": search, "#lesson-chapter": chapter,
    "#search-status": status, "#search-results": results
  };
  const document = {
    documentElement: root,
    querySelector(selector) { return lookup[selector] || null; },
    querySelectorAll() { return []; },
    getElementById() { return null; },
    createElement(tag) { return node(tag); }
  };
  const window = {
    ScarpLessonSearch: { searchLessons },
    localStorage: { getItem() { return null; } }
  };
  const requests = [];
  const fetch = url => {
    requests.push(url);
    return fetchImpl
      ? fetchImpl(url)
      : Promise.resolve({ ok: true, json: async () => data });
  };
  const script = fs.readFileSync(path.join(__dirname, "search.js"), "utf8");
  vm.runInNewContext(script, { document, window, fetch }, { timeout: 2000 });
  const displayedLinks = () => results.children.map(li => li.children[0]);
  return { search, chapter, status, results, requests, displayedLinks, root,
    type(value) {
      search.value = value;
      return search.listeners.input();
    },
    filter(value) {
      chapter.value = value;
      return chapter.listeners.change();
    }
  };
}

test("search waits for user input, loads once and exposes safe links", async () => {
  const ui = boot();
  assert.deepEqual(ui.requests, []);
  assert.match(ui.status.textContent, /Browse chapters/);
  assert.ok(ui.root.classes.has("js-ready"));

  await ui.type("funcra");
  assert.deepEqual(ui.requests, ["search-index.json"]);
  const [link] = ui.displayedLinks();
  assert.equal(link.href, lessons[1].url);
  assert.equal(link.children[0].textContent, "Typed functions");
  assert.match(link.children[2].textContent, /Matched Scarp source/);
  assert.equal(ui.status.textContent, "1 matching lesson.");

  await ui.type("फ़ंक्शन");
  assert.equal(ui.requests.length, 1, "same-origin index must be cached");
  assert.equal(ui.displayedLinks()[0].href, lessons[1].url);
  assert.equal(ui.displayedLinks()[0].children.length, 2,
    "Hindi metadata match is not labeled source-only");
});

test("chapter-only browsing, combining filters and clearing search", async () => {
  const ui = boot();
  await ui.filter("04-collections");
  assert.equal(ui.displayedLinks()[0].href, lessons[2].url);
  await ui.type("funcra");
  assert.equal(ui.results.children.length, 0);
  assert.match(ui.status.textContent, /No matching lessons/);

  await ui.filter("03-functions");
  assert.equal(ui.displayedLinks()[0].href, lessons[1].url);
  await ui.type("");
  assert.equal(ui.displayedLinks()[0].href, lessons[1].url);
  await ui.filter("");
  assert.equal(ui.results.children.length, 0);
  assert.match(ui.status.textContent, /Browse chapters/);
});

test("checkpoint marker is visible only for its associated lesson", async () => {
  const ui = boot();
  await ui.type("hello");
  const [link] = ui.displayedLinks();
  assert.equal(link.href, lessons[0].url);
  assert.ok(link.children.some(child => child.textContent.includes("Quick check available")));
  await ui.type("funcra");
  assert.ok(ui.displayedLinks()[0].children.every(
    child => !child.textContent.includes("Quick check available")));
});

test("injection-like source data renders as text; unsafe URLs cannot appear", async () => {
  const injected = {
    ...lessons[0], id: "01-basics/02-unsafe", title: '<img src=x onerror="alert(1)">',
    description: "Risk example", has_checkpoint: false,
    url: "lessons/01-basics/02-unsafe/index.html"
  };
  const unsafeLink = {
    ...lessons[2], id: "04-collections/02-bad", title: "Risk unsafe link",
    description: "Risk example", url: "javascript:alert(1)"
  };
  const ui = boot({ data: [injected, unsafeLink] });
  await ui.type("risk");
  assert.equal(ui.results.children.length, 1, "reject a non-course destination");
  assert.equal(ui.status.textContent, "1 matching lesson.");
  assert.equal(ui.displayedLinks()[0].children[0].textContent, injected.title);
  assert.equal(ui.displayedLinks()[0].href, injected.url);
});

test("at most 30 links are shown, with a truthful overflow message", async () => {
  const many = Array.from({ length: 35 }, (_, index) => ({
    ...lessons[0], id: "01-basics/" + String(index + 1).padStart(2, "0") + "-sample",
    title: "Group " + index,
    url: "lessons/01-basics/" + String(index + 1).padStart(2, "0") + "-sample/index.html"
  }));
  const ui = boot({ data: many });
  await ui.type("group");
  assert.equal(ui.results.children.length, 30);
  assert.match(ui.status.textContent, /35 matching lessons.*first 30/);
});

test("stale response after clear cannot resurrect old results", async () => {
  let release;
  const ui = boot({ fetchImpl: () => new Promise(resolve => { release = resolve; }) });
  const old = ui.type("funcra");
  await ui.type("");
  release({ ok: true, json: async () => lessons });
  await old;
  assert.equal(ui.results.children.length, 0);
  assert.match(ui.status.textContent, /Browse chapters/);
});

test("stale failure after clearing does not replace the helpful hint", async () => {
  let reject;
  const ui = boot({ fetchImpl: () => new Promise((_, fail) => { reject = fail; }) });
  const old = ui.type("funcra");
  await ui.type("");
  reject(new Error("offline"));
  await old;
  assert.equal(ui.results.children.length, 0);
  assert.match(ui.status.textContent, /Browse chapters/);
});

test("failed request can be retried without a page reload", async () => {
  let attempts = 0;
  const ui = boot({ fetchImpl: () => {
    attempts += 1;
    if (attempts === 1) return Promise.reject(new Error("offline"));
    return Promise.resolve({ ok: true, json: async () => lessons });
  }});
  await ui.type("funcra");
  assert.match(ui.status.textContent, /Search is unavailable/);
  await ui.type("फ़ंक्शन");
  assert.equal(attempts, 2);
  assert.equal(ui.displayedLinks()[0].href, lessons[1].url);
});

test("invalid index data does not crash the page", async () => {
  const ui = boot({ data: { not: "an array" } });
  await ui.type("hello");
  assert.match(ui.status.textContent, /Search is unavailable/);
  assert.deepEqual(ui.results.children, []);
});
