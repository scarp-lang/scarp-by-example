# Static Scarp learning portal

This project is built by `python scripts/build_site.py` using the real numbered `.srp` files, their byte-exact `.stdout` fixtures and the English/Hindi chapter guides. No external frontend dependencies, services, CDNs, frameworks or fake browser execution are needed.

## Generated routes

| Route | Content |
| --- | --- |
| `index.html` | Homepage, six chapter cards and a client-side lesson finder |
| `chapters/NN-topic/index.html` | Chapter overview with links to its runnable lessons |
| `lessons/NN-topic/NN-example/index.html` | Dedicated page for each lesson: source, expected output, local run commands, previous/next navigation, guides |
| `search-index.json` | Static metadata for local search; never external tracking |

A course with 50 runnable examples produces **57 HTML documents** (home, six chapters, fifty lessons). The URL paths are designed to work under the GitHub Pages project prefix `/scarp-by-example/` and from nested subdirectories. All local links are checked by the Python unit tests.

## Browser behavior

The theme toggle stores a preference locally when available; the initial dark design works without JavaScript. Search and copy-code are progressive enhancements. Every lesson and chapter remains navigable without JavaScript, and the original GitHub source/fixture links are always present.

Displayed source is escaped as text, not evaluated. Control-character output such as a literal carriage return is rendered visibly as `\\r`, without rewriting the original fixture. No code is executed in the browser.

The website links to the original English and Hindi chapter explanations. Scarp is prerelease software; all examples are pinned to the exact compiler commit in `docs/compiler-target.json`.

## Build and test

```sh
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/build_site.py --output dist
```

The GitHub Pages workflow first compiles and validates every real Scarp lesson and checks the CLI, then generates the static site. Pull requests build the site but do not deploy; merged `main` changes deploy using GitHub Actions. Git tracks source files under `site/` and `scripts/`, not generated `dist/`.
