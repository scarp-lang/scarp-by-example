# Input and tuples with published Scarp alpha.6

This optional workshop uses Scarp v0.0.6-alpha.6 from source
`cdf6a3924ec2a36c7beca5a9aec4f01a0bce515e`. Its compiler target is recorded
alongside the lesson. The numbered course has its own
[compatibility target](../../docs/compatibility.md).
[Published compiler release](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.6)

## Read two lines and return a tuple

`main.srp` reads a name and an integer from two UTF-8 input lines.
`text_trim` removes surrounding whitespace. `text_to_integer` parses the
second line explicitly. The pure `profile` function returns a
`tuple<string, integer>`, and the literal index `[1]` selects its score.

Run these commands from the repository root with the alpha.6 compiler.

```sh
scarp verify tutorials/input-and-tuples/main.srp
scarp exec tutorials/input-and-tuples/main.srp < tutorials/input-and-tuples/main.stdin
```

The first command checks source without consuming input. The second reads the
checked-in fixture and produces the exact bytes in `main.stdout`.

```text
Profile
("संस्कार 🌍", 42)
अंक: 42
```

Alpha.6 reads redirected or piped input. Its runtime buffers program output
until computation succeeds. Even the earlier `Profile` line is withheld if
the first input read reaches EOF, which reports E0055. Try removing the second
input line, then restore the fixture before committing. The host controls
reader readiness and elapsed-time deadlines.

To verify the workshop on Windows, Linux or macOS, build the pinned source
and run the same Python verifier used in CI.

```sh
python scripts/verify_alpha6_workshop.py --compiler /path/to/scarp --compiler-source /path/to/scarp-checkout
```

The verifier checks the source SHA and executable version, compares stdout
byte for byte, and checks that EOF suppresses queued program output.

## हिन्दी अभ्यास

यह अलग कार्यशाला प्रकाशित Scarp v0.0.6-alpha.6 पर चलती है। पहले
`main.stdin` और `main.srp` खोलें। पहली पंक्ति नाम है और दूसरी अंक हैं।
`read_line()` एक पंक्ति पढ़ता है, `text_trim` किनारों की खाली जगह हटाता
है और `text_to_integer` लिखे हुए अंक को integer में बदलता है।

`profile` नाम और अंक को एक immutable tuple में लौटाता है। `result[1]`
से दूसरा सदस्य मिलता है क्योंकि गिनती शून्य से शुरू होती है। इनपुट में नाम
और अंक बदलकर परिणाम देखें। उसके बाद input और stdout fixtures वापस रखें।
सफल गणना के बाद आउटपुट दिखता है। इनपुट समाप्त होने की त्रुटि आने पर पहले
लिखी गई `Profile` पंक्ति भी बाहर नहीं आती।
