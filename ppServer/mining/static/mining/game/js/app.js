// Create the canvas
let canvas;
let ctx;

let bg_color;
let materials;
var char_layer_index;

var levelPosition = new Rectangle();

// Game state
var entities = [];  // game logic, not for rendering directly
var collidables = [];
var breakables = [];

var player;
var other_players = [];

var lastTime;

// startup
document.addEventListener("DOMContentLoaded", () => {

    // some const things
    bg_color = JSON.parse(document.querySelector("#bg-color").innerHTML);
    layers = JSON.parse(document.querySelector("#layers").innerHTML);
    char_layer_index = JSON.parse(document.querySelector("#char-layer-index").innerHTML);

    const img_urls = [
        '/static/res/img/mining/char_skin_front.png',
        '/static/res/img/mining/char_skin_back.png',
        '/static/res/img/mining/char_skin_left.png',
        '/static/res/img/mining/char_skin_right.png',
        ...new Set(layers.reduce((acc, l) => [...acc, ...l.entities], []).map(entity => entity.material.icon))
    ];
    // load assets
    resources.load(...img_urls);

    // calc game dimensions
    const max_coords = layers
        .filter(layer => layer.index !== char_layer_index)
        .reduce((entities, layer) => [...entities, ...(layer.entities || [])], [])
        .reduce((max, entity) => {
            max.x = Math.max(max.x, entity.x + entity.w);
            max.y = Math.max(max.y, entity.y + entity.h);
            return max;
        }, new Vector());
    levelPosition = {x: 0, y : 0, w: max_coords.x, h: max_coords.y};


    resources.onReady(init);
});

function init() {
    initWsSocket();
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

    handleInput(dt, player);
    updateEntities(dt);

    player.resolveCollisions();
    Canvas.setRenderOffset();
    player.stayInBounds(levelPosition);

    markReachableBreakableBlocks();
};



function updateEntities(dt) {
    // Update all non-player sprites
    [...entities, player].forEach(e => e.updateSprite(dt));
}


function markReachableBreakableBlocks() {
    const reach = Math.max(player.pos.w, player.pos.h) / 2;

    const reachRect = new Rectangle(player.pos.x - reach, player.pos.y - reach, player.pos.w + 2*reach, player.pos.h + 2*reach);
    
    // Run collision detection for all enemies and bullets
    for(const breakable of breakables) {
        breakable.is_in_reach = boxCollides(reachRect, breakable.pos);
    }
}

// Draw everything
function render() {    
    ctx.fillStyle = '#3a3d40';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = bg_color;
    ctx.fillRect(Canvas.renderOffset.x, Canvas.renderOffset.y, levelPosition.w, levelPosition.h);
    
    entities.filter(e => e.layer.index < 0).forEach(e => e.render(ctx, Canvas.renderOffset));
    other_players.forEach(p => p.render(ctx, Canvas.renderOffset));

    player.render(ctx);

    entities.filter(e => e.layer.index >= 0).forEach(e => e.render(ctx, Canvas.renderOffset));

    renderMarkForBreakables(Canvas.renderOffset);

    if (Canvas.clicked_breakable) {
        const centerPoint = new Vector(player.pos.x + player.pos.w/2, player.pos.y - 30 - 10);
        const percentFilled = Canvas.clicked_breakable.lost_rigidity / Canvas.clicked_breakable.rigidity * 100;
        drawPie(ctx, centerPoint, 30, percentFilled);

        if (percentFilled >= 100) {
            // remove block
            entities = entities.filter(e => e !== Canvas.clicked_breakable);
            updateFromEntities();
            
            // add loot to inventory
            ws_break(Canvas.clicked_breakable);

            Canvas.clicked_breakable = undefined;
        }
    }
}


// Reset game to original state
function reset() {

    // setup canvas
    canvas = Canvas.reset();
    ctx = canvas.getContext("2d");
    
    // init player
    player = Player.reset(layers.find(l => l.index === char_layer_index));

    let last_pos = new Vector();

    // save update of player position every 1s
    setInterval(() => {
        if (last_pos.x !== player.pos.x || last_pos.y !== player.pos.y) {
            const position = {x: player.pos.x, y: player.pos.y};
            ws_save_player_position(position);
            last_pos = position;
        }
    }, 1000);

    // init layers
    layers = Layer.reset();

    // init field with all entities
    entities = Entity.reset(layers.filter(l => l.index != char_layer_index));
    updateFromEntities();
}


function updateFromEntities() {
    collidables = entities.filter(entity => entity.layer.is_collidable);
    breakables = entities.filter(entity => entity.layer.is_breakable);
}