# Scarp alpha.20 — सटीक Decimal और Tuple

[English tutorial](../../tutorials/alpha20-exact-values/README.md)

इस अभ्यास के लिए प्रकाशित Scarp v0.0.6-alpha.20 का उपयोग करें। मुख्य पाठ्यक्रम अभी alpha.19 पर है।

## Decimal

`0.1d` और `0.2d` का प्रकार decimal है। उनका योग ठीक 0.3 होता है। बिना d वाले 0.1 और 0.2 float हैं और उनका प्रतिनिधित्व binary64 में होता है। दोनों प्रकार स्वतः एक दूसरे में परिवर्तित नहीं होते।

[Decimal literals](../../tutorials/alpha20-exact-values/decimal_literals.srp) चलाकर [आउटपुट](../../tutorials/alpha20-exact-values/decimal_literals.stdout) से तुलना करें। `decimal_format` प्रदर्शित दशमलव अंकों को नियंत्रित करता है; यह मूल संख्या की type नहीं बदलता। Decimal की सीमा भी निश्चित है।

**अभ्यास:** 0d से शुरू करके 0.1d तीन बार जोड़ें। उत्तर का अनुमान पहले लगाएँ।

## Tuple

[Tuple snapshots](../../tutorials/alpha20-exact-values/tuple_snapshots.srp) में reading को var से घोषित किया गया है। उसका पहला सदस्य बदलने पर original का पुराना मान नहीं बदलता। bind से घोषित tuple पर indexed assignment मान्य नहीं है। Index एक वैध पूर्णांक literal होना चाहिए और नया सदस्य उसी प्रकार का होना चाहिए।

**अभ्यास:** (1, 90) और (2, 0) में तुलना पहले सदस्य से तय होती है। दोनों के दूसरे सदस्य की तुलना करना आवश्यक नहीं है।

[Tuple ordering](../../tutorials/alpha20-exact-values/tuple_ordering.srp) में nested numeric tuple भी दिखाए गए हैं। सभी प्रकार के tuples की तुलना संभव है, ऐसा नहीं मानना चाहिए।

## चलाना

~~~sh
scarp version
scarp verify tutorials/alpha20-exact-values/tuple_snapshots.srp
scarp exec tutorials/alpha20-exact-values/tuple_snapshots.srp
~~~

गलत उदाहरण अलग फाइल में बनाएँ: bind पर assignment, सीमा से बाहर index और decimal के साथ float जोड़ना। उन्हें compiler द्वारा अस्वीकार होना चाहिए।

यह workshop interpreter के लिए है, native compilation CLI के लिए नहीं।
