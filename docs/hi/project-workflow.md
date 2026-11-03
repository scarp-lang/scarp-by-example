# Scarp में पहला असली प्रोजेक्ट — हिन्दी

यह गाइड **प्रकाशित Scarp v0.0.5-alpha.4** पर आधारित है। आधिकारिक स्रोत कमिट `79141329176f5dce51457e90a6652902f6432135` है। यह कोई भविष्य का प्रस्ताव नहीं है। [English guide](../project-workflow.md) · [कम्पाइलर संगतता](../compatibility.md)

Scarp प्रोजेक्ट एक डायरेक्टरी होती है जिसमें `Scarp.project` नाम की manifest फ़ाइल और एक `.srp` entrypoint फ़ाइल होती है। अभी `launch` प्रोग्राम को **interpreter** से चलाता है; native executable नहीं बनाता।

## चरण 1 — नया प्रोजेक्ट बनाएँ

ऐसी डायरेक्टरी से कमांड चलाएँ जहाँ `hello-world` पहले से मौजूद न हो:

```sh
scarp create hello-world
```

बनने वाली फ़ाइलें:

```text
hello-world/
├── Scarp.project
└── src/
    └── main.srp
```

Manifest का सही रूप:

```text
scarp-project: 1
name: hello-world
entry: src/main.srp
```

`src/main.srp` में शुरुआत में यह प्रोग्राम होता है:

```scarp
print("Hello from Scarp!");
```

**याद रखें:** `create` पहले से मौजूद फ़ोल्डर को नहीं अपनाता या बदलता—भले ही वह खाली हो। यह किसी पैकेज को इंटरनेट से डाउनलोड भी नहीं करता।

## चरण 2 — बिना चलाए प्रोजेक्ट की जाँच

```sh
scarp verify hello-world
```

`verify` manifest और उसके entrypoint के syntax, नाम, प्रकार और imports की उपलब्ध **static जाँच** करता है। सामान्य runtime statements नहीं चलते। सफल होने पर कुछ नहीं छपता। यदि आप सीधे फ़ाइल की जाँच चाहते हैं, तो `scarp verify hello-world/src/main.srp` चलाएँ; इसमें manifest की जाँच नहीं होती।

## चरण 3 — प्रोजेक्ट चलाएँ

```sh
scarp launch hello-world
```

आउटपुट:

```text
Hello from Scarp!
```

`launch` असली Scarp interpreter से manifest की घोषित फ़ाइल चलाता है। यह native executable या installable package नहीं बनाता। Project-directory का नाम स्पष्ट देना अनिवार्य है; Scarp ऊपर की directories में manifest ढूँढता नहीं है।

## चरण 4 — इस कोर्स के तैयार उदाहरण की जाँच

हमारा [नमूना manifest](../../tutorials/first-project/Scarp.project), [स्रोत](../../tutorials/first-project/src/main.srp) और [सटीक आउटपुट](../../tutorials/first-project/expected.stdout) एक ही रिपॉज़िटरी में हैं। **scarp-by-example की मुख्य डायरेक्टरी से** चलाएँ:

```sh
scarp verify tutorials/first-project
scarp launch tutorials/first-project
```

इन कमांड को CI में Linux, Windows और macOS पर वास्तविक कम्पाइलर से जाँचा जाता है। प्रोजेक्ट ट्यूटोरियल को पहले से मौजूद **50 नंबर वाले पाठों** में अलग से नहीं गिना जाता।

## अभ्यास

अपने प्रोजेक्ट की कॉपी में `src/main.srp` बदलें:

```scarp
print(6 * 7);
```

पहले `scarp verify YOUR_PROJECT_DIRECTORY` चलाएँ; फिर `scarp launch YOUR_PROJECT_DIRECTORY`। क्या परिणाम `42` आता है? यह Scarp के समर्थित पूर्णांक गुणा का उदाहरण है।

दूसरे प्रयोग में अस्थायी प्रोजेक्ट के भीतर `print(1 / 0);` डालकर static और runtime जाँच का अंतर समझें: `verify` प्रोग्राम नहीं चलाता, लेकिन `launch` runtime त्रुटि देगा। मूल कोर्स के नमूने में बदलाव न करें।

## Manifest के नियम

- `Scarp.project` UTF-8 में होती है और इसमें **तीन सही क्रम वाली पंक्तियाँ** होनी चाहिए।
- अधिकतम फ़ाइल आकार 4096 bytes है।
- प्रोजेक्ट नाम 1–96 UTF-8 bytes का होना चाहिए; पथ separator, colon और control characters नहीं होने चाहिए।
- `entry` केवल प्रोजेक्ट के भीतर का relative `.srp` पथ होना चाहिए। `../` जैसे रास्ते, असुरक्षित symlinks और अज्ञात keys मना हैं।
- गलत manifest पर सामान्यतः exit code `1` आता है। `--diagnostic-format=json` से schema-v1 त्रुटि विवरण मिल सकता है।
- `verify` में runtime-budget flags नहीं होते; `launch` में हैं।

**सीमा:** `create`, `verify` और `launch` का होना native compiler, package registry, dependency lockfile, GPU, autograd या language-level async के लागू होने का प्रमाण नहीं है। यह अभी शुरुआती development manifest format है।

[हिन्दी पाठ सूची](README.md) · [CLI हिंदी गाइड](cli-quickstart.md) · [Official compiler release](https://github.com/scarp-lang/scarp/releases/tag/v0.0.5-alpha.4)
