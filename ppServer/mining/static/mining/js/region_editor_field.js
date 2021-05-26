const selected_entities = new Set();
var queue_place_entity = [];
var queue_remove_entity = [];

var delete_mode = false;
var fill_rect_mode = false;
var selected_entities_rect_select_mode = [];
var rect_select_mode_coords;

const pressed_mouse_buttons = new Set();

var highlight_entity = undefined;

function initField() {
    canvas = document.querySelector("canvas");

    // mousedown, mousemove, and mouseup
    canvas.addEventListener('mousedown', e => {
        pressed_mouse_buttons.add(e.button);
        
        const point = new Vector(e.offsetX, e.offsetY);
        if (Input.isDown('SHIFT')) { update_rectangle_select_mode(point); }
        else { change_material_at(point); }
    });
    
    canvas.addEventListener('mousemove', e => {
        if (pressed_mouse_buttons.size) {
            const point = new Vector(e.offsetX, e.offsetY);
            
            if (Input.isDown('SHIFT')) { update_rectangle_select_mode(point); }
            else { change_material_at(point); }
        }
    });
    
    window.addEventListener('mouseup', e => {
        pressed_mouse_buttons.delete(e.button);
        if (Input.isDown('SHIFT')) { reset_rectangle_select_mode(); }
    });
    window.addEventListener('blur', () => {
        pressed_mouse_buttons.clear();
        if (Input.isDown('SHIFT')) { reset_rectangle_select_mode(); }
    });
    window.addEventListener('click', e => {
        if (e.target !== canvas && e.target.id !== "random-rotate-selected") {
            selected_entities.clear();
        }
    });


    canvas.addEventListener("click", e => {
        const point = new Vector(e.offsetX, e.offsetY);
        delete_mode ?
            queue_remove_entity.push({point, layer: selected_layer}) :
            queue_place_entity.push({point, material: selected_material, layer: selected_layer});
    });
    // don't open menu on right-click inside of the field
    canvas.addEventListener("contextmenu", e => { e.preventDefault(); });

    reset_rectangle_select_mode();
}


function change_material_at(point) {
    // right-click or delete mode
    if (pressed_mouse_buttons.has(2) || (pressed_mouse_buttons.has(0) && delete_mode)) {
        queue_remove_entity.push({point, layer: selected_layer});
        return;
    }
    
    // left-click
    if (pressed_mouse_buttons.has(0)) {
        queue_place_entity.push({point, material: selected_material, layer: selected_layer});
    }
}



// HELPERS //

function is_intersecting(entityA, entityB) {
    if (entityA.layer !== entityB.layer) { return false; }
    
    const a = entityA;
    const b = entityB;

    return !(a.x + a.w * a.scale <= b.x || a.x >= b.x + b.w * b.scale ||
        a.y + a.h * a.scale <= b.y || a.y >= b.y + b.h * b.scale);
}


// FIELD CALLBACKS //

// alter material on cell
function set_material_at(point, layer, material) {
    if (!point || !material || !layer) { return; }

    // set up new entity
    new_entity = {
        x: Math.floor(point.x / grid_size) * grid_size,
        y: Math.floor(point.y / grid_size) * grid_size,
        material,
        scale: 1,
        layer: layer.id,
        mirrored: false,
        rotation_angle: 0
    };
    new_entity.h = new_entity.material.h;
    new_entity.w = new_entity.material.w;

    // check for already existing entity in that spot
    const existing_entity = layer.entities.find(e => is_intersecting(e, new_entity));
    last_selected_entity = existing_entity || new_entity;

    if (existing_entity) {
        selected_entities.add(existing_entity);
        return;
    }

    // if not, add new entity
    layer.entities.push(new_entity);
    selected_entities.add(new_entity);
}

function delete_material_at(point, layer) {
    if (!point || !layer) { return; }

    const point_rect = {...point, w: 1, h: 1, scale: 1, layer: layer.id};

    layer.entities = layer.entities.filter(e => !is_intersecting(e, point_rect));
    selected_entities.clear();
    last_selected_entity = undefined;
}

function get_entity_at(point, layer_tag) {
    new_entity = {
        ...point,
        w: 1,
        h: 1,
        material: undefined,
        scale: 1,
        layer: parseInt(layer_tag.dataset.id)
    };

    // check for already existing entity in that spot
    return layers.find(layer => layer.id === new_entity.layer).entities.find(e => is_intersecting(e, new_entity));
}


function update_rectangle_select_mode(point) {

    let entity = get_entity_at(point, selected_layer);
    if (!entity) {
        if (!fill_rect_mode) { return; }

        // include current point as dummy entity into selected area, even though there is no entity
        entity = {
            ...point,
            h: 1,
            w: 1,
            scale: 1
        }
    }
    highlight_entity = entity;

    const layer = layers.find(layer => layer.id === parseInt(selected_layer.dataset.id));

    // coordinates of selected area
    rect_select_mode_coords = {
        minx: Math.min(rect_select_mode_coords.minx, entity.x),
        maxx: Math.max(rect_select_mode_coords.maxx, entity.x + (entity.w * entity.scale)),
        miny: Math.min(rect_select_mode_coords.miny, entity.y),
        maxy: Math.max(rect_select_mode_coords.maxy, entity.y + (entity.h * entity.scale))
    };

    // selected area
    const rect = {
        x: rect_select_mode_coords.minx,
        y: rect_select_mode_coords.miny,
        w: rect_select_mode_coords.maxx - rect_select_mode_coords.minx,
        h: rect_select_mode_coords.maxy - rect_select_mode_coords.miny,
        scale: 1,
        layer: layer.id
    };

    if (fill_rect_mode) { fill_up_missing_entities(rect); }

    // add entities to selected_entities_rect_select_mode
    selected_entities_rect_select_mode = layer.entities.filter(e => is_intersecting(e, rect));

    // remove entities in area from selected_entities
    const reduced_selected_entities = [...selected_entities].filter(e => !selected_entities_rect_select_mode.includes(e));
    selected_entities.clear();
    reduced_selected_entities.forEach(e => selected_entities.add(e));
}

function reset_rectangle_select_mode() {
    rect_select_mode_coords = {minx: Number.MAX_SAFE_INTEGER, maxx: -10, miny: Number.MAX_SAFE_INTEGER, maxy: -10};

    selected_entities_rect_select_mode.forEach(e => selected_entities.add(e));
    selected_entities_rect_select_mode = [];
    highlight_entity = undefined;
}


function fill_up_missing_entities(rect) {
    const material = materials.find(material => material.id == selected_material.dataset.id);

    const start_x = Math.floor(rect.x / grid_size) * grid_size;
    const start_y = Math.floor(rect.y / grid_size) * grid_size;
    const w = rect.w;
    const h = rect.h;

    for (let x = start_x; x < rect.x + w; x += material.w) {
        for (let y = start_y; y < rect.y + h; y += material.h) {
            const entity = {
                point: { x, y },
                material: selected_material,
                layer: selected_layer,
            };
            queue_place_entity.push(entity);
        }
    }
}