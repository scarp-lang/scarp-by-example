# Scarp CLI — शुरुआत से सीखें (हिन्दी)

यह गाइड **Scarp v0.0.6-alpha.2** के प्रकाशित स्रोत कमिट `398b8ff705154a02423fe458ce3a427401e81e31` के लिए है। Scarp अभी **प्री-रिलीज़** है। यहाँ बताए गए कमांड इसी संस्करण के वास्तविक कम्पाइलर स्रोत पर आधारित हैं।

यह कमांड सीखने की गाइड है। `inspect` का आउटपुट बदल सकने वाला डिबग डेटा है, इसलिए इसके लिए नई `.srp`/`.stdout` पाठ फ़ाइलें नहीं बनाई जातीं।

## 1. कम्पाइलर तैयार करना

[संगतता निर्देश](../compatibility.md) से निर्धारित स्रोत डाउनलोड और बिल्ड करें। इसके बाद जाँचें:

```sh
scarp version
scarp guide
scarp diagnose
```

- `version` चल रहे कम्पाइलर का संस्करण दिखाता है।
- `guide` सही कमांड और उनकी मदद दिखाता है।
- `diagnose` बिना इंटरनेट उपयोग किए कम्पाइलर और सिस्टम की सुविधाएँ बताता है।

यदि `scarp` PATH में नहीं है, तो उसका पूरा executable पथ लिखें: Linux/macOS पर `target/debug/scarp` और Windows पर `target\debug\scarp.exe`। नीचे दिए उदाहरण **scarp-by-example** रिपॉज़िटरी की मुख्य डायरेक्टरी से चलाएँ।

## 2. पहले verify, फिर exec

```sh
scarp verify examples/01-basics/01-hello.srp
scarp exec examples/01-basics/01-hello.srp
```

**`verify`** स्रोत, इम्पोर्ट, नाम और प्रकार की उपलब्ध स्थिर जाँच (static validation) करता है। यह प्रोग्राम की runtime पंक्तियाँ **नहीं चलाता**। सफल रहने पर सामान्यतः कुछ नहीं छपता और exit code `0` होता है।

**`exec`** वास्तविक Scarp interpreter से प्रोग्राम चलाता है। पहले पाठ का आउटपुट `Hello from Scarp!` है; [मूल आउटपुट फ़ाइल](../../examples/01-basics/01-hello.stdout) से तुलना करें। `exec` कोई native executable नहीं बनाता।

मॉड्यूल वाले उदाहरण में `_support` की साथी फ़ाइलें उसी स्थान पर रखें:

```sh
scarp verify examples/05-modules/01-modular-inference.srp
scarp exec examples/05-modules/01-modular-inference.srp
```

## 3. नया Scarp प्रोजेक्ट (प्रकाशित alpha.4 में नया)

ऐसी डायरेक्टरी से शुरू करें जहाँ `hello-world` फ़ोल्डर पहले से मौजूद न हो:

```sh
scarp create hello-world
scarp verify hello-world
scarp launch hello-world
```

`create` नया फ़ोल्डर बनाता है जिसमें `Scarp.project` और `src/main.srp` फ़ाइलें होती हैं। पहले से मौजूद फ़ोल्डर को यह कभी नहीं बदलता। `verify DIRECTORY` manifest तथा स्रोत की static जाँच करता है, जबकि `launch DIRECTORY` उसी प्रोग्राम को interpreter में चलाता है।

Manifest की तीन पंक्तियाँ हैं:

```text
scarp-project: 1
name: hello-world
entry: src/main.srp
```

कोर्स के तैयार नमूने को भी चलाएँ:

```sh
scarp verify tutorials/first-project
scarp launch tutorials/first-project
```

इन कमांड के लिए [विस्तृत हिंदी प्रोजेक्ट ट्यूटोरियल](project-workflow.md) पढ़ें।

## 4. कोड की अंदरूनी संरचना देखना

```sh
scarp inspect tokens examples/01-basics/01-hello.srp
scarp inspect ast examples/01-basics/01-hello.srp
scarp inspect modules examples/05-modules/01-modular-inference.srp
scarp inspect modules --json examples/05-modules/01-modular-inference.srp
scarp inspect modules --json tutorials/module-inspection
scarp inspect symbols --json tutorials/module-inspection
scarp inspect references --json tutorials/module-inspection
```

| कमांड | वास्तविक उपयोग |
| --- | --- |
| `inspect tokens` | सिर्फ़ शब्दों/टोकन और उनके स्थान की जाँच; पूरा parsing या type-checking नहीं |
| `inspect ast` | स्रोत का syntax tree दिखाता है; इम्पोर्ट resolve नहीं करता, प्रकार नहीं जाँचता और प्रोग्राम नहीं चलाता |
| `inspect modules` | इम्पोर्ट सहित मॉड्यूलों की स्थिर जाँच; alpha.5 से प्रोजेक्ट डायरेक्टरी स्वीकार करता है |
| `inspect symbols` | alpha.6 से नाम, घोषणा और इम्पोर्ट की बिना चलाए स्थिर सूची |
| `inspect references` | alpha.6 से नाम के प्रयोग, कॉल और असाइनमेंट के स्थान की स्थिर सूची |

**नया alpha.5:** ऊपर दिया `inspect modules --json tutorials/module-inspection` कमांड प्रोजेक्ट की स्थिर जानकारी देता है; वह प्रोग्राम चलाकर आउटपुट नहीं बनाता। [पूरा दो-मॉड्यूल हिंदी उदाहरण](project-inspection.md) देखें। प्रयोगात्मक C11 backend सिर्फ Rust embedding API है, `scarp compile` CLI नहीं।

**प्रकाशित alpha.6 में नया:** [`inspect symbols` और `inspect references` की हिंदी गाइड](source-navigation.md) देखें। दोनों `--json` के साथ संस्करण-1 संरचित जानकारी देते हैं और प्रोग्राम की runtime पंक्तियाँ नहीं चलाते। यह LSP या rename सुविधा नहीं है।

`inspect ast` का परिणाम बदल सकने वाला **debug format** है, स्थायी JSON API नहीं। `inspect ast --json` और `inspect tokens --json` उपलब्ध नहीं हैं। इनका आउटपुट प्रोग्राम के `.stdout` से अलग होता है।

## 5. verify और पुराने check में अंतर

**`scarp verify` और `scarp check` एक जैसे नहीं हैं।** पुराने `check` में कुछ runtime expressions वास्तव में evaluate होते हैं, लेकिन उनका आउटपुट छिपा रहता है। पुराने `run` और नए `exec` का उद्देश्य प्रोग्राम चलाना है।

अंतर समझने के लिए नंबर वाले पाठों के बाहर एक अस्थायी `.srp` फ़ाइल में यह लिख सकते हैं:

```scarp
print(1 / 0);
```

`scarp verify FILE.srp` इसे static स्तर पर सही मानेगा। `scarp check FILE.srp` गणना चलने पर शून्य से भाग देने की त्रुटि देगा। `scarp exec FILE.srp` भी त्रुटि देगा। रिपॉज़िटरी की [स्वचालित CLI जाँच](../../scripts/verify_cli.py) अस्थायी फ़ाइल बनाकर इसी अंतर को जाँचती है।

## जल्दी याद रखने के लिए

- `scarp version` — संस्करण; `scarp guide` — कमांड की मदद; `scarp diagnose` — सिस्टम की क्षमताएँ।
- `scarp verify FILE` — चलाए बिना static जाँच।
- `scarp exec FILE` — स्रोत चलाकर असली आउटपुट प्राप्त करें।
- `scarp inspect tokens/ast/modules/symbols/references FILE` — कम्पाइलर की अंदरूनी जानकारी देखें।
- `scarp run` और `scarp check` — पुराने compatibility कमांड; `check` runtime evaluation कर सकता है।

सफलता का exit code सामान्यतः `0`, स्रोत/प्रोग्राम त्रुटि `1` और कमांड के गलत प्रयोग का `2` है। यह संस्करण `create`, project `verify` और interpreter-backed `launch` उपलब्ध कराता है, लेकिन `compile`, native executable या package publishing उपलब्ध नहीं कराता।

[हिन्दी पाठ सूची](README.md) · [English CLI guide](../cli-quickstart.md) · [संगतता नीति](../compatibility.md)
