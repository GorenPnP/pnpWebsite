let char;
let max_pos;

let pressed_keys = [];

document.addEventListener("DOMContentLoaded", () => {
    char = {tag: document.querySelector("#char"), pos: {x: 0, y: 0}};
    max_pos = {
        x: parseInt(document.querySelector("#width").innerHTML) - 1,
        y: parseInt(document.querySelector("#height").innerHTML) - 1
    }

    document.addEventListener("mousemove", e => {
        const cell = e.target.closest(".cell");
    });

    // setup keys to fire once on press
    document.addEventListener("keyup", e => {
        pressed_keys = pressed_keys.filter(key => key !== e.key);
    });
    document.addEventListener("keydown", e => {
        const key = e.key;

        if (pressed_keys.includes(key)) { return; }
        pressed_keys.push(key);

        const move_map = {
            ArrowUp: {x: 0, y: -1},
            ArrowDown: {x: 0, y: 1},
            ArrowLeft: {x: -1, y: 0},
            ArrowRight: {x: 1, y: 0},
            " ": {x: 0, y: -1}
        }

        const pos_offset = move_map[key];
        if (pos_offset) { move_char_to(char.pos.x + pos_offset.x, char.pos.y + pos_offset.y); }
    })

    prepopulate_field();
    spawn_char();
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

const field_size = 64;
function convert_to_char_game_coords(field_coord, max_field_coord, max_game_coord) {

    // central position
    const game_coord = Math.floor(max_game_coord / 2);

    // go low close enough to end to leave center position?
    if (field_coord <= game_coord) { return field_coord; }

    // go high close enough to end to leave center position?
    if (max_field_coord - field_coord <= game_coord) {
        return max_game_coord - (max_field_coord - field_coord);
    }

    return game_coord;
}

function move_char_to(field_x, field_y) {
    // stay in FIELD coordinates, not out of bounds
    field_x = Math.max(0, Math.min(field_x, max_pos.x));
    field_y = Math.max(0, Math.min(field_y, max_pos.y));
    
    // TODO can be done in main
    const game_height = document.querySelector(".field").offsetHeight;
    const game_width  = document.querySelector(".field").offsetWidth;
    
    
    // in GAME coordinates
    const game_x = convert_to_char_game_coords(field_x, max_pos.x, Math.floor(game_width / field_size) - 1);
    const game_y = convert_to_char_game_coords(field_y, max_pos.y, Math.floor(game_height / field_size) - 1);

    document.documentElement.style.setProperty("--field-offset-x", `calc(${game_x - field_x} * var(--field-size))`);
    document.documentElement.style.setProperty("--field-offset-y", `calc(${game_y - field_y} * var(--field-size))`);


    char.pos = {x: field_x, y: field_y};
    char.tag.parentNode.style.setProperty("--field-offset-x", `${game_x * field_size}px`);
    char.tag.parentNode.style.setProperty("--field-offset-y", `${game_y * field_size}px`);
}

function spawn_char() {
    const pos = JSON.parse(document.querySelector("#spawn-point").innerHTML);
    move_char_to(pos.x, pos.y);
}