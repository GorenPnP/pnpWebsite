let char_canvas;

const MovementDirections = {
    "ArrowLeft": {x: -1, y: 0, img: "/static/res/img/mining/char_skin_left.png"},
    "ArrowRight": {x: 1, y: 0, img: "/static/res/img/mining/char_skin_right.png"},
    "ArrowUp": {x: 0, y: -1, img: "/static/res/img/mining/char_skin_front.png"},
    "ArrowDown": {x: 0, y: 1, img: "/static/res/img/mining/char_skin_back.png"},
    " ": {x: 0, y: -1, img: "/static/res/img/mining/char_skin_front.png"}
}
let current_movement = {x: 0, y: 0, img: ""};

document.addEventListener("DOMContentLoaded", () => {
    char_canvas = document.querySelector(`.field-container--char`);
    document.addEventListener('keydown', e => {
        const movement = MovementDirections[e.key];
        if (movement) {

            // merge them
            current_movement = {
                x: current_movement.x + movement.x,
                y: current_movement.y + movement.y,
                img: movement.img
            };

            move();
        }
    });
    document.addEventListener('keyup', e => {
        const movement = MovementDirections[e.key];
        if (movement) {

            // merge them
            current_movement = {
                x: current_movement.x - movement.x,
                y: current_movement.y - movement.y,
                img: movement.img
            };
            move();
        }
    });

    spawn_char();
});

function spawn_char() {
    // init canvas
    update_canvas_dimensions_of(char_canvas);

    const ctx = char_canvas.getContext("2d");

    // draw char on it
    const img = new Image();
    img.onload = () => {
        const spawn = JSON.parse(document.querySelector("#spawn-point").innerHTML);
        ctx.drawImage(img, 0, 0, img.naturalWidth, img.naturalHeight, spawn.x * tile_size, spawn.y * tile_size, tile_size, tile_size);
    }
    img.src = "/static/res/img/mining/char_skin_front.png";
}

function move() {
    console.log(current_movement)
    if (!current_movement) { return; }
    
    current_movement = normalize_vector(current_movement);

}

function normalize_vector(vec) {
    return {
        ...vec,
        x: Math.max(-1, Math.min(1, vec.x)),
        y: Math.max(-1, Math.min(1, vec.y)),
    }
}