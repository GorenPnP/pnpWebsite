var field_width_input;
var field_height_input;

var bg_color;
var opacity;
var zooming = 1;
var grid_size = 64;
var show_border = true;

function initToolbar(layers) {

    // init globals
    field_width_input = document.querySelector('#field-width');
    field_height_input = document.querySelector('#field-height');
    bg_color = JSON.parse(document.querySelector("#bg-color").innerHTML);

    // toolbar listeners
    field_width_input.addEventListener('input', update_field_size);
    field_height_input.addEventListener('input', update_field_size);
    document.querySelector("#field-bg-color").addEventListener('input', update_field_bg_color);
    document.querySelector('#zoom').addEventListener('input', zoom);
    document.querySelector('#grid-size').addEventListener('input', update_grid_size);
    document.querySelector('#unselected-field-opacity').addEventListener('input', update_unselected_field_opacity);
    document.querySelector('#delete-on-layer').addEventListener('click', delete_all_on_layer);
    document.querySelector('#random-rotate-selected').addEventListener('click', random_rotate_selected);

    // calc level width & height
    level_dimensions = get_level_dimensions(layers);
    field_width_input.value = Math.ceil(level_dimensions.w/grid_size) || 1;
    field_height_input.value = Math.ceil(level_dimensions.h/grid_size) || 1;

    // init field
    update_field_size();
    zoom();
}


// HELPERS //

function get_number_input_value(input) {
    let { value, min, max } = input;
    min = parseInt(min || 1);
    max = parseInt(max || 1000);
    value = parseInt(value || min);
    value = Math.max(min, Math.min(value, max));
    input.value = value;
    return value;
}


// TOOLBAR CALLBACKS //

function update_field_size() {
    const width = get_number_input_value(field_width_input) * grid_size;
    const height = get_number_input_value(field_height_input) * grid_size;
    level_dimensions = new Rectangle(0, 0, width, height);

    canvas.width = width;
    canvas.height = height;
    canvas.style.width = width;
    canvas.style.height = height;
}

function zoom() {
    zooming = parseFloat(document.querySelector("#zoom").value) || 1;
    update_field_size();
}

function toggle_field_border() {
    const border_toggle_checkbox = document.querySelector('#border-toggle');
    border_toggle_checkbox.classList.toggle('checked');

    show_border = border_toggle_checkbox.classList.contains("checked");
}

function toggle_delete_mode() {
    const delete_toggle_checkbox = document.querySelector('#delete-toggle');
    delete_mode = delete_toggle_checkbox.classList.toggle('checked');
}

function toggle_rect_fill_mode() {
    const toggle_fill_checkbox = document.querySelector('#rect-fill');
    fill_rect_mode = toggle_fill_checkbox.classList.toggle('checked');
}

function update_unselected_field_opacity() {
    opacity = parseFloat(document.querySelector('#unselected-field-opacity').value);
}

function update_field_bg_color() {
    bg_color = document.querySelector('#field-bg-color').value;
}

function update_grid_size() {
    grid_size = parseInt(document.querySelector("#grid-size").value);
    update_field_size();
}

function delete_all_on_layer() {
    if (!selected_layer) { return; }

    layers = layers.map(layer => {
        if (layer.index != selected_layer.dataset.index) { return layer; }

        return {...layer, entities: [] };
    });
}

function random_rotate_selected() {
    selected_entities.forEach(e => {
        e.rotation_angle = Math.floor(Math.random() * 4);   // random of 0, 1, 2, 3
        e.mirrored = !Math.floor(Math.random() * 2);        // random of true, false
    })
}
