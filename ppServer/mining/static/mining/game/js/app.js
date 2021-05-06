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
    direction: [0, 0],
    lastJump: Date.now(),
    hitGround: false,
    sprite: new Sprite('/static/res/img/mining/char_skin_front.png', [0, 0], [64, 64])
};

var explosions = [];

var entities = [];  // game logic, not for rendering directly
var collidables = [];

var lastFire = Date.now();
var gameTime = 0;

// Speed in pixels per second
var playerSpeed = 200;
var bulletSpeed = 500;
var enemySpeed = 100;

var lastTime;


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

    const playerPos1 = player.pos[1];

    checkCollisions();

    const playerPos2 = player.pos[1];
    player.hitGround = (playerPos1 > playerPos2 || player.hitGround === player.pos[1]) ? player.pos[1]: undefined;

    // if (player.direction[1] <= 0) {
    //     player.direction[1] = 1;
    //     player.pos[1] += playerSpeed * dt;
    //     checkCollisions();
    // }
};

function handleInput(dt) {
    player.direction = [0, 0];
    const unit = 1;

    if (input.isDown('DOWN') || input.isDown('s')) {
        player.pos[1] += playerSpeed * dt;
        player.direction[1] += unit;
    }

    if (input.isDown('UP') || input.isDown('w')) {
        player.pos[1] -= playerSpeed * dt;
        player.direction[1] -= unit;
    }
    if (input.isDown('SPACE')) {
        console.log(Date.now() - player.lastJump > 100, player.hitGround)
        if (Date.now() - player.lastJump > 100 && player.hitGround) {
            player.pos[1] -= playerSpeed * dt;
            player.direction[1] -= unit;
            player.lastJump = Date.now();
        }
    }

    if (input.isDown('LEFT') || input.isDown('a')) {
        player.pos[0] -= playerSpeed * dt;
        player.direction[0] -= unit;
    }

    if (input.isDown('RIGHT') || input.isDown('d')) {
        player.pos[0] += playerSpeed * dt;
        player.direction[0] += unit;
    }
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
    return !(r <= x2 || x > r2 ||
             b <= y2 || y > b2);
}

function boxCollides(pos, size, pos2, size2) {
    return collides(pos[0], pos[1],
                    pos[0] + size[0], pos[1] + size[1],
                    pos2[0], pos2[1],
                    pos2[0] + size2[0], pos2[1] + size2[1]);
}

function boxCollidesX(pos2, size2) {
    const x = player.pos[0];
    const r = x + player.sprite.size[0];
    const x2 = pos2[0];
    const r2 = x2 + size2[0];
    return !(r < x2 || x > r2);
}

function boxCollidesY(pos2, size2) {
    const y = player.pos[1];
    const b = y + player.sprite.size[1];
    const y2 = pos2[1];
    const b2 = y2 + size2[1];
    return !(b < y2 || y > b2);
}


function checkCollisions() {
    checkPlayerBounds();
    
    // Run collision detection for all enemies and bullets
    for(var i = 0; i < collidables.length; i++) {
        var pos = collidables[i].pos;
        var size = collidables[i].sprite.size;

        if (boxCollides(pos, size, player.pos, player.sprite.size)) {
        //     // Remove the block
        //     collidables.splice(i, 1);
        //     i--;

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

        // have a direction of some sort!
        player.direction = player.direction[0] || player.direction[1] ? player.direction : [1, 1];

        // As long as they are colliding (Be careful for infinite loops)
        let coll_x = boxCollidesX(pos, size);
        let coll_y = boxCollidesY(pos, size);
        let x_first = false;
        while(coll_x && coll_y) {
   
            if (x_first) {
                coll_x = resolveCollisionX(pos, size);
                coll_y = resolveCollisionY(pos, size);
            } else {
                coll_y = resolveCollisionY(pos, size);
                coll_x = resolveCollisionX(pos, size);
            }
            x_first = !x_first;
        }
    }
}

function resolveCollisionX(pos, size) {
    return resolveCollision(pos, size, true);
}
function resolveCollisionY(pos, size) {
    return resolveCollision(pos, size, false);
}
function resolveCollision(pos, size, dir_x) {
    const collisionDetection = dir_x ? boxCollidesX : boxCollidesY;
    const index = dir_x ? 0 : 1;

    if (player.direction[index] && boxCollidesX(pos, size) && boxCollidesY(pos, size)) {
    
        // move the player 1 unit back the direction it came from
        player.pos[index] -= player.direction[index];
    }
    return collisionDetection(pos, size);
}

function checkPlayerBounds() {
    // Check bounds
    max_right = canvas.width - player.sprite.size[0];
    max_down = canvas.height - player.sprite.size[1];

    player.pos[0] = Math.max(0, Math.min(player.pos[0], max_right));
    player.pos[1] = Math.max(0, Math.min(player.pos[1], max_down));
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
