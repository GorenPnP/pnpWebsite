// init sizes
GRID_HEIGHT = parseInt((document.querySelector("[name=height]") as HTMLInputElement).value);
GRID_WIDTH = parseInt((document.querySelector("[name=width]") as HTMLInputElement).value);
document.querySelector("body")?.style.setProperty("--tile-size", `${TILE_SIZE}px`);

// init grid & tiles
const grid = new Grid();
grid.draw_empty_grid();

const tiles = JSON.parse(document.querySelector("#game")?.innerHTML || "[]");
for (const tile of tiles) {
    grid.createTile(tile.type, tile.pos, tile.stufe, tile.connective_tags, tile.converter_config);
}


// init toolbar
const tb = new Toolbar();



/**** EVENT LISTENERS *****/

(document.querySelector("#form") as any).onsubmit = (event: SubmitEvent) => grid.save(event);


// change cursor when hovering over clickable tile
canvas.onpointermove = function ({x, y}) {
    const {x: offsetX, y: offsetY} = canvas.getBoundingClientRect();
    x = Math.floor((x-offsetX) / TILE_SIZE);
    y = Math.floor((y-offsetY) / TILE_SIZE);
    // const tile = grid.get(x, y);

};

// click clickable tiles
canvas.onclick = function ({x, y}) {
    const {x: offsetX, y: offsetY} = canvas.getBoundingClientRect();
    x = Math.floor((x-offsetX) / TILE_SIZE);
    y = Math.floor((y-offsetY) / TILE_SIZE);
    const tile = grid.get(x, y);

    if (tile) { grid.clear({x, y}); }
    else { grid.createTile(tb.active, {x, y}); }
};


document.querySelector<HTMLInputElement>("[name=width]")!.addEventListener("change", function() {
    GRID_WIDTH = parseInt(this.value);
    grid.set_dimensions(GRID_WIDTH, GRID_HEIGHT);
});
document.querySelector<HTMLInputElement>("[name=height]")!.addEventListener("change", function() {
    GRID_HEIGHT = parseInt(this.value);
    grid.set_dimensions(GRID_WIDTH, GRID_HEIGHT);
});