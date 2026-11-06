# Scarp में नाम और संदर्भ खोजें (alpha.6)

प्रकाशित Scarp `v0.0.6-alpha.2` में कोड को **बिना चलाए** किसी नाम की घोषणा (definition) और उसके प्रयोग (reference) देख सकते हैं। इसे *स्थिर स्रोत निरीक्षण* कहते हैं। यह अभी पूरा Language Server (LSP), स्वचालित rename या संपादन के बीच पहचान बनाए रखने वाला सिस्टम **नहीं** है।

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

[English tutorial](../source-navigation.md) · [आधिकारिक कम्पाइलर अनुबंध](https://github.com/scarp-lang/scarp/blob/v0.0.6-alpha.2/docs/symbol-index.md)

## अगला अभ्यास: एक ही नाम के दो अलग बाइंडिंग

[दो-मॉड्यूल source-navigation वर्कशॉप](../../tutorials/source-navigation/README.md) और इसका [वेबसाइट पृष्ठ](https://scarp-lang.github.io/scarp-by-example/projects/source-navigation/) देखें। यह प्रकाशित alpha.6 कम्पाइलर के उदाहरण से बनाया गया है और वास्तविक आउटपुट `30` है।

```sh
scarp verify tutorials/source-navigation
scarp inspect symbols --json tutorials/source-navigation
scarp inspect references --json tutorials/source-navigation
scarp inspect references --json tutorials/source-navigation/src/main.srp
scarp launch tutorials/source-navigation
```

इस प्रोजेक्ट में `base` की **दो घोषणाएँ** हैं। अंदर वाले `base` का initializer बाहर वाले `base` को पढ़ता है; `total += base` अंदर वाले नाम का उपयोग करता है। `value:` नाम `twice` के पैरामीटर से और `n:` नाम दूसरे मॉड्यूल के `adjust` पैरामीटर से जुड़ा है। `private_seed` निजी घोषणा है।

**अभ्यास:** दोनों `base` का declaration और reference खोजें; `launch` चलाने से पहले आउटपुट का अनुमान लगाएँ। CI में वास्तविक कम्पाइलर से span और पहचान की जाँच होती है; वेबसाइट पर JSON का नकली परिणाम या Scarp execution नहीं दिखाया जाता।

### वेबसाइट पर घोषणाओं से प्रयोगों तक जाएँ

[वर्कशॉप के क्लिक करने योग्य सोर्स एक्सप्लोरर](https://scarp-lang.github.io/scarp-by-example/projects/source-navigation/) में **11 घोषणाएँ और 20 उपयोग** चुन सकते हैं। बाहर और अंदर वाले `base` को अलग-अलग चुनें: उनके हाइलाइट किए गए प्रयोग अलग हैं। Keyboard से लिंक खोल सकते हैं; JavaScript बंद होने पर भी लिंक सीधे व्याख्या तक पहुँचाते हैं। यह प्रकाशित alpha.6 कम्पाइलर से CI में सत्यापित शिक्षण-मानचित्र है, लाइव compiler या editor नहीं। वेबसाइट किसी Scarp कोड को चलाती नहीं है।
