const selected_entities = new Set();
var queue_place_entity = [];
var queue_remove_entity = [];

var delete_mode = false;
var fill_rect_mode = false;
var selected_entities_rect_select_mode = [];
var rect_select_mode_coords;
var rect_select_mode_start_point;

const pressed_mouse_buttons = new Set();

var highlight_entity = undefined;

function initField() {
    canvas = document.querySelector("canvas");

    // mousedown, mousemove, and mouseup
    canvas.addEventListener('mousedown', e => {
        pressed_mouse_buttons.add(e.button);
        
        const point = new Vector(e.offsetX, e.offsetY);
        if (Input.isDown('SHIFT')) {
            rect_select_mode_start_point = point;
            update_rectangle_select_mode(point);
        }
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
        if (Input.isDown('SHIFT')) {
            if (fill_rect_mode) { fill_up_missing_entities(); }
            reset_rectangle_select_mode();
        }
    });
    window.addEventListener('blur', () => {
        pressed_mouse_buttons.clear();
        if (Input.isDown('SHIFT')) {
            if (!fill_rect_mode) { fill_up_missing_entities(); }
            reset_rectangle_select_mode();
        }
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
    const start = grid_cell_of_point(rect_select_mode_start_point);
    const current = grid_cell_of_point(point);
    rect_select_mode_coords = new Rectangle(
        Math.min(start.x, current.x),
        Math.min(start.y, current.y),
        Math.max(start.x, current.x) - Math.min(start.x, current.x) + grid_size,
        Math.max(start.y, current.y) - Math.min(start.y, current.y) + grid_size
    );

    const rect = {
        ...rect_select_mode_coords,
        scale: 1,
        layer: layer.id
    };
    // add entities to selected_entities_rect_select_mode
    selected_entities_rect_select_mode = layer.entities.filter(e => is_intersecting(e, rect));

    // remove entities in area from selected_entities
    const reduced_selected_entities = [...selected_entities].filter(e => !selected_entities_rect_select_mode.includes(e));
    selected_entities.clear();
    reduced_selected_entities.forEach(e => selected_entities.add(e));
}

function grid_cell_of_point(point) {
    return new Rectangle(
        Math.floor(point.x / grid_size) * grid_size,
        Math.floor(point.y / grid_size) * grid_size,
        grid_size,
        grid_size,
    );
}

function reset_rectangle_select_mode() {
    rect_select_mode_start_point = undefined;
    rect_select_mode_coords = {minx: Number.MAX_SAFE_INTEGER, maxx: -10, miny: Number.MAX_SAFE_INTEGER, maxy: -10};

    selected_entities_rect_select_mode.forEach(e => selected_entities.add(e));
    selected_entities_rect_select_mode = [];
    highlight_entity = undefined;
}


function fill_up_missing_entities() {
    const material = materials.find(material => material.id == selected_material.dataset.id);

    const max_x = rect_select_mode_coords.x + rect_select_mode_coords.w;
    const max_y = rect_select_mode_coords.y + rect_select_mode_coords.h;

    for (let x = rect_select_mode_coords.x; x < max_x; x += material.w) {
        for (let y = rect_select_mode_coords.y; y < max_y; y += material.h) {

            const entity = {
                point: { x, y },
                material: selected_material,
                layer: selected_layer,
            };
            queue_place_entity.push(entity);
        }
    }
}