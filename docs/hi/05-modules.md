# 05 · मॉड्यूल और इम्पोर्ट (हिन्दी)

यह [अंग्रेज़ी अध्याय](../../examples/05-modules/README.md) का हिन्दी साथी है। मूल `.srp` और `.stdout` फ़ाइलें सभी भाषाओं में एक जैसी रहती हैं।

मॉड्यूल प्रोग्राम को अलग फ़ाइलों में व्यवस्थित करते हैं। `import "...srp" as name` से फ़ाइल को एक छोटे नाम से इस्तेमाल किया जाता है। `pub` द्वारा उपलब्ध कराई गई बाइंडिंग या फ़ंक्शन ही दूसरे मॉड्यूल में उपयोग किए जा सकते हैं।

**मॉड्यूल** = अलग स्रोत फ़ाइल में रखा कोड; **इम्पोर्ट** = दूसरी फ़ाइल की उपलब्ध घोषणाएँ लाना; **नेमस्पेस** = इम्पोर्ट के बाद नामों का समूह; **पब्लिक** = दूसरे मॉड्यूल से उपयोग की अनुमति।

**कैसे चलाएँ:** `scarp verify examples/05-modules/01-modular-inference.srp` के बाद `scarp exec examples/05-modules/01-modular-inference.srp`। फ़ाइलों और आयात के सापेक्ष पथ सही रखने के लिए इस रिपॉज़िटरी की जड़ से चलाएँ।

## पाठ

### 01 · मॉड्यूल से अनुमान गणना

प्रोग्राम `_support/linear.srp` और `_support/settings.srp` आयात करता है। `linear.predict` दो इनपुट संख्याओं से दो स्कोर निकालता है। `settings.title` शीर्षक दिखाता है। `argmax` सबसे बड़े स्कोर का इंडेक्स और `onehot` एक संख्यात्मक वेक्टर बनाता है।

[Scarp स्रोत](../../examples/05-modules/01-modular-inference.srp) · [सटीक अपेक्षित आउटपुट](../../examples/05-modules/01-modular-inference.stdout)

**आउटपुट:** पहले `Modular inference`, फिर `[4.0, 1.0]`, और अंत में `0 [1.0, 0.0]`।

**अभ्यास:** `linear.predict` का स्रोत पढ़ें: उसका आयात किया गया `settings.gain` कहाँ से आता है?

### 02 · आयातित कॉन्स्टैंट अभिव्यक्ति

`_support/constants.srp` एक अन्य `_support/constant_base.srp` को आयात करता है। `pub bind answer` जैसे नाम दूसरे मॉड्यूल में उपलब्ध होते हैं। ऊपर की फ़ाइल में `doubled` इसी मान को दोगुना करता है; `constants.adjust()` डिफ़ॉल्ट आर्गुमेंट वाला फ़ंक्शन है।

[Scarp स्रोत](../../examples/05-modules/02-constant-expressions.srp) · [सटीक अपेक्षित आउटपुट](../../examples/05-modules/02-constant-expressions.stdout)

**आउटपुट:** `constant expressions 42 84 true 0.75 42`।

**अभ्यास:** `answer` और `doubled` के बीच संबंध समझाएँ; `pub` की भूमिका पहचानें।

### 03 · integer series और named argument

इस उदाहरण में `import "_support/integer_series.srp" as series;` से दूसरे स्रोत की सार्वजनिक सुविधाएँ मिलती हैं। `series.sequence(2, start: -1)` दो पूर्णांक -1 और 0 बनाता है। `start: -1` एक **named argument** है, जो डिफ़ॉल्ट मान बदलता है। `series.spread(values)` का परिणाम 0.5 और बिटवाइज़ मास्क का परिणाम 3 है। `integers` संख्यात्मक कलेक्शन है, सामान्य list या map सुविधा नहीं।

[Scarp स्रोत](../../examples/05-modules/03-integer-series.srp) · [सटीक अपेक्षित आउटपुट](../../examples/05-modules/03-integer-series.stdout)

**आउटपुट:** `[integer: -1, 0] 0.5 3`।

**अभ्यास:** `sequence` के `count` और `start` आर्गुमेंट अलग-अलग क्या निर्धारित करते हैं?

### 04 · public और private कोड का अंतर

`_support/inspection.srp` मॉड्यूल में `pub` से उपलब्ध `label` और `adjusted` फ़ंक्शन हैं, लेकिन `helper` तथा `offset` केवल मॉड्यूल के भीतर उपयोग किए जाते हैं। `adjusted(39)` के भीतर 1 और डिफ़ॉल्ट `step = 2` जोड़ने से 42 आता है। दूसरे मॉड्यूल से private नाम को सीधे उपयोग करने की अनुमति नहीं मिलती।

[Scarp स्रोत](../../examples/05-modules/04-public-private-api.srp) · [सटीक अपेक्षित आउटपुट](../../examples/05-modules/04-public-private-api.stdout)

**आउटपुट:** `module tools 42`।

**अभ्यास:** `adjusted` सार्वजनिक होने पर भी `helper` को निजी क्यों रखा जा सकता है?

### 05 · सार्वजनिक सिग्नेचर देखना

`pub bind base: integer = 6;` तथा `pub bind answer: integer = base * 7;` सार्वजनिक typed constants हैं। `pure funcra echo(value: integer = answer)` का डिफ़ॉल्ट आर्गुमेंट 42 है। प्रोग्राम चलाने से `42` छपता है।

[Scarp स्रोत](../../examples/05-modules/05-exported-signatures.srp) · [सटीक अपेक्षित आउटपुट](../../examples/05-modules/05-exported-signatures.stdout)

**कमांड से जाँच:**

```sh
scarp inspect modules --json examples/05-modules/05-exported-signatures.srp
scarp exec examples/05-modules/05-exported-signatures.srp
```

पहला कमांड मॉड्यूल और फ़ंक्शन की जानकारी देता है; यह प्रोग्राम **नहीं चलाता**। दूसरे का आउटपुट `42` है। JSON inspection को Scarp में सामान्य JSON लाइब्रेरी न समझें। [विस्तृत CLI गाइड](cli-quickstart.md) पढ़ें।

**अभ्यास:** `echo()` बिना कोई argument देने पर `42` कैसे लौटाता है?

## सीमाएँ और अगला कदम

कोड की सटीक संगतता [कम्पाइलर नीति](../compatibility.md) और GitHub Actions से जाँची जाती है। भविष्य के async, networking, general collections या autonomous agents को मौजूदा रन करने योग्य API न मानें।

[हिन्दी सामग्री-सूची](README.md) · [मूल पाठ्यक्रम](../../README.md#course)
