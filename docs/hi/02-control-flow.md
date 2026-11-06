# 02 · नियंत्रण प्रवाह (हिन्दी)

यह [अंग्रेज़ी नियंत्रण-प्रवाह अध्याय](../../examples/02-control-flow/README.md) का हिन्दी साथी है। स्रोत फ़ाइलें और अपेक्षित आउटपुट अंग्रेज़ी पाठ के समान हैं।

**चलाएँ:** `scarp exec examples/02-control-flow/01-decisions.srp`। स्थिर जाँच के लिए `scarp verify` चलाएँ। शर्तों में `true` या `false` जैसे बूलियन मान उपयोग होते हैं।

**मुख्य शब्द:** शर्त = किसी निर्णय का बूलियन प्रश्न; लूप = दोहराव; break = लूप समाप्त करना; continue = वर्तमान चक्कर का शेष भाग छोड़ना।

## पाठ

### 01 · if, elif, else

शर्तों की क्रम से जाँच की जाती है। score के आधार पर grade चुना जाता है; दूसरी शर्त में and है।

[Scarp स्रोत](../../examples/02-control-flow/01-decisions.srp) · [सटीक अपेक्षित आउटपुट](../../examples/02-control-flow/01-decisions.stdout)

**अभ्यास:** 73 अंकों के लिए कौन-सी शाखा चलेगी?

### 02 · while, break, continue

while लूप शर्त सही रहने तक चलता है। continue वर्तमान चक्कर का बाकी भाग छोड़ता है; break लूप से बाहर निकलता है।

[Scarp स्रोत](../../examples/02-control-flow/02-while-loops.srp) · [सटीक अपेक्षित आउटपुट](../../examples/02-control-flow/02-while-loops.stdout)

**अभ्यास:** कौन-से index total में जोड़े गए हैं?

### 03 · निश्चित गिनती वाला repeat

repeat count as index शुरुआत में गिनती तय कर लेता है। बाद में count को शून्य करने से चक्करों की पहले से तय संख्या नहीं बदलती।

[Scarp स्रोत](../../examples/02-control-flow/03-repeat.srp) · [सटीक अपेक्षित आउटपुट](../../examples/02-control-flow/03-repeat.stdout)

**अभ्यास:** index == 2 पर continue होने पर total क्या बनता है?

### 04 · नेस्टेड repeat और continue

बाहरी `repeat 4 as row` की हर पुनरावृत्ति में अंदर का `repeat 3 as column` चलता है। इस तरह 12 (row, column) जोड़ियाँ बनती हैं। `row == column` होने पर `continue` केवल अंदर वाले लूप के मौजूदा चक्कर को छोड़ता है। ऐसी तीन जोड़ियाँ हैं: (0, 0), (1, 1), (2, 2)। बाकी 9 जोड़ियों के row + column का योग 24 है।

[Scarp स्रोत](../../examples/02-control-flow/04-nested-repeat.srp) · [सटीक अपेक्षित आउटपुट](../../examples/02-control-flow/04-nested-repeat.stdout)

**अभ्यास:** अगर `repeat 3 as column` की संख्या 4 हो जाए, तो कितनी जोड़ियाँ और कितने `continue` होंगे? अनुमान लगाकर कंपाइलर से जाँचें।

## दोहराएँ

पहले शर्त या दोहराव की गिनती समझें। फिर `.stdout` से मिलाएँ। `repeat` में प्रारम्भिक गिनती सुरक्षित रहने की बात इसी कम्पाइलर के वर्तमान उदाहरण पर आधारित है; पुराने प्री-रिलीज़ अलग हो सकते हैं।

[हिन्दी सामग्री सूची](README.md) · [अंग्रेज़ी फ़ंक्शन अध्याय](../../examples/03-functions/README.md)
