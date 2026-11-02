# 04 · संख्यात्मक कलेक्शन (हिन्दी)

यह [अंग्रेज़ी अध्याय](../../examples/04-collections/README.md) का हिन्दी साथी है। Scarp स्रोत और आउटपुट मूल फ़ाइलों से साझा हैं; यहाँ काल्पनिक कोड नहीं दिया गया है।

वर्तमान Scarp कम्पाइलर में विशिष्ट संख्यात्मक `vector`, `integers` और `tile` हैं। इन्हें हर तरह का डेटा रखने वाले सामान्य `list`, `map` या `set` का विकल्प न समझें।

**वेक्टर** = संख्याओं का क्रम; **इंडेक्स** = शून्य से शुरू होने वाला स्थान; **विंडो** = वेक्टर का चुना गया हिस्सा; **टाइप एनोटेशन** = बाइंडिंग के साथ उसका अपेक्षित प्रकार।

**कैसे चलाएँ:** रिपॉज़िटरी की जड़ से `scarp check examples/04-collections/01-vectors.srp` और `scarp run examples/04-collections/01-vectors.srp`।

## पाठ

### 01 · वेक्टर और संख्यात्मक फ़ंक्शन

`len(values)` लंबाई और `values[0]` पहला मान देता है। `scale`, `sum`, `mean`, `dot`, `mse`, `clamp` और `fill` संख्यात्मक फ़ंक्शन हैं। स्केल किया गया नया `weights` पुराने `snapshot` से अलग है।

[Scarp स्रोत](../../examples/04-collections/01-vectors.srp) · [सटीक अपेक्षित आउटपुट](../../examples/04-collections/01-vectors.stdout)

**आउटपुट:** `sum(values)` = `10.0`, `mean(values)` = `2.5`। पूरा आठ-पंक्तियों वाला आउटपुट मूल फ़ाइल से मिलाएँ।

**अभ्यास:** पुराना `snapshot` `[0.2, 0.3, 0.5]` क्यों बना रहता है?

### 02 · वेक्टर विंडो

`window(values, 1, 2)` दूसरे स्थान से दो मान चुनता है। `stitch` उसके साथ नया वेक्टर जोड़ता है। शून्य लंबाई की विंडो खाली है।

[Scarp स्रोत](../../examples/04-collections/02-vector-windows.srp) · [सटीक अपेक्षित आउटपुट](../../examples/04-collections/02-vector-windows.stdout)

**आउटपुट:** `[20.0, 30.0]`, फिर `[20.0, 30.0, 50.0]`, फिर `[]`।

**अभ्यास:** विंडो में `10.0` क्यों नहीं आया?

### 03 · पूर्णांक कलेक्शन

`integers` पूर्णांकों का विशेष क्रम है। `ints_range`, `ints_window`, `ints_set`, `ints_len`, `ints_to_vector` तथा `ints_join` के साथ अलग-अलग गणनाएँ होती हैं। `repeat` से विंडो का योग निकाला गया है।

[Scarp स्रोत](../../examples/04-collections/03-integer-collections.srp) · [सटीक अपेक्षित आउटपुट](../../examples/04-collections/03-integer-collections.stdout)

**आउटपुट:** `values` में 1–5, बदले हुए क्रम में पहला मान 9, और विंडो का योग `9` है।

**अभ्यास:** `ints_set` नया क्रम देता है या मूल बाइंडिंग को बदलता है?

### 04 · टाइप एनोटेशन

`bind samples: vector`, `var total: float`, `bind grid: tile`, `bind ready: boolean` और `bind label: string` से प्रकार स्पष्ट होते हैं। `total` में बाद में `0.5` जुड़ता है।

[Scarp स्रोत](../../examples/04-collections/04-typed-declarations.srp) · [सटीक अपेक्षित आउटपुट](../../examples/04-collections/04-typed-declarations.stdout)

**आउटपुट:** `typed true 6.5`।

**अभ्यास:** `width(grid) == 3` बूलियन कैसे बनाता है?

## संगतता

इन पाठों का सिंटैक्स एक निश्चित विकास-चरण वाले कम्पाइलर से जाँचा जाता है। पुराने प्रीरिलीज़ का सिंटैक्स अलग हो सकता है। [संगतता नीति](../compatibility.md) देखें।

[हिन्दी सामग्री-सूची](README.md) · [मूल पाठ्यक्रम](../../README.md#course)
