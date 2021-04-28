document.addEventListener("DOMContentLoaded", () => {

    document.addEventListener("mousemove", e => {
        const cell = e.target.closest(".cell");
    });

    prepopulate_field();
});

function prepopulate_field() {
    const prepopulated_cells = [...document.querySelectorAll(".cell")].filter(cell => cell.hasAttribute("data-material_id"));
    const material_images = [...document.querySelectorAll(".material")]
        .reduce((acc, material) => {
            acc[material.dataset.id] = material.dataset.src || "";
            return acc;
        }, {});
    prepopulated_cells.forEach(cell => {
        const url = material_images[cell.dataset.material_id];
        cell.style.backgroundImage = url ? `url(${url})` : "";
    });
}