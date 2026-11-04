/* Tiny, dependency-free self-check. Uses only authored, fixture-validated answers.
   Does not execute Scarp, contact a server, store scores, or modify lesson progress. */
(() => {
  "use strict";

  for (const card of document.querySelectorAll("[data-checkpoint]")) {
    const form = card.querySelector("[data-checkpoint-form]");
    const interactive = card.querySelector("[data-checkpoint-interactive]");
    const fallback = card.querySelector("[data-checkpoint-fallback]");
    const feedback = card.querySelector("[data-checkpoint-feedback]");
    const explanation = card.querySelector("[data-checkpoint-explanation]");
    const expected = card.dataset.checkpointAnswer;

    // Never hide the readable <details> answer unless every control can work.
    if (!form || !interactive || !fallback || !feedback || !explanation ||
        !/^[0-2]$/.test(expected)) continue;

    form.addEventListener("submit", event => {
      event.preventDefault();
      const selected = form.querySelector('input[name="checkpoint-choice"]:checked');
      if (!selected) {
        feedback.textContent = "Choose an answer first. / पहले एक उत्तर चुनें।";
        explanation.hidden = true;
        return;
      }
      const correct = selected.value === expected;
      feedback.textContent = correct
        ? "Correct! / सही उत्तर!"
        : "Not quite. Read the explanation and try again. / अभी सही नहीं। व्याख्या पढ़कर फिर प्रयास करें।";
      explanation.hidden = false;
    });

    form.addEventListener("reset", () => {
      feedback.textContent = "";
      explanation.hidden = true;
    });

    interactive.hidden = false;
    fallback.hidden = true;
  }
})();
