const renders = [
  { title: "Hero entry reveal", file: "01_hero_entry_reveal.png", note: "24 mm establishing view from the apartment entry" },
  { title: "Cooking & oven zone", file: "demo_cooking.png", note: "induction hob, box hood, oven column" },
  { title: "Breakfast dining", file: "demo_dining.png", note: "glazing, pendants, pulled-out chair" },
  { title: "Articulated storage open", file: "demo_interactions.png", note: "fridge, tall cabinet, interiors visible" },
  { title: "Walk-in pantry", file: "demo_pantry.png", note: "shelving, jars, toaster, drawers" },
];

const grid = document.querySelector("#render-grid");
renders.forEach((r, index) => {
  const card = document.createElement("figure");
  card.className = "render-card";
  card.innerHTML = `
    <img src="images/${r.file}" alt="${r.title}" loading="lazy">
    <figcaption>
      <span class="render-index">${String(index + 1).padStart(2, "0")}</span>
      ${r.title} — ${r.note}
    </figcaption>
  `;
  grid.appendChild(card);
});
