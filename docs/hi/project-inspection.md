# Scarp प्रोजेक्ट के मॉड्यूल बिना प्रोग्राम चलाए देखें

**इस कोर्स का वर्तमान कंपाइलर:** [Scarp v0.0.6-alpha.1](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.1), स्रोत कमिट `aa329a22cf2bf92d2c9814a26ff9c8b67a72e6e8`। यह **प्री-रिलीज़** है, stable नहीं। मॉड्यूल निरीक्षण पहली बार alpha.5 में आया था।

alpha.5 से उपलब्ध `scarp inspect modules --json PROJECT_DIRECTORY` उपलब्ध है। यह `Scarp.project` फ़ाइल पढ़कर entrypoint और उसके imports की **static जाँच** करता है और schema-v1 मॉड्यूल जानकारी देता है। सामान्य प्रोग्राम की `print` जैसी पंक्तियाँ नहीं चलाता।

[वेबसाइट का उदाहरण](https://scarp-lang.github.io/scarp-by-example/projects/module-inspection/) · [English guide](../project-inspection.md)

## 1. प्रोजेक्ट में दो मॉड्यूल

```text
tutorials/module-inspection/
├── Scarp.project
├── src/
│   ├── main.srp
│   └── lib/
│       └── math.srp
└── expected.stdout
```

`Scarp.project` में ये तीन पंक्तियाँ हैं:

```text
scarp-project: 1
name: module-inspection
entry: src/main.srp
```

`src/main.srp` दूसरे मॉड्यूल को import करता है:

```scarp
import "lib/math.srp" as math;
print(math.answer);
```

`src/lib/math.srp` में सार्वजनिक scalar स्थिर binding है:

```scarp
// Public compile-time scalar binding imported by main.srp.
pub bind answer = 21 * 2;
```

वास्तविक interpreter से परिणाम `42` आता है; यह `expected.stdout` में दर्ज है। यह उदाहरण 51 numbered lessons से अलग है।

## 2. पहले inspect, फिर launch

**scarp-by-example** रिपॉज़िटरी की root डायरेक्टरी में वर्तमान प्रकाशित alpha.6 कंपाइलर से चलाएँ:

```sh
scarp verify tutorials/module-inspection
scarp inspect modules --json tutorials/module-inspection
scarp inspect modules --json tutorials/module-inspection/src/main.srp
scarp launch tutorials/module-inspection
```

- **verify DIRECTORY** manifest और इम्पोर्ट की स्थिर जाँच करता है; प्रोग्राम नहीं चलाता।
- **inspect modules --json DIRECTORY** imports, dependencies और modules की schema-v1 JSON जानकारी देता है। इसी entrypoint वाली `.srp` फ़ाइल inspect करने पर imports, dependencies और symbols समान होने चाहिए। schema-v1 में module का `path` केवल display label है, जो प्लेटफ़ॉर्म के अनुसार अलग दिख सकता है।
- **launch DIRECTORY** वास्तविक interpreter से प्रोग्राम चलाकर `42` तथा newline प्रिंट करता है।

पुराना `scarp modules --json DIRECTORY` कमांड संगतता के लिए मौजूद है, लेकिन नए निर्देशों में `scarp inspect modules` का प्रयोग करें।

रिपॉज़िटरी का `scripts/verify_cli.py` module graph की समानता, runtime execution न होने, और गलत manifest पर JSON error की जाँच करता है।

## 3. छोटा अभ्यास

प्रोजेक्ट की **अलग कॉपी** बनाएँ। `math.srp` में binding को `pub bind answer = 30 + 12;` कर दें। फिर inspect, verify और launch करें। दोनों expressions का मान `42` ही है। अभ्यास के बाद मूल फ़ाइल न बदलें।

## 4. किन सुविधाओं को उपलब्ध न समझें

वर्तमान प्रीरिलीज़ में `scarp compile` कमांड से सामान्य `.srp` प्रोग्राम का native executable नहीं बनता। प्रयोगात्मक **C11 emitter** सिर्फ सीमित Rust embedding API के रूप में मौजूद है; बाहरी C11 compiler host को देना होता है। इसलिए native compilation, package registry, GPU, async/networking या पूर्ण AI training framework को वर्तमान Scarp सुविधा न मानें।

[कंपाइलर संगतता](../compatibility.md) · [CLI सीखें](cli-quickstart.md) · [पहला Scarp प्रोजेक्ट](project-workflow.md)

**अगला अभ्यास:** [दो-मॉड्यूल source-navigation वर्कशॉप](https://scarp-lang.github.io/scarp-by-example/projects/source-navigation/) में दो अलग `base` घोषणाओं और उनके प्रयोगों को खोजें।
