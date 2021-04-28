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
        const material_id = cell.dataset.material_id;
        const url = material_id != -1 ? material_images[material_id] : "/static/res/img/mining/char_front.png";
        cell.style.backgroundImage = url ? `url(${url})` : "";
    });
}