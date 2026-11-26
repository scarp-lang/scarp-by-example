# Scarp v0.0.7-alpha.1 — संख्यात्मक प्रोग्रामिंग

यह स्वतंत्र कार्यशाला प्रकाशित [Scarp v0.0.7-alpha.1](https://github.com/scarp-lang/scarp/releases/tag/v0.0.7-alpha.1) और स्रोत कमिट `996bd5b83c8cb26e98637563729f67bdacc61cd4` के लिए है। मुख्य पाठ्यक्रम और पुराने पाठ अपने अलग संस्करणों पर बने रहते हैं।

## 1. फिक्स्ड ऐरे जोड़ना

[array_concat.srp](../../tutorials/alpha7-numerical/array_concat.srp) में दो-दो पूर्णांकों के ऐरे से चार पूर्णांकों का नया ऐरे बनता है। दोनों मूल ऐरे सुरक्षित रहते हैं। खाली, निश्चित प्रकार वाला ऐरे जोड़ने पर मान नहीं बदलते। दोनों ऐरे के सदस्य का प्रकार समान होना चाहिए।

**अभ्यास:** पहले ऐरे में दो नए मान डालें। आउटपुट की पाँचों पंक्तियों का अनुमान लगाएँ। [अपेक्षित आउटपुट](../../tutorials/alpha7-numerical/array_concat.stdout) देखें।

## 2. महत्तम समापवर्तक और लघुत्तम समापवर्त्य

[integer_reductions.srp](../../tutorials/alpha7-numerical/integer_reductions.srp) में 18, 30 और 42 का GCD/HCF 6 है। 3, 5 और 8 का LCM 120 है। ऋणात्मक मान और शून्य के उदाहरण भी हैं। ये फ़ंक्शन इस रिलीज़ में 2 से 1024 पूर्णांक स्वीकार करते हैं; ये BigInt का विकल्प नहीं हैं।

**अभ्यास:** 6, 10 और 15 का GCD तथा LCM निकालें। [अपेक्षित आउटपुट](../../tutorials/alpha7-numerical/integer_reductions.stdout) से मूल उदाहरण जाँचें।

## 3. स्थिर softplus

[stable_softplus.srp](../../tutorials/alpha7-numerical/stable_softplus.srp) में softplus हर स्कोर पर अलग लागू होता है। बड़ा धनात्मक स्कोर लगभग अपने बराबर परिणाम देता है और बड़ा ऋणात्मक स्कोर शून्य के बहुत करीब पहुँचता है। शून्य पर परिणाम log(2) के करीब है; इसलिए दो असमानताओं से जाँच की गई है। यह मॉडल ट्रेनिंग नहीं है।

**अभ्यास:** दोनों स्कोर में किसका परिणाम अधिक होगा? [अपेक्षित आउटपुट](../../tutorials/alpha7-numerical/stable_softplus.stdout) देखें।

## अपने कंप्यूटर पर चलाएँ

~~~sh
scarp version
scarp verify tutorials/alpha7-numerical/array_concat.srp
scarp exec tutorials/alpha7-numerical/array_concat.srp
~~~

सही संस्करण इस्तेमाल करें। वेबसाइट कोड चलाने वाला ब्राउज़र इंटरप्रेटर नहीं है। Native ELF64 API प्रयोगात्मक Rust-host सुविधा है; यह नया Scarp CLI compilation command नहीं है।

[English guide](../../tutorials/alpha7-numerical/README.md)
