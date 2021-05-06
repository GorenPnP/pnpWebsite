const tile_size = 64;
let field_tag;
let char_layer_tag;

let layers = [];
let materials = [];

let max_field_pos = {x: -1, y: -1};

document.addEventListener("DOMContentLoaded", () => {
    field_tag = document.querySelector(".field");

    layers = JSON.parse(document.querySelector("#layers").innerHTML);
    materials = JSON.parse(document.querySelector("#materials").innerHTML);

    update_layer_dimensions();

    layers.forEach(layer => paint_layer(layer));
});

function update_layer_dimensions() {
    max_field_pos = layers.reduce((acc, layer) => {

        // get maximum of one layer
        const max_pos = { y: layer.field.length - 1 };
        max_pos.x = layer.field.reduce((max_x, row) => Math.max(max_x, row.length - 1), -1);

        // merge
        acc.x = Math.max(acc.x, max_pos.x);
        acc.y = Math.max(acc.y, max_pos.y);
        return acc;
    }, {x: -1, y: -1});
}

function paint_layer(layer) {
    // init canvas
    const canvas = document.querySelector(`.field-container--${layer.index}`);
    update_canvas_dimensions_of(canvas);

    const ctx = canvas.getContext("2d");

    // paint materials on it
    layer.field.forEach((row, y) => row.forEach((cell, x) => {
        if (!cell) {
            // ctx.fillStyle = `rgb(${Math.round(Math.random() * 255)},0,0)`;
            // ctx.fillRect(x * tile_size, y * tile_size, tile_size, tile_size);
            return;
        }
        const img = new Image();
        img.onload = () => {
            ctx.drawImage(img, 0, 0, img.naturalWidth, img.naturalHeight, x * tile_size, y * tile_size, tile_size, tile_size);
        }
        img.src = materials.find(material => material.id === cell).icon;
    }));
}

function update_canvas_dimensions_of(canvas) {
    const width = Math.min(field_tag.offsetWidth, (max_field_pos.x + 1) * tile_size);
    const height = Math.min(field_tag.offsetHeight, (max_field_pos.y + 1) * tile_size);
    canvas.height = height;
    canvas.width = width;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
}