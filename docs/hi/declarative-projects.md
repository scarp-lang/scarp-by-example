# नया Scarp प्रोजेक्ट: `scarp.project` (हिन्दी)

Scarp के प्रकाशित नए संस्करणों में प्रोजेक्ट के लिए छोटे अक्षरों वाला
**`scarp.project`** मैनिफ़ेस्ट इस्तेमाल होता है।
`scarp init` यह नया प्रारूप बनाता है (alpha.8 से)।
पुराना `Scarp.project` और `scarp create`
पुराने प्रोजेक्ट चलाने के लिए उपलब्ध हैं। नए काम में
`scarp.project` अपनाएँ।

[असली प्रोजेक्ट की फ़ाइलें](../../tutorials/declarative-project/README.md) ·
[English tutorial](../declarative-projects.md) ·
[पुराने प्रारूप का गाइड](project-workflow.md)

## 1. प्रोजेक्ट बनाएँ

```sh
scarp init learning-project
scarp verify learning-project
scarp run learning-project
```

`init` पहले से मौजूद फ़ोल्डर में फ़ाइलें नहीं बदलता।
इस कोर्स की `tutorials/declarative-project` डायरेक्टरी
पहले से मौजूद है, इसलिए उस पर दोबारा `init` न चलाएँ।

मैनिफ़ेस्ट:

```text
project "learning-project" {
    version: "0.1.0"
    entry: "src/main.srp"
    type: "application"
    dependencies {}
}
```

यह **TOML या JSON नहीं** है। अभी `dependencies {}`
के भीतर पैकेज जोड़कर उन्हें डाउनलोड नहीं किया जा सकता।
`src/main.srp` दूसरे मॉड्यूल से
`multiply(6, 7)` चलाता है।

## 2. जाँचें और चलाएँ

कोर्स की मूल डायरेक्टरी से:

```sh
scarp verify tutorials/declarative-project
scarp run tutorials/declarative-project
```

`verify` कोड चलाए बिना जाँचता है; सफल होने पर
आउटपुट खाली रहता है। `run` interpreter से
असली प्रोग्राम चलाता है। आउटपुट ठीक यह है:

```text
Total: 42
```

प्रोजेक्ट की डायरेक्टरी के भीतर:

```sh
cd tutorials/declarative-project
scarp verify
scarp exec
```

बिना फ़ाइल नाम वाला `exec` वर्तमान डायरेक्टरी का
सही मैनिफ़ेस्ट पढ़ता है (alpha.18 से)। गलत मैनिफ़ेस्ट मिलने पर
मनमानी दूसरी फ़ाइल चलाना सुरक्षित fallback नहीं है।

## 3. मैनिफ़ेस्ट की जानकारी पढ़ें

```sh
scarp project info --json tutorials/declarative-project
```

यह केवल मैनिफ़ेस्ट की सत्यापित जानकारी देता है, प्रोग्राम नहीं
चलाता। JSON में `schema_version: 1`,
`name: learning-project`,
`manifest: scarp.project` और
`format: v2` जैसी जानकारी मिलती है।

## 4. असली टेस्ट चलाएँ

```sh
scarp test --list --json tutorials/declarative-project
scarp test --require-tests --json tutorials/declarative-project
scarp test --json --filter input tutorials/declarative-project
```

पहला कमांड सिर्फ़ टेस्ट फाइलों की सूची पढ़ता है। दूसरा दो
वास्तविक Scarp प्रोग्राम चलाकर कुल **2 passed, 0 failed**
की जाँच करता है। \`--require-tests\` खाली टेस्ट-सूट को
सफल नहीं मानता। `02-input.srp` में
`read_line()` का इनपुट उसकी
`02-input.stdin` फ़ाइल के 6 और 7 से मिलता है।
इससे दूसरा टेस्ट खुद 42 की जाँच कर सकता है।

**अभ्यास:** एक अलग कॉपी में `multiply(7, 8)`
चलाएँ और आउटपुट पहले अनुमान से बताएँ। फिर एक नया
`tests/*.srp` प्रोग्राम बनाकर 56 की
`assert` जाँच लिखें।

## पुरानी फ़ाइल से नई फ़ाइल

पुराने `Scarp.project` में तीन पंक्तियाँ थीं:
`scarp-project: 1`, `name:` और
`entry:`। नया मैनिफ़ेस्ट एक अलग grammar है।
सिर्फ़ नाम का `S` छोटा कर देना
पूरी migration नहीं है। नया मैनिफ़ेस्ट बनाएँ, verify और run करें,
फिर पुरानी फ़ाइल हटाएँ।

अज्ञात fields, असुरक्षित रास्ते, गलत मैनिफ़ेस्ट और प्रोजेक्ट के
बाहर स्थित entrypoint स्वीकार नहीं किए जाते। अभी package registry,
dependency installation, lockfile, native executable build या
browser में Scarp चलाने की सुविधा नहीं है।
