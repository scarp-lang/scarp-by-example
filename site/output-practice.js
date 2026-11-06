// Progressive enhancement for predicting a lesson's compiler-verified stdout.
// This checks displayed text only; it NEVER executes Scarp or stores predictions.
(() => {
  "use strict";
  const practice = document.querySelector("[data-output-practice]");
  const output = document.querySelector("[data-verified-output]");
  const expected = output?.querySelector("code");
  if (!practice || !output || !expected) return;

  const start = practice.querySelector("[data-output-start]");
  const workspace = practice.querySelector("[data-output-workspace]");
  const prediction = practice.querySelector("[data-output-prediction]");
  const check = practice.querySelector("[data-output-check]");
  const toggle = practice.querySelector("[data-output-toggle]");
  const reset = practice.querySelector("[data-output-reset]");
  const feedback = practice.querySelector("[data-output-feedback]");
  if (![start, workspace, prediction, check, toggle, reset, feedback].every(Boolean)) return;

  // Browsers normalize textarea newlines to LF. Ignore exactly one terminal LF
  // so copying expected stdout from the rendered page does not require guessing
  // whether the compiler emitted its final newline.
  function normalizeDisplay(value) {
    return value.replace(/\r\n?/g, "\n").replace(/\n$/, "");
  }

  // Feedback reports where the mismatch begins without exposing the answer.
  // Compare only rendered text; the compiler and stdout fixtures are unchanged.
  function mismatchHint(entered, verified) {
    const written = entered.split("\n");
    const actual = verified.split("\n");
    const overlap = Math.min(written.length, actual.length);
    let index = 0;
    while (index < overlap && written[index] === actual[index]) index++;
    const line = index + 1;
    const location = "First difference at line " + line +
      ". / पहली अलग पंक्ति: " + line + "। ";
    if (written.length !== actual.length) {
      return location + "You entered " + written.length + " line" +
        (written.length === 1 ? "" : "s") + "; the verified output has " +
        actual.length + ". / पंक्तियों की संख्या अलग है।";
    }
    if (written[index].trim() === actual[index].trim()) {
      return location + "Check leading or trailing spaces. / शुरुआत या अंत के स्पेस जाँचें।";
    }
    if (written[index].toLocaleLowerCase() === actual[index].toLocaleLowerCase()) {
      return location + "Check capitalization. / बड़े-छोटे अक्षर जाँचें।";
    }
    return location + "Check the text, spaces, or punctuation. / अक्षर, स्पेस या विराम-चिह्न जाँचें।";
  }

  function showOutput(visible) {
    output.hidden = !visible;
    toggle.textContent = visible ? "Hide verified output" : "Reveal verified output";
    toggle.setAttribute("aria-expanded", String(visible));
  }

  start.addEventListener("click", () => {
    start.hidden = true;
    workspace.hidden = false;
    showOutput(false);
    feedback.textContent = "";
    prediction.focus();
  });

  check.addEventListener("click", () => {
    if (!prediction.value.trim()) {
      feedback.textContent = "Enter your predicted output first. / पहले अनुमान लिखें।";
      return;
    }
    const entered = normalizeDisplay(prediction.value);
    const verified = normalizeDisplay(expected.textContent);
    feedback.textContent = entered === verified
      ? "Your prediction matches the displayed verified output. / आपका अनुमान सही है।"
      : "Your prediction does not match the displayed output yet. " +
        mismatchHint(entered, verified) +
        " Reveal the verified output when ready. / तैयार होने पर उत्तर देखें।";
  });

  toggle.addEventListener("click", () => showOutput(output.hidden));

  reset.addEventListener("click", () => {
    prediction.value = "";
    feedback.textContent = "";
    workspace.hidden = true;
    start.hidden = false;
    showOutput(true);
  });

  // Expose controls only after every required element has been initialized.
  practice.hidden = false;
})();
