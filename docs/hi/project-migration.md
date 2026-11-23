# Scarp प्रोजेक्ट माइग्रेशन: `Scarp.project` से `scarp.project`

Scarp के प्रकाशित कम्पाइलर में दो अलग project manifest format हैं।
**पुराना v1**: `Scarp.project`, जो `scarp create` से बनता है।
**नया v2**: `scarp.project`, जो `scarp init` से बनता है।
नया प्रोजेक्ट बनाते समय v2 चुनें।

[दो वास्तविक प्रोजेक्ट](../../tutorials/project-migration/README.md) ·
[English guide](../project-migration.md) ·
[आधुनिक प्रोजेक्ट का परिचय](declarative-projects.md)

## पहले और बाद का मैनिफ़ेस्ट

पुराने `Scarp.project` में केवल तीन पंक्तियाँ:

```text
scarp-project: 1
name: project-migration
entry: src/main.srp
```

नए `scarp.project` में घोषणात्मक प्रारूप:

```text
project "project-migration" {
    version: "0.1.0"
    entry: "src/main.srp"
    type: "application"
    dependencies {}
}
```

यह TOML या JSON नहीं है। `dependencies {}` अभी package
डाउनलोड नहीं करता। **सिर्फ़ बड़े `S` को छोटे `s` में बदलने
से पुराना format v2 नहीं बनता।** नई फ़ाइल का content भी
बदलना ज़रूरी है।

## असली कम्पाइलर पर दोनों प्रोजेक्ट चलाएँ

कोर्स की मूल डायरेक्टरी से:

```sh
scarp verify tutorials/project-migration/legacy
scarp verify tutorials/project-migration/modern
scarp run tutorials/project-migration/legacy
scarp run tutorials/project-migration/modern
```

`verify` प्रोग्राम चलाए बिना उसकी जाँच करता है।
दोनों `run` का सटीक आउटपुट है:

```text
Migrated: 42
```

दोनों जगह `src/main.srp`, imported math मॉड्यूल,
टेस्ट और आउटपुट की बाइट्स बिल्कुल समान हैं। सिर्फ़
मैनिफ़ेस्ट अलग है। इससे यह पता चलता है कि बदलाव
के बाद प्रोग्राम का व्यवहार नहीं बदला।

## JSON से सही format पहचानें

```sh
scarp project info --json tutorials/project-migration/legacy
scarp project info --json tutorials/project-migration/modern
```

पहले में `"format": "legacy-v1"` और
`"version": null` मिलेगा। दूसरे में
`"format": "v2"` और `"version": "0.1.0"`।
JSON रिपोर्ट का `schema_version` 1 दोनों में हो सकता है;
यह project manifest के format से अलग चीज़ है।

## दोनों टेस्ट की पुष्टि करें

```sh
scarp test --list --json tutorials/project-migration/legacy
scarp test --require-tests --json tutorials/project-migration/legacy
scarp test --list --json tutorials/project-migration/modern
scarp test --require-tests --json tutorials/project-migration/modern
```

पहला कमांड बिना टेस्ट चलाए सूची दिखाता है। दूसरा
दोनों टेस्ट चलाता है। अपेक्षित परिणाम **2 passed, 0 failed**
है। दूसरे टेस्ट को उसकी `02-input.stdin` फ़ाइल से
19 और 23 मिलते हैं; टर्मिनल से इनपुट नहीं लेना पड़ता।

## अपने प्रोजेक्ट का सुरक्षित माइग्रेशन

1. पुराने प्रोजेक्ट का backup या नई Git branch बनाएँ।
2. शुरुआत में `src/`, `tests/` और imports वैसे ही रखें।
3. नया lowercase `scarp.project` v2 syntax में लिखें।
4. पुराने और नए नाम की दोनों फाइलें साथ न रखें;
   कुछ सिस्टम में दोनों एक ही फ़ाइल मानी जाएँगी।
5. `project info --json` में `"format": "v2"` की जाँच करें।
6. `verify`, `run` और `test --require-tests` चलाएँ।
7. सबके परिणाम मिलने के बाद ही नई सुविधाएँ जोड़ें।

**गलत माइग्रेशन का प्रयोग:** 
[verifier](../../scripts/verify_project_migration.py) एक
अस्थायी कॉपी में नाम मात्र बदलने और जानबूझकर फेल
किए गए टेस्ट की जाँच करता है। मूल कोर्स फ़ाइलों
को नहीं बदलता। `scarp test --json=v2` failure
को structured runtime diagnostic के रूप में दिखाता है।

यह अभी native executable compiler या package
registry नहीं है। वास्तविक dependency installation
और browser में Scarp code चलना इन उदाहरणों में
समर्थित नहीं माना गया है।
