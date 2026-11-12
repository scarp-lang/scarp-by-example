# Scarp alpha.8: प्रोजेक्ट बनाना और टेस्ट करना

यह पाठ प्रकाशित **Scarp v0.0.6-alpha.8** के लिए है। इसका निश्चित compiler source commit `37253e7805c0ca594560700dd1deb3928458e60d` है। पुराने alpha.4 compiler से इसे न चलाएँ। [English guide](../alpha8-project-testing.md) और [पूरा प्रोजेक्ट](../../tutorials/alpha8-project-testing/README.md) देखें।

## 1. `scarp.project` क्या है?

`scarp.project` एक छोटा, declarative project manifest है। यह TOML, JSON या executable Scarp code नहीं है। उदाहरण:

```text
project "alpha8-test-workshop" {
    version: "0.1.0"
    entry: "src/main.srp"
    type: "application"
    dependencies {}
}
```

`entry` से compiler को मुख्य फ़ाइल का पता मिलता है। `dependencies {}` अभी खाली आरक्षित ब्लॉक है; इससे कोई package डाउनलोड नहीं होता। नया project बनाने के लिए `scarp init new-project` लिखें; यह पहले से मौजूद directory को overwrite नहीं करता।

## 2. प्रोग्राम चलाएँ और जाँचें

[`src/offset.srp`](../../tutorials/alpha8-project-testing/src/offset.srp) में reusable `pure funcra` है। [`src/main.srp`](../../tutorials/alpha8-project-testing/src/main.srp) इसे import करके 42 प्रिंट करता है:

```sh
scarp verify tutorials/alpha8-project-testing
scarp run tutorials/alpha8-project-testing
```

**`verify`** source की static जाँच करता है, प्रोग्राम को चलाता नहीं। **`run`** असली Scarp interpreter से चलाता है। परिणाम ठीक `42` और उसके बाद एक newline होना चाहिए; [`expected.stdout`](../../tutorials/alpha8-project-testing/expected.stdout) में सही bytes दिए गए हैं।

## 3. `assert` और टेस्ट फ़ाइलें

[`tests/addition.srp`](../../tutorials/alpha8-project-testing/tests/addition.srp) में Boolean शर्तों की जाँच होती है। उदाहरण: `assert(2 + 2 == 4);`। शर्त false होने पर runtime diagnostic **E0065** मिलता है। `assert` अपने आप कोई output नहीं छापता।

```sh
scarp test --list tutorials/alpha8-project-testing
scarp test --require-tests tutorials/alpha8-project-testing
scarp test --json tutorials/alpha8-project-testing
```

`--list` केवल फ़ाइलों के नाम दिखाता है; टेस्ट नहीं चलाता। `--json` schema 1 में machine-readable result देता है। `--require-tests` से बिना टेस्ट वाले प्रोजेक्ट पर CI गलती से सफल नहीं होगा।

## 4. `.stdin` में टेस्ट का इनपुट

[`tests/input.srp`](../../tutorials/alpha8-project-testing/tests/input.srp) दो लाइन पढ़ता है। उसी नाम वाली [`tests/input.stdin`](../../tutorials/alpha8-project-testing/tests/input.stdin) में `17` और `25` हैं। परीक्षण इनको जोड़कर 42 से मिलाता है।

```sh
scarp test --json --filter input tutorials/alpha8-project-testing
```

`--filter input` केवल नाम में `input` वाले टेस्ट चुनता है। यह case-sensitive साधारण substring है, regex नहीं। अपने **अलग लोकल कॉपी** में 25 को 24 करके देखें: अब assertion विफल होगा और E0065 मिलेगा। मूल Git fixture को न बदलें।

## 5. वास्तविक compiler से जाँच

```sh
python scripts/verify_alpha8_project_testing.py --compiler /absolute/path/to/scarp
```

Windows में compiler के `scarp.exe` का पूरा path लिखें। verifier application output, JSON result, test order, filter, गलत assertion, empty test suite और input isolation जाँचता है। GitHub Actions में Linux, Windows और macOS पर exact published compiler commit से build किया जाता है।

**ध्यान दें:** यह interpreter-आधारित पाठ है। इसमें native executable, package installation, async, GPU या AI model training होने का दावा नहीं किया गया है। मुख्य numbered course का compiler pin अलग और अपरिवर्तित है।
