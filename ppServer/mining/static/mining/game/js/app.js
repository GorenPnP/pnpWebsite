const path_prefix = "/static/mining/game/";


// A cross-browser requestAnimationFrame
// See https://hacks.mozilla.org/2011/08/animating-with-javascript-from-setinterval-to-requestanimationframe/
const requestAnimFrame = (() => {
    return window.requestAnimationFrame    ||
        window.webkitRequestAnimationFrame ||
        window.mozRequestAnimationFrame    ||
        window.oRequestAnimationFrame      ||
        window.msRequestAnimationFrame     ||
        function (callback) {
            window.setTimeout(callback, 1000 / 60);
        };
})();

// Create the canvas
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");
let bg_color;

let materials;

// Game state
var player = {
    pos: [0, 0],
    speed: [0, 0],
    lastJump: Date.now(),
    spriteMap: {
        UP: new Sprite('/static/res/img/mining/char_skin_front.png', [0, 0], [64, 64]),
        DOWN: new Sprite('/static/res/img/mining/char_skin_back.png', [0, 0], [64, 64]),
        LEFT: new Sprite('/static/res/img/mining/char_skin_left.png', [0, 0], [64, 64]),
        RIGHT: new Sprite('/static/res/img/mining/char_skin_right.png', [0, 0], [64, 64])
    },
    sprite: new Sprite('/static/res/img/mining/char_skin_front.png', [0, 0], [64, 64]),
};

var explosions = [];

var entities = [];  // game logic, not for rendering directly
var collidables = [];

var lastJump = Date.now();

var gameTime = 0;
var lastTime;

// Speed in pixels per second
var playerFriction = .15;    // float in [0, 1] (slowing % per s)
var playerMaxSpeed = [2, 8];    // speed is already px/s, so on 'px per s' here :)
var playerXAcceleration = 3; // px per s
var playerFallAcceleration = 80; // px per s
var playerJumpAcceleration = 100; // px per s
var playerJumpDuration = 300;   // in ms


window.addEventListener("resize", () => setCanvasSize());


// startup
document.addEventListener("DOMContentLoaded", () => {
    const main_container = document.querySelector(".main-container");
    main_container.appendChild(canvas);
    setCanvasSize();

    bg_color = JSON.parse(document.querySelector("#bg-color").innerHTML);
    materials = JSON.parse(document.querySelector("#materials").innerHTML);

    resources.load(
        path_prefix + 'img/sprites.png',
        '/static/res/img/mining/char_skin_front.png',
        '/static/res/img/mining/char_skin_front.png',
        '/static/res/img/mining/char_skin_back.png',
        '/static/res/img/mining/char_skin_left.png',
        '/static/res/img/mining/char_skin_right.png',
        ...materials.map(material => material.icon));
    resources.onReady(init);
});

function setCanvasSize() {
    const main_container = document.querySelector(".main-container");

    canvas.width = main_container.offsetWidth;
    canvas.height = main_container.offsetHeight;
    canvas.style.width = `${main_container.offsetWidth}px`;
    canvas.style.height = `${main_container.offsetHeight}px`;
}

function init() {
    reset();
    lastTime = Date.now();
    main();
}

// The main game loop
function main() {
    var now = Date.now();
    var dt = (now - lastTime) / 1000.0;

    update(dt);
    render();

    lastTime = now;
    requestAnimFrame(main);
};


// Update game objects
function update(dt) {
    gameTime += dt;

    handleInput(dt);
    updateEntities(dt);

    checkCollisions();

    updatePlayerSprite();
};

function handleInput(dt) {

    if (( input.isDown('DOWN') && !input.isDown('UP')) ||
        (!input.isDown('DOWN') &&  input.isDown('UP'))) {
        
        // move/accelerate y
        if (input.isDown('DOWN') && !input.isDown('UP')) { player.speed[1] += playerFallAcceleration * dt; }
        const now = Date.now();
        if (input.isDown('UP') && !input.isDown('DOWN')) {
            // check if on ground
            if (player.speed[1] === 0) { lastJump = now; }
            
            // jump for x seconds
            if (lastJump === now || (lastJump + playerJumpDuration >= now && player.speed[1] < 0)) {
                player.speed[1] -= playerJumpAcceleration * dt;
            }
        }
    }

    if (( input.isDown('LEFT') &&  input.isDown('RIGHT')) ||
    (!input.isDown('LEFT') && !input.isDown('RIGHT'))) {
        
        // slow down x
        player.speed[0] *= (1 - playerFriction) * dt;
    } else {
        // move/accelerate x
        const accDiff = playerXAcceleration * dt;
        player.speed[0] += input.isDown('RIGHT') ? accDiff  : (-1 * accDiff);
    }

    // apply gravity
    player.speed[1] += playerFallAcceleration * dt;

    // not faster than max speed
    player.speed[0] = Math.min( Math.abs(player.speed[0]), playerMaxSpeed[0]) * Math.sign(player.speed[0]);
    player.speed[1] = Math.min( Math.abs(player.speed[1]), playerMaxSpeed[1]) * Math.sign(player.speed[1]);
}

