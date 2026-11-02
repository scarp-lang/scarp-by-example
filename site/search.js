// Progressive enhancement: every lesson remains readable without JavaScript.
(() => {
  const search = document.querySelector("#search");
  const status = document.querySelector("#search-status");
  const lessons = [...document.querySelectorAll(".lesson")];
  const sections = [...document.querySelectorAll(".section")];
  if (!search || !status) return;

  const update = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let shown = 0;
    for (const lesson of lessons) {
      const matches = lesson.dataset.search.includes(query);
      lesson.hidden = !matches;
      if (matches) shown += 1;
    }
    for (const section of sections) {
      section.hidden = !section.querySelector(".lesson:not([hidden])");
    }
    status.textContent = query
      ? `Showing ${shown} of ${lessons.length} lessons.`
      : `Showing all ${lessons.length} lessons.`;
  };
  search.addEventListener("input", update);
})();
