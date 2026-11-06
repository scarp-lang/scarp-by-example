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
    const matched = normalizeDisplay(prediction.value) ===
      normalizeDisplay(expected.textContent);
    feedback.textContent = matched
      ? "Your prediction matches the displayed verified output. / आपका अनुमान सही है।"
      : "The text does not match the displayed output yet. Reveal it to compare. / उत्तर देखकर मिलान करें।";
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