function updateEntities(dt) {
    // Update the player sprite animation
    player.sprite.update(dt);

    // Update all non-player sprites
    [...explosions, ...entities].forEach(e => e.sprite.update(dt));

    // Remove explosions if animation is done
    explosions = explosions.filter(explosion => !explosion.sprite.done);
}

// Collisions

function collides(x, y, r, b, x2, y2, r2, b2) {
    return !(r <= x2 || x >= r2 ||
             b <= y2 || y >= b2);
}

function boxCollides(pos, size, pos2, size2) {
    return collides(pos[0], pos[1],
                    pos[0] + size[0], pos[1] + size[1],
                    pos2[0], pos2[1],
                    pos2[0] + size2[0], pos2[1] + size2[1]);
}

function checkCollisions() {

    let playerMovedXPos = [player.pos[0] + Math.round(player.speed[0]), player.pos[1]];
    let playerMovedYPos = [player.pos[0], player.pos[1] + Math.round(player.speed[1])];

    const playerSize = player.sprite.size;
    
    // Run collision detection for all enemies and bullets
    for(const collidable of collidables) {
        var pos = collidable.pos;
        var size = collidable.sprite.size;
        
        if (boxCollides(pos, size, player.pos, playerSize)) {
            
            // Add an explosion
            explosions.push({
                pos,
                sprite: new Sprite(path_prefix + 'img/sprites.png',
                [0, 117],
                [39, 39],
                16,
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                null,
                true)
            });
        }


        // resolve collisions
        // console.log(playerMovedYPos)
        
        // collide in x
        if (boxCollides(pos, size, playerMovedXPos, playerSize)) {
            while (boxCollides(pos, size, playerMovedXPos, playerSize) && player.speed[0]) {
                playerMovedXPos[0] -= Math.sign(player.speed[0]);
            }
            player.speed[0] = 0;
        }
        
        // collide in y
        if (boxCollides(pos, size, playerMovedYPos, playerSize)) {
            while (boxCollides(pos, size, playerMovedYPos, playerSize) && player.speed[1]) {
                playerMovedYPos[1] -= Math.sign(player.speed[1]);
            }
            player.speed[1] = 0;
        }

        player.pos[0] = Math.round(playerMovedXPos[0]);
        player.pos[1] = Math.round(playerMovedYPos[1]);
    }
    checkPlayerBounds();
}

function checkPlayerBounds() {
    // Check bounds
    max_right = canvas.width - player.sprite.size[0];
    max_down = canvas.height - player.sprite.size[1];

    player.pos[0] = Math.max(0, Math.min(player.pos[0], max_right));
    player.pos[1] = Math.max(0, Math.min(player.pos[1], max_down));

    // enable jumping from furthest buttom
    if (player.pos[1] === max_down && player.speed[1] > 0) { player.speed[1] = 0; }
}

// Draw everything
function render() {
    ctx.fillStyle = bg_color;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    renderEntities(collidables.filter(c => c.layer.index < 0));
    renderEntity(player);
    renderEntities(collidables.filter(c => c.layer.index >= 0));

    renderEntities(explosions);
}

function renderEntities(list) {
    for(const entity of list) { renderEntity(entity); }    
}

function renderEntity(entity) {
    ctx.save();
    ctx.translate(entity.pos[0], entity.pos[1]);
    entity.sprite.render(ctx);
    ctx.restore();
}

function updatePlayerSprite() {

    const limit = 0.25;
    const speed_x = Math.abs(player.speed[0]) < limit ? 0 : player.speed[0];
    const speed_y = Math.abs(player.speed[1]) < limit ? 0 : player.speed[1];

    // look in x
    if (Math.abs(speed_x) > Math.abs(speed_y)) {
        player.sprite = speed_x > 0 ? player.spriteMap.RIGHT : player.spriteMap.LEFT;
    }
    // look in y
    else {
        player.sprite = speed_y > 0 ? player.spriteMap.DOWN : player.spriteMap.UP;
    }
}


// Reset game to original state
function reset() {
    gameTime = 0;

    enemies = [];
    bullets = [];

    resetMap();

    const pos = JSON.parse(document.querySelector("#spawn-point").innerHTML);
    player.pos = [pos.x * 64, pos.y * 64];
}

function resetMap() {
    const layers = JSON.parse(document.querySelector("#layers").innerHTML).sort((a, b) => a.index - b.index);

    entities = [];

    for (const layer of layers) {
        const field = layer.field;

        for (let y = 0; y < field.length; y++) {
            for (let x = 0; x < field[y].length; x++) {
                const material_id = field[y][x];

                if (material_id) {
                    const sprite_url = materials.find(material => material.id === material_id).icon;
                    const pos = [x * 64, y * 64];

                    entities.push({
                        pos,
                        layer,
                        sprite: new Sprite(sprite_url, [0, 0], [64, 64])
                    });
                }
            }
        }
    }
    collidables = entities.filter(entity => entity.layer.is_collidable);
}
