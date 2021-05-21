var canvas;
var ctx;

var layers;
var char_layer_index;
var materials;

var next_creation_id = 0;

var field_width_input;
var field_height_input;

var bg_color;
var opacity;
var zooming = 1;
var grid_size = 64;
var show_border = true;

var last_rendered = Date.now();
var rendering_cooldown = 150;

var selected_layer;
var selected_material;
var selected_entity;
const class_selected = "selected";

var delete_mode = false;

const pressed_mouse_buttons = new Set();

document.addEventListener("DOMContentLoaded", () => {

    // init globals
    field_width_input = document.querySelector('#field-width');
    field_height_input = document.querySelector('#field-height');
    char_layer_index = JSON.parse(document.querySelector("#char-layer-index").innerHTML);
    layers = JSON.parse(document.querySelector("#layers").innerHTML);
    materials = JSON.parse(document.querySelector("#materials").innerHTML);
    bg_color = JSON.parse(document.querySelector("#bg-color").innerHTML);

    const img_urls = [...document.querySelectorAll(".material img")].map(img => img.src.replace(`${window.location.protocol}//${window.location.host}`, ''));
    resources.load(...img_urls);

    // toolbar listeners
    field_width_input.addEventListener('input', update_field_size);
    field_height_input.addEventListener('input', update_field_size);
    document.querySelector("#field-bg-color").addEventListener('input', update_field_bg_color);
    document.querySelector('#zoom').addEventListener('input', zoom);
    document.querySelector('#grid-size').addEventListener('input', update_grid_size);
    document.querySelector('#unselected-field-opacity').addEventListener('input', update_unselected_field_opacity);

    // material bar listeners
    document.querySelector('#delete-on-layer').addEventListener('click', delete_all_on_layer);
    document.querySelectorAll('.material')
        .forEach(material => material.addEventListener('click', () => select_material(material)));

    // layer bar listeners
    document.querySelectorAll('.layer')
        .forEach(layer => layer.addEventListener('click', () => select_layer(layer)));

    // field listeners
    canvas = document.querySelector("canvas");
    ctx = canvas.getContext("2d");

    // mousedown, mousemove, and mouseup
    canvas.addEventListener('mousedown', e => {
        pressed_mouse_buttons.add(e.button);
        
        const point = new Vector(e.offsetX, e.offsetY);
        change_material_at(point);
    });
    
    canvas.addEventListener('mousemove', e => {
        if (pressed_mouse_buttons) {
            const point = new Vector(e.offsetX, e.offsetY);
            change_material_at(point);
        }
    });
    
    window.addEventListener('mouseup', e => {
        pressed_mouse_buttons.delete(e.button);
    });
    window.addEventListener('blur', () => {
        pressed_mouse_buttons.clear();
    });
    window.addEventListener('click', e => {
        if (e.target !== canvas) {
            selected_entity = undefined;
            render();
        }
    });


    canvas.addEventListener("click", e => {
        const point = new Vector(e.offsetX, e.offsetY);
        delete_mode ? delete_material_at(point) : set_material_at(point);
    });
    // don't open menu on right-click inside of the field
    canvas.addEventListener("contextmenu", e => { e.preventDefault(); });

    // submit listener
    document.querySelector(".button--ok").addEventListener("click", submit);


    // create initial status
    // select first in bars
    select_material(document.querySelector('.material'));
    select_layer(document.querySelector('.layer'));

    // init field
    update_field_size();
    zoom();

    resources.onReady(() => {
        start_keyevent_loop();
        setTimeout(render, rendering_cooldown);
    });
});

function change_material_at(point) {
    // right-click or delete mode
    if (pressed_mouse_buttons.has(2) || (pressed_mouse_buttons.has(0) && delete_mode)) {
        delete_material_at(point);
        return;
    }
    
    // left-click
    if (pressed_mouse_buttons.has(0)) { set_material_at(point); }
}

function update_field_size() {
    let width = parseInt(field_width_input.value || 0);
    let height = parseInt(field_height_input.value || 0);

    set_size_of_field(width, height);
}

function set_size_of_field(width, height) {

    canvas.width = width;
    canvas.height = height;
    canvas.style.width = width;
    canvas.style.height = height;
    render();
}


// HELPERS //


// FIELD CALLBACKS //

// alter material on cell
function set_material_at(point) {
    // TODO real collision detection

    if (!point || !selected_material || !selected_layer) { return; }

    const layer = layers.find(l => l.index == selected_layer.dataset.index);

    // check for already existing cell
    existing_cell = layer.entities.find(e => is_intersecting(e, {...point, w: 1, h: 1, scale: 1, layer: layer.id}));
    if (existing_cell) {
        selected_entity = existing_cell;
        return render();
    }

    // add cell
    cell = {
            x: Math.floor(point.x / grid_size) * grid_size,
            y: Math.floor(point.y / grid_size) * grid_size,
            material: layer.index === char_layer_index ? {w: 64, h: 64, icon: "/static/res/img/mining/char_skin_front.png"} : materials.find(m => m.id == selected_material.dataset.id),
            scale: 1,
            layer: layer.id,
            mirrored: false,
            rotation_angle: 0,
            creation_id: next_creation_id++
        };
    cell.h = cell.material.h;
    cell.w = cell.material.w;

    layer.entities.push(cell);
    selected_entity = cell;
    render();
}

function delete_material_at(point) {
    if (!point || !selected_layer) { return; }

    const layer = layers.find(layer => selected_layer.dataset.index == layer.index);
    const entity = layer.entities.find(e => is_intersecting(e, {...point, w: 1, h: 1, scale: 1, layer: layer.id}));
    layer.entities = layer.entities.filter(e => e !== entity);
    selected_entity = undefined;
    render();
}


// set bg images to the cells' material_ids on start
function render() {
    if (last_rendered + rendering_cooldown > Date.now()) { return; }
    last_rendered = Date.now();

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

    // draw outline around selected_entity as last thing to render
    if (!selected_entity) { return; }
    const e = selected_entity;

    // render img
    ctx.save();
    ctx.strokeStyle = "#fff";
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
}


// MATERIAL BAR CALLBACKS //

function select_material(material) {
    if (!material || (selected_material && material === selected_material)) { return; }

    selected_material && selected_material.classList.remove(class_selected);

    selected_material = material;
    material.classList.add(class_selected);
}

// LAYER BAR CALLBACKS //

function select_layer(layer) {
    if (!layer || (selected_layer && layer === selected_layer)) { return; }

    // prepare for change of material bar (if necessary)
    const old_layer_is_char_layer = selected_layer && selected_layer.dataset.index == char_layer_index;
    const new_layer_is_char_layer = layer.dataset.index == char_layer_index;

    selected_layer && selected_layer.classList.remove(class_selected);

    // if will switch between bars, select first entry in one
    if (selected_layer && old_layer_is_char_layer !== new_layer_is_char_layer) {
        select_material(document.querySelector(!new_layer_is_char_layer ? ".material--noncharacter" : ".material--character"));
    }

    selected_entity = undefined;

    selected_layer = layer;
    layer.classList.add(class_selected);

    // TODO adapt opacities

    // adapt material bar
    document.querySelectorAll(".material--noncharacter").forEach(tag => tag.style.display = new_layer_is_char_layer ? "none" : "");
    document.querySelectorAll(".material--character").forEach(tag => tag.style.display = new_layer_is_char_layer ? "" : "none");

    render();
}


// SUBMIT CALLBACK //

function submit() {
    const name = document.querySelector("#name").value;
    // check if name exists
    if (!name) {
        alert("Name missing");
        return;
    }

    // check if spawnpoints exist
    const char_field_layer = layers.find(layer => layer.index === char_layer_index && layer.entities.length);
    if (!char_field_layer) {
        alert("Spawn point(s) missing");
        return;
    }


    const fields = layers
        .map(layer => layer.entities)
        .reduce((acc, layer) => [...acc, ...layer], []);
    console.log(fields)

    post({ name, fields: JSON.stringify(fields), bg_color },
        () => window.location.href = `/mining`,
        error => alert(error.response.data.message));
}


// TOOLBAR CALLBACKS //

function zoom() {
    zooming = parseFloat(document.querySelector("#zoom").value) || 1;
    update_field_size();
}

function toggle_field_border() {
    const border_toggle_checkbox = document.querySelector('#border-toggle');
    border_toggle_checkbox.classList.toggle('checked');

    show_border = border_toggle_checkbox.classList.contains("checked");

    update_field_size();
    render();
}

function toggle_delete_mode() {
    const delete_toggle_checkbox = document.querySelector('#delete-toggle');
    delete_mode = delete_toggle_checkbox.classList.toggle('checked');
}

function update_unselected_field_opacity() {
    opacity = parseFloat(document.querySelector('#unselected-field-opacity').value);
    render();
}

function update_field_bg_color() {
    bg_color = document.querySelector('#field-bg-color').value;
    render();
}

function update_grid_size() {
    grid_size = parseInt(document.querySelector("#grid-size").value);
    render();
}


// INFO CALLBACKS //

function delete_all_on_layer() {
    if (!selected_layer) { return; }

    layers = layers.map(layer => {
        if (layer.index != selected_layer.dataset.index) { return layer; }

        return {...layer, entities: [] };
    });

    render();
}




function start_keyevent_loop() {
    const dt = 1;
    setInterval(() => {
        if (!selected_entity || Input.isEmpty()) { return; }

        const next_pos = {...selected_entity};

        // translate
        if (Input.isDown('T')) {
            // down
            if (Input.isDown('DOWN') && !Input.isDown('UP')) { next_pos.y += dt; }
            // up
            if (!Input.isDown('DOWN') && Input.isDown('UP')) { next_pos.y -= dt; }
            // right
            if (!Input.isDown('LEFT') && Input.isDown('RIGHT')) { next_pos.x += dt; }
            // left
            if (Input.isDown('LEFT') && !Input.isDown('RIGHT')) { next_pos.x -= dt; }
        }
        // rotate
        else if (Input.isDown('R')) {
            next_pos.rotation_angle = (next_pos.rotation_angle + 1) % 4;
        }
        // mirror
        else if (Input.isDown('M')) {
            next_pos.mirrored = !next_pos.mirrored;
        }
        // scale
        else {
            // down
            if (Input.isDown('DOWN') && !Input.isDown('UP')) { next_pos.scale = Math.max(0.1, next_pos.scale - dt * .1); }
            // up
            if (!Input.isDown('DOWN') && Input.isDown('UP')) {next_pos.scale += dt * .1; }
        }

        // check collisions
        const layer = layers.find(l => l.id === selected_entity.layer);
        if (layer.entities.filter(e => !are_equal_entities(e, next_pos)).every(e => !is_intersecting(e, next_pos))) {
            selected_entity = next_pos; }

        // update entity
        layers = layers.map(l => {
            if (l.id !== selected_entity.layer) { return l; }
            return {
                ...l,
                entities: l.entities.map(e => { return are_equal_entities(e, selected_entity) ? selected_entity : e; })
            }
        });

        render();
    }, rendering_cooldown);
}


function is_intersecting(entityA, entityB) {
    if (entityA.layer !== entityB.layer) { return false; }
    
    const a = entityA;
    const b = entityB;

    return !(a.x + a.w * a.scale <= b.x || a.x >= b.x + b.w * b.scale ||
        a.y + a.h * a.scale <= b.y || a.y >= b.y + b.h * b.scale);
}

function are_equal_entities(a, b) {
    const id_a = a.id || a.creation_id;
    const id_b = b.id || b.creation_id;
    return id_a === id_b;
}