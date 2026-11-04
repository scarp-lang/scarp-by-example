# Bilingual practice checkpoint authoring

Scarp by Example uses curated, optional multiple-choice **comprehension checks**
alongside its verified executable lessons. A checkpoint is **not** a new `.srp`
file, a compiler test, or an in-browser Scarp interpreter.

## Source of truth

Questions live in [`practice-questions.json`](practice-questions.json).
The site builder runs `scripts/practice_questions.py` to reject questions
that do not match the checked-in course inventory and `.stdout` fixture.

Each entry requires:

- `source`: the exact existing numbered `examples/.../*.srp` path.
- `evidence_line`: one complete line appearing *verbatim* in the matching
  `.stdout` fixture, without the trailing newline.
- `question`: an object with nonempty `en` and `hi` strings.
- `options`: exactly three distinct bilingual choices.
- `correct`: zero-based index of the correct choice; its English text must
  appear in `evidence_line`.
- `explanation`: an accurate, concise English and Hindi explanation
  grounded in the source program and the expected result.

There is currently one question in each of the six chapters; add any new
question only after inspecting its real Scarp source, supporting modules, and
fixture. A matching fixture is necessary but **not sufficient** evidence that a
question is well written: review distractors, explanation, and Hindi translation
manually. Avoid ambiguous wording and questions depending on undocumented
syntax. Do not add questions for proposed compiler capabilities.

## Browser behavior

JavaScript enables radio choices, instant correct/incorrect feedback and
showing the explanation. The existing lesson language switch updates question,
options and explanations. Feedback is bilingual. Press **Try again** to reset
the answer; no answer history or score is saved, transmitted, or included in the
separate lesson-completion backup.

Without JavaScript, the authored question and an expandable answer with
explanation remain readable. There is no fake execution or grading by a remote
service. Completing a checkpoint never automatically marks a lesson complete.

## Review checklist

1. Verify source and expected stdout against the **exact pinned published
   Scarp compiler revision** before changing `evidence_line`.
2. Confirm all three options are distinct, only one answer actually addresses
   the question, and both explanations are correct.
3. Confirm both translations are understandable; do not translate Scarp syntax,
   path names, function names or exact compiler output.
4. Run `python -m unittest discover -s scripts -p "test_*.py"` and
   `node --test site/test_checkpoint.cjs`.
5. Run `python scripts/build_site.py --output dist`, inspect both language
   variants, and confirm the no-JavaScript answer disclosure remains readable.
6. Require the existing compiler/CLI and Pages CI workflows to pass before
   merging. Course prereleases are independent from compiler prereleases.

## Limits

A matching fixture line does not prove every interpretation in the explanation:
the review must also check the source implementation. This first set contains
**six** reviewed questions, not one automatically generated quiz for each of
the 50 lessons. Further chapters or questions require matching real examples
and review, not copied filler.
