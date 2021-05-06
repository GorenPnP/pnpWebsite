let char;
let max_pos;

let pressed_keys = [];

let collision_map;

document.addEventListener("DOMContentLoaded", () => {
    char = {tag: document.querySelector("#char"), pos: {x: 0, y: 0}};
    max_pos = {
        x: parseInt(document.querySelector("#width").innerHTML) - 1,
        y: parseInt(document.querySelector("#height").innerHTML) - 1
    }

    // document.addEventListener("mousemove", e => {
    //     const cell = e.target.closest(".cell");
    // });

    // fill collision map
    init_collision_map();
    apply_lighting(1, 2, 2);

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
    });


    document.querySelector(".field-container--char").addEventListener('transitionend', e => {
        if (["top", "left"].includes(e.propertyName)) {
            document.documentElement.style.setProperty("--char-img", "var(--char-img-front)");
            move_char_to(char.pos.x, char.pos.y + 1);
        }
      });

    prepopulate_field();
    spawn_char();
});

function create_empty_map(value) {
    return Array.from({length: max_pos.y + 1}, () => Array.from({length: max_pos.x + 1}, () => { return JSON.parse(JSON.stringify(value)); }));
}

function init_collision_map() {
    collision_map = create_empty_map({});
    [...document.querySelectorAll(".field-container[data-collidable]")]
        .reduce((acc, layer) => {
            layer.querySelectorAll(".cell[data-material_id]").forEach(cell => {
                acc[cell.dataset.y_pos][cell.dataset.x_pos][layer.dataset.layer_index] = cell;
            });
            return acc;
        }, collision_map);
}

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

function apply_lighting(max_brightness, factor, max_depth) {

    // get list of collidable block positions for lighting
    const collision_pos = collision_map
        .reduce((acc, row) => [...(acc || []), ...row], [])
        .filter(cell => Object.keys(cell).length && Object.values(cell).length)
        .map(cell => {
            tag = Object.values(cell)[0];
            return {x: parseInt(tag.dataset.x_pos), y: parseInt(tag.dataset.y_pos)};
        });

    // compute lighting
    const lighting_map = apply_lighting_of(max_brightness, factor, max_depth, collision_pos);

    // apply lighting to those blocks
    lighting_map.forEach((row, y) => row.forEach((brightness, x) => {
        Object.values(collision_map[y][x]).forEach(cell_layer => cell_layer.style.filter = `brightness(${brightness})`)
    }));
}

function apply_lighting_of(brightness, factor, max_depth, collision_pos) {
    return _apply_lighting_of(brightness, factor, max_depth, collision_pos);
}

// internal use only! Don't call directly, use apply_lighting_of() instead!
function _apply_lighting_of(brightness, factor, max_depth, collision_pos, _lighting_map) {
    if (max_depth <= 0) { return _lighting_map; }

    // init map with brightness * 2 wherever air is 
    if (!_lighting_map) {
        _lighting_map = create_empty_map(brightness * factor);
        collision_pos.forEach(cell => _lighting_map[cell.y][cell.x] = 0);
        return _apply_lighting_of(brightness, factor, max_depth, collision_pos, _lighting_map);
    }

    // apply brightness if none set jet AND a neighboring cell was brighter
    collision_pos.forEach(cell => {

        const neighbors = get_neighbor_pos(cell.x, cell.y);
        if (!_lighting_map[cell.y][cell.x] && neighbors.some(pos => _lighting_map[pos.y][pos.x] === brightness * factor)) {
            _lighting_map[cell.y][cell.x] = brightness;
        }
    });

    return _apply_lighting_of(brightness / factor, factor, max_depth - 1, collision_pos, _lighting_map);
}

function get_neighbor_pos(x, y) {
    neighbors = [];
    for (let _x = x - 1; _x <= x + 1; _x++) {
        for (let _y = y - 1; _y <= y + 1; _y++) {
            neighbors.push({x: _x, y: _y});
        }
    }

    return neighbors.filter(pos => {
        if (pos.x === x && pos.y === y) { return false; }

        // in bounds of field?
        if (pos.x < 0 || pos.y < 0) { return false; }
        if (pos.x > max_pos.x || pos.y > max_pos.y) { return false; }
        return true;
    })
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

    // collision detection
    if (Object.keys(collision_map[field_y][field_x]).length) {
        // if moved in x direction: try to also move up
        if (field_x !== char.pos.x && field_y === char.pos.y) {
            move_char_to(field_x, char.pos.y - 1);
        }
        return;
    }
    
    // TODO can be done in main
    const game_height = document.querySelector(".field").offsetHeight;
    const game_width  = document.querySelector(".field").offsetWidth;
    
    
    // in GAME coordinates
    const game_x = convert_to_char_game_coords(field_x, max_pos.x, Math.floor(game_width / field_size) - 1);
    const game_y = convert_to_char_game_coords(field_y, max_pos.y, Math.floor(game_height / field_size) - 1);

    document.documentElement.style.setProperty("--field-offset-x", `calc(${game_x - field_x} * var(--field-size))`);
    document.documentElement.style.setProperty("--field-offset-y", `calc(${game_y - field_y} * var(--field-size))`);


    // css transitions
    if (char.pos.x < field_x) { document.documentElement.style.setProperty("--char-img", "var(--char-img-right)"); }
    if (char.pos.x > field_x) { document.documentElement.style.setProperty("--char-img", "var(--char-img-left)"); }
    if (char.pos.y < field_y) { document.documentElement.style.setProperty("--char-img", "var(--char-img-back)"); }
    if (char.pos.y > field_y) { document.documentElement.style.setProperty("--char-img", "var(--char-img-front)"); }

    // set pos
    char.pos = {x: field_x, y: field_y};
    char.tag.parentNode.style.setProperty("--field-offset-x", `${game_x * field_size}px`);
    char.tag.parentNode.style.setProperty("--field-offset-y", `${game_y * field_size}px`);
}

function spawn_char() {
    const pos = JSON.parse(document.querySelector("#spawn-point").innerHTML);
    move_char_to(pos.x, pos.y);
}