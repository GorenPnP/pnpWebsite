var canvas;
var ctx;

var layers;
var char_layer_index;
var materials;

const class_selected = "selected";

var lastTime;

document.addEventListener("DOMContentLoaded", () => {

    // start img loading
    const img_urls = [...document.querySelectorAll(".material img")].map(img => img.src.replace(`${window.location.protocol}//${window.location.host}`, ''));
    resources.load(...img_urls);

    // init globals
    canvas = document.querySelector("canvas");
    ctx = canvas.getContext("2d");
    
    char_layer_index = JSON.parse(document.querySelector("#char-layer-index").innerHTML);
    layers = JSON.parse(document.querySelector("#layers").innerHTML);
    materials = JSON.parse(document.querySelector("#materials").innerHTML);

    // init all other components
    initSidebars();
    initToolbar();
    initField();

    // start running
    lastTime = Date.now();
    resources.onReady(main);
});


function main() {
    const now = Date.now();
    const dt = (now - lastTime) / 1000.0;

    handle_input(dt);

    update();
    render();

    lastTime = now;
    requestAnimFrame(main);
}

function handle_input(dt) {
    if (selected_entities.size && !Input.isEmpty()) {
        selected_entities.forEach(e => handle_input_of(e, dt));
        if (Input.isDown('M')) { Input.blockKey('M'); }
        if (Input.isDown('R')) { Input.blockKey('R'); }
    }
}

function handle_input_of(entity, dt) {

    const dt_translate = dt * 50;
    const dt_scale = dt * 2;

    // translate
    if (Input.isDown('T')) {
        // down
        if (Input.isDown('DOWN') && !Input.isDown('UP')) { entity.y += dt_translate; }
        // up
        if (!Input.isDown('DOWN') && Input.isDown('UP')) { entity.y -= dt_translate; }
        // right
        if (!Input.isDown('LEFT') && Input.isDown('RIGHT')) { entity.x += dt_translate; }
        // left
        if (Input.isDown('LEFT') && !Input.isDown('RIGHT')) { entity.x -= dt_translate; }
    }
    // rotate
    else if (Input.isDown('R')) {
        entity.rotation_angle = (entity.rotation_angle + 1) % 4;
    }
    // mirror
    else if (Input.isDown('M')) {
        entity.mirrored = !entity.mirrored;
    }
    // scale
    else {
        // down
        if (Input.isDown('DOWN') && !Input.isDown('UP')) { entity.scale = Math.max(0.1, entity.scale - dt_scale); }
        // up
        if (!Input.isDown('DOWN') && Input.isDown('UP')) {entity.scale += dt_scale; }
    }
}



// HELPERS //



function update() {
    let queue = [...queue_place_entity];
    queue_place_entity = [];
    queue.forEach(entry => {
        const layer = layers.find(layer => entry.layer.dataset.index == layer.index);
        const material = layer.index === char_layer_index ? {w: 64, h: 64, icon: "/static/res/img/mining/char_skin_front.png"} : materials.find(m => m.id == entry.material.dataset.id)
        
        set_material_at(entry.point, layer, material);
    });

    queue = [...queue_remove_entity];
    queue_remove_entity = [];
    queue.forEach(entry => {
        const layer = layers.find(layer => entry.layer.dataset.index == layer.index);
        delete_material_at(entry.point, layer)
    });
}


// set bg images to the cells' material_ids on start
function render() {

    // paint background & grid
    ctx.save();
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = bg_color;
    for (let x = 0; x * grid_size < canvas.width; x++) {
        for (let y = 0; y * grid_size < canvas.width; y++) {
            const strokeThickness = new Vector(1, 1);
            if ((x+1) % 5 === 0) { strokeThickness.x = 2; }
            if ((y+1) % 5 === 0) { strokeThickness.y = 2; }

            if (!show_border) { strokeThickness.x = strokeThickness.y = 0; }

            ctx.fillRect(x * grid_size, y * grid_size, grid_size - strokeThickness.x, grid_size - strokeThickness.y);
        }
    }
    ctx.restore();


    // paint entities
    for (const layer of layers.sort((a, b) => a.index - b.index)) {        
        for (const entity of layer.entities) {
            
            // render img
            ctx.save();
            ctx.globalAlpha = layer.index == selected_layer.dataset.index ? 1 : opacity;


            let x = entity.x;
            let y = entity.y;
            let w = entity.w * entity.scale;
            let h = entity.h * entity.scale;
            
            // rotate
            ctx.translate(x + w/2, y + h/2);
            ctx.rotate(entity.rotation_angle/2 * Math.PI);
            
            // mirror with y-axis. Because canvas is rotated previously, choose x-axis if rotation is 90° or 270°
            if (entity.mirrored) {
                if (entity.rotation_angle % 2) {
                    ctx.scale(1, -1);
                    h *= -1;
                } else {
                    ctx.scale(-1, 1);
                    w *= -1;
                }
            }


            // x, y = 0 would be the center of the entity. compute offset for upper left corner
            // in respect to rotation & mirroring
            x = -w/2;
            y = -h/2;

            // translate & scale
            const url = layer.index !== char_layer_index ? entity.material.icon : "/static/res/img/mining/char_skin_front.png";
            ctx.drawImage(resources.get(url),
                0, 0, entity.w, entity.h,
                x, y, w, h);

            ctx.restore();
        }
    }

    render_outlines(selected_entities, '#fff');
    // render_outlines(selected_entities_rect_select_mode, '#f00');
    render_outlines(highlight_entity ? [highlight_entity] : [], '#f0f');

    ctx.strokeStyle = '#0f0';
    ctx.lineWidth = 5;
    let x = rect_select_mode_coords.minx;
    let y = rect_select_mode_coords.miny;
    let w = rect_select_mode_coords.maxx - rect_select_mode_coords.minx;
    let h = rect_select_mode_coords.maxy - rect_select_mode_coords.miny;
    ctx.strokeRect(x, y, w, h);
}

function render_outlines(entities, color) {
    // draw outline around selected_entity as last thing to render
    if (!entities || (!entities.size && !entities.length)) { return; }
    entities.forEach(e => {

        // render img
        ctx.save();
        ctx.strokeStyle = color;
        ctx.lineWidth = 5;
        let x = e.x;
        let y = e.y;
        let w = e.w * e.scale;
        let h = e.h * e.scale;
        
        // rotate
        ctx.translate(x + w/2, y + h/2);
        ctx.rotate(e.rotation_angle/2 * Math.PI);
    
    
        // x, y = 0 would be the center of the entity. compute offset for upper left corner
        // in respect to rotation
        x = -w/2;
        y = -h/2;
    
        // translate & scale
        ctx.strokeRect(x, y, w, h);
        ctx.restore();
    });
}