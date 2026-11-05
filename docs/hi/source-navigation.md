# Scarp में नाम और संदर्भ खोजें (alpha.6)

प्रकाशित Scarp `v0.0.6-alpha.1` में कोड को **बिना चलाए** किसी नाम की घोषणा (definition) और उसके प्रयोग (reference) देख सकते हैं। इसे *स्थिर स्रोत निरीक्षण* कहते हैं। यह अभी पूरा Language Server (LSP), स्वचालित rename या संपादन के बीच पहचान बनाए रखने वाला सिस्टम **नहीं** है।

यह गाइड पहले से मौजूद [दो-मॉड्यूल प्रोजेक्ट](../../tutorials/module-inspection/Scarp.project) पर आधारित है। `src/lib/math.srp` में `answer` नाम की public बाइंडिंग है और `src/main.srp` उसे `math` नाम से import करके उपयोग करता है।

## कमांड चलाएँ

[संगतता गाइड](../compatibility.md) में बताए गए निश्चित कम्पाइलर संस्करण को तैयार करें। फिर कोर्स की मुख्य डायरेक्टरी से:

```sh
scarp verify tutorials/module-inspection
scarp inspect modules --json tutorials/module-inspection
scarp inspect symbols --json tutorials/module-inspection
scarp inspect references --json tutorials/module-inspection
scarp launch tutorials/module-inspection
```

- `inspect symbols` घोषणाओं और नामों की सूची देता है।
- `inspect references` बताता है कि वे नाम कहाँ पढ़े, लिखे या बुलाए गए हैं।
- `launch` वास्तव में interpreter से प्रोग्राम चलाता है और [मूल आउटपुट](../../tutorials/module-inspection/expected.stdout) के अनुसार `42` छापता है।

`--json` से प्राप्त जानकारी प्रोग्राम का आउटपुट **नहीं** है; इसके लिए नई `.stdout` पाठ फ़ाइल बनाना गलत होगा। आप प्रोजेक्ट फ़ोल्डर की जगह `tutorials/module-inspection/src/main.srp` भी दे सकते हैं।

## JSON समझें

`schema_version` का मान `1` है। `kind` में `scarp.symbols` या `scarp.references` आता है। `files` में स्रोत फ़ाइलें, `symbols` में नामों की पहचान और `references` में उनके उपयोग के स्थान आते हैं।

`location.span` में UTF-8 **बाइट** स्थान होते हैं, जबकि लाइन और कॉलम 1 से शुरू होने वाली Unicode-scalar स्थिति होती है। एक बार निकली symbol ID अगली जाँच या संपादन में स्थायी नहीं मानी जा सकती। फ़ाइलों के दिखाए गए पथ Windows और Linux पर अलग हो सकते हैं।

`print(1 / 0);` लिखी अस्थायी फ़ाइल पर स्थिर inspection सफल हो सकती है क्योंकि गणना चलती नहीं; `exec` पर रनटाइम त्रुटि मिलेगी। लेकिन अज्ञात नाम इस्तेमाल करने पर inspection भी त्रुटि देगी। [स्वचालित CLI टेस्ट](../../scripts/verify_cli.py) इन्हीं सीमाओं को जाँचता है।

**अभ्यास:** प्रोजेक्ट में `answer` की घोषणा किस फ़ाइल में है? उसका उपयोग किस फ़ाइल में हुआ? `symbols` और `references` से तुलना करें।

[English tutorial](../source-navigation.md) · [आधिकारिक कम्पाइलर अनुबंध](https://github.com/scarp-lang/scarp/blob/v0.0.6-alpha.1/docs/symbol-index.md)
