# Scarp alpha.15: फ़ाइल सीमा और UTF-8 string की तुलना

**प्रकाशित संस्करण:** [Scarp v0.0.6-alpha.15](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.15)
(19 नवंबर 2026, commit `a21b7b6d942bd1ca9abbbbb522f92f9c8e21e281`)।
यह स्थानीय अभ्यास है; वेबसाइट पर Scarp कोड चलाने का दावा नहीं है।

## 1. वास्तविक Scarp उदाहरण

[स्रोत](../../tutorials/alpha15-limits/string-comparisons.srp) में
दो हिन्दी strings की तुलना की गई है।
[आउटपुट फ़ाइल](../../tutorials/alpha15-limits/string-comparisons.stdout)
में `true` की दो पंक्तियाँ हैं।

```sh
scarp verify tutorials/alpha15-limits/string-comparisons.srp
scarp exec tutorials/alpha15-limits/string-comparisons.srp
```

`verify` स्थैतिक जाँच करता है; `exec` interpreter में चलाता है।
बराबर **UTF-8 byte length** वाली strings की तुलना में alpha.15
प्रत्येक शुरू हुए 64 bytes पर एक अतिरिक्त work step गिनता है।
एक हिन्दी अक्षर कई UTF-8 bytes ले सकता है; सीमा अक्षरों की संख्या से
न निकालें।

## 2. 1 MiB निरीक्षण सीमा

`scarp inspect tokens FILE`, `scarp inspect ast FILE` और पुराने
`scarp tokens FILE` कमांड केवल स्रोत पढ़ते हैं।
**1 MiB = 1,048,576 bytes** तक की फ़ाइल स्वीकार होती है;
एक अतिरिक्त byte होने पर फ़ाइल अस्वीकार होती है।

```sh
python scripts/verify_alpha15_limits.py --compiler /path/to/scarp --compiler-source /path/to/alpha15-checkout
```

स्क्रिप्ट प्रकाशित version और commit, अस्थायी फ़ाइलों की दोनों सीमाएँ,
और 129-byte तुलना को जाँचती है। उस **खास परीक्षण** में
`--max-steps 12` पर E0017 और `--max-steps 13` पर सफलता मिलती है;
यह सभी प्रोग्रामों के लिए 13-step सीमा नहीं है।
सामान्य `scarp compile` native-executable CLI उपलब्ध नहीं है।

[English guide](../../tutorials/alpha15-limits/README.md) ·
[मुख्य पाठ्यक्रम](README.md)
