# 05 · मॉड्यूल और इम्पोर्ट (हिन्दी)

यह [अंग्रेज़ी अध्याय](../../examples/05-modules/README.md) का हिन्दी साथी है। मूल `.srp` और `.stdout` फ़ाइलें सभी भाषाओं में एक जैसी रहती हैं।

मॉड्यूल प्रोग्राम को अलग फ़ाइलों में व्यवस्थित करते हैं। `import "...srp" as name` से फ़ाइल को एक छोटे नाम से इस्तेमाल किया जाता है। `pub` द्वारा उपलब्ध कराई गई बाइंडिंग या फ़ंक्शन ही दूसरे मॉड्यूल में उपयोग किए जा सकते हैं।

**मॉड्यूल** = अलग स्रोत फ़ाइल में रखा कोड; **इम्पोर्ट** = दूसरी फ़ाइल की उपलब्ध घोषणाएँ लाना; **नेमस्पेस** = इम्पोर्ट के बाद नामों का समूह; **पब्लिक** = दूसरे मॉड्यूल से उपयोग की अनुमति।

**कैसे चलाएँ:** `scarp check examples/05-modules/01-modular-inference.srp` के बाद `scarp run examples/05-modules/01-modular-inference.srp`। फ़ाइलों और आयात के सापेक्ष पथ सही रखने के लिए इस रिपॉज़िटरी की जड़ से चलाएँ।

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

## सीमाएँ और अगला कदम

कोड की सटीक संगतता [कम्पाइलर नीति](../compatibility.md) और GitHub Actions से जाँची जाती है। भविष्य के async, networking, general collections या autonomous agents को मौजूदा रन करने योग्य API न मानें।

[हिन्दी सामग्री-सूची](README.md) · [मूल पाठ्यक्रम](../../README.md#course)
