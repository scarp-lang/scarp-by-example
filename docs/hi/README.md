# Scarp by Example — हिन्दी सीखने की सामग्री

यहाँ हिन्दी में समझाने वाले पाठ उपलब्ध हैं। **Scarp प्रोग्राम की मूल .srp फ़ाइलें नहीं बदली गई हैं।** प्रत्येक व्याख्या वही चलने वाला स्रोत और सत्यापित अपेक्षित आउटपुट दिखाती है।

## उपलब्ध अध्याय

- [01 · Scarp की बुनियाद](01-basics.md) — 16 पाठ: बाइंडिंग, स्कोप, Unicode स्ट्रिंग, आउटपुट और रूपांतरण।
- [02 · नियंत्रण प्रवाह](02-control-flow.md) — 4 पाठ: शर्तें, while, repeat और nested repeat।
- [03 · फ़ंक्शन](03-functions.md) — 4 पाठ: प्रकार, रिकर्शन और कॉन्ट्रैक्ट।
- [04 · संख्यात्मक कलेक्शन](04-collections.md) — 14 पाठ: वेक्टर, नॉर्म, विंडो, न्यूटन विधि और संख्यात्मक फ़ंक्शन।
- [05 · मॉड्यूल](05-modules.md) — 5 पाठ: इम्पोर्ट, कॉन्स्टैंट, integer series, public/private API और फ़ंक्शन सिग्नेचर।
- [06 · AI के संख्यात्मक आधार](06-ai-foundations.md) — 16 पाठ: मैट्रिक्स गुणन, लॉस, वर्ग स्कोर और संख्यात्मक संभावनाएँ।

**कुल: 59 पाठ, 6 अध्याय।** [अंग्रेज़ी पाठ्यक्रम](../../README.md#course) में वही मूल `.srp` स्रोत और अपेक्षित आउटपुट हैं।

**नया:** [Scarp में अपना पहला प्रोजेक्ट (alpha.4 से उपलब्ध)](project-workflow.md) — `create`, `verify DIRECTORY` और `launch` का प्रयोग सीखें।

**प्रकाशित alpha.6:** [स्रोत में नाम और संदर्भ खोजें](source-navigation.md) — बिना प्रोग्राम चलाए `inspect symbols` और `inspect references` से घोषणाएँ और प्रयोग देखें। [दो-मॉड्यूल वर्कशॉप](https://scarp-lang.github.io/scarp-by-example/projects/source-navigation/) में दो अलग `base` बाइंडिंग खोजें।

**प्रकाशित alpha.5:** [दो मॉड्यूल वाले प्रोजेक्ट को बिना चलाए inspect करें](project-inspection.md) — `scarp inspect modules --json DIRECTORY` की वास्तविक static जानकारी।

**नया alpha.3 अभ्यास:** [AI coding lab में अतिरिक्त चुनौती](https://scarp-lang.github.io/scarp-by-example/labs/06-ai-foundations/#stretch-challenge) — temperature-controlled softmax और Top-K से स्कोर रैंक करें। यह random sampling या model training नहीं है।

## Scarp चलाने का तरीका

नए CLI कमांड जानने के लिए [हिन्दी CLI गाइड](cli-quickstart.md) पढ़ें। इसमें `verify` और पुराने `check` का वास्तविक अंतर भी है।

पहले [आधिकारिक कम्पाइलर](https://github.com/scarp-lang/scarp) का संस्करण जाँचें। यह प्रोजेक्ट **प्रकाशित Scarp v0.0.6-alpha.5 के सटीक स्रोत कमिट `205e92f`** पर उदाहरणों को जाँचता है; पुराने प्री-रिलीज़ का सिंटैक्स अलग हो सकता है। [संगतता नीति](../compatibility.md) देखें।

```sh
scarp verify examples/01-basics/01-hello.srp
scarp exec examples/01-basics/01-hello.srp
```

कमांड प्रोजेक्ट के मूल फ़ोल्डर से चलाएँ। आउटपुट की तुलना संबंधित `.stdout` फ़ाइल से करें। यदि कमांड PATH में नहीं है तो निर्मित executable का पूरा पथ प्रयोग करें।

**नोट:** सामान्य maps/sets, structured errors, async, concurrency और networking के पाठ अभी runnable के रूप में प्रकाशित नहीं हैं।

## योगदान

अध्याय और पाठ क्रमांक समान रखें, और keywords, .srp स्रोत तथा .stdout आउटपुट का अनुवाद न करें। [अनुवाद नीति](../translations/README.md) और [योगदान गाइड](../../CONTRIBUTING.md) पढ़ें.
