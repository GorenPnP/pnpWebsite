var field_width_input;
var field_height_input;
var field_containers = [];

var selected_layer;
var selected_material;
const class_selected = "selected";

var delete_mode = false;

document.addEventListener("DOMContentLoaded", () => {
    field_width_input = document.querySelector('#field-width');
    field_height_input = document.querySelector('#field-height');
    
    field_containers = document.querySelectorAll('.field-container');
    // add 1 field_container if none exists
    if (!field_containers.length) {
        const field_container = document.createElement("DIV");
        field_container.classList.add("field-container", "field-container--0", "selected");
        document.querySelector(".field").appendChild(field_container);
        field_containers = [field_container];

        // add layer
        const default_layer = document.createElement("DIV");
        default_layer.classList.add("layer")
        default_layer.setAttribute("data-index", 0);
        const layer_text = document.createElement("SPAN");
        layer_text.innerHTML = "Default";
        default_layer.appendChild(layer_text);
        document.querySelector(".layer-container").appendChild(default_layer);
    }

    field_width_input.addEventListener('input', update_field_size);
    field_height_input.addEventListener('input', update_field_size);
    document.querySelector("#field-bg-color").addEventListener('input',update_field_bg_color);
    document.querySelector('#zoom').addEventListener('input', zoom);
    document.querySelector('#unselected-field-opacity').addEventListener('input', update_unselected_field_opacity);
    document.querySelectorAll('.material')
        .forEach(material => material.addEventListener('click', () => select_material(material)));
    document.querySelectorAll('.layer')
        .forEach(layer => layer.addEventListener('click', () => select_layer(layer)));

    document.addEventListener("mousemove", e => {
        const cell = e.target.closest(".cell");
        
        // rightclick or delete mode
        if (cell && (e.buttons === 2 || (e.buttons === 1 && delete_mode))) {
            delete_material_on(cell);
            return;
        }
        
        // leftclick
        if (cell && e.buttons === 1) {
            set_material_on(cell);
            return;
        }
    });
    document.addEventListener("click", e => {
        const cell = e.target.closest(".cell");
        if (cell) { delete_mode ? delete_material_on(cell) : set_material_on(cell); }
    });

    // don't open menu on rightclick inside of the field
    field_containers.forEach(field_container => field_container.addEventListener("contextmenu", e => { e.preventDefault(); }));

    // handle submit
    document.querySelector(".button--ok").addEventListener("click", submit);


    // select first
    select_material(document.querySelector('.material'));
    select_layer(document.querySelector('.layer'));

    // init field
    update_field_size();
    zoom();

    prepopulate_field();
});

function update_field_size() {
    const width = parseInt(field_width_input.value || 0);
    const height = parseInt(field_height_input.value || 0);
    set_size_of_field(width, height);
}

function set_size_of_field(width, height) {

    field_containers.forEach(field_container => {
        field_container.style.gridTemplateColumns = `repeat(${width}, var(--field-size))`;
        field_container.style.gridTemplateRows = `repeat(${height}, var(--field-size))`;
    });

    add_cells(width, height);
    remove_cells(width, height);
}

function add_cells(width, height) {

    // add cells
    field_containers.forEach(field_container => {
        let cells = [...field_container.querySelectorAll(".cell")];
        // add one seed-cell to start from if no cell exists
        if (!cells.length) {
            const cell = create_filed_cell(0, 0);
            field_container.appendChild(cell);
            cells = [...field_container.querySelectorAll(".cell")];
        }

        // get current x/y dimensions to expand from
        let last_cell = cells.reverse()[0];
        const max_x = parseInt(last_cell.dataset.x_pos);
        const max_y = parseInt(last_cell.dataset.y_pos);

        // add in x direction
        for (let border_cell of field_container.querySelectorAll(`.cell[data-x_pos="${max_x}"]`)) {
            for (let x = width - 1; x > max_x; x--) {
                const cell = create_filed_cell(x, border_cell.dataset.y_pos);
                border_cell.after(cell);
            }
        }

        // add in y direction
        last_cell = [...field_container.querySelectorAll(".cell")].reverse()[0];
        for (let y = height - 1; y > max_y; y--) {
            for(let x = width - 1; x >= 0; x--) {
                const cell = create_filed_cell(x, y);
                last_cell.after(cell);
            }
        }
    });
}

function create_filed_cell(x_pos, y_pos) {
    const cell = document.createElement("DIV");
    cell.className = "cell";
    cell.setAttribute("data-x_pos", x_pos);
    cell.setAttribute("data-y_pos", y_pos);
    return cell;
}

function remove_cells(width, height) {

    field_containers.forEach(field => {
        [...field.querySelectorAll(".cell")]
            .filter(cell => cell.dataset.x_pos >= width || cell.dataset.y_pos >= height)
            .forEach(cell => cell.remove());
    })
}

function zoom() {
    const field_size = document.querySelector("#zoom").value || 64;
    document.documentElement.style.setProperty("--field-size", `${field_size}px`);
}

function select_material(material) {
    if (!material || (selected_material && material === selected_material)) { return; }

    selected_material && selected_material.classList.remove(class_selected);

    selected_material = material;
    material.classList.add(class_selected);
}
function select_layer(layer) {
    if (!layer || (selected_layer && layer === selected_layer)) { return; }

    selected_layer && selected_layer.classList.remove(class_selected);

    selected_layer = layer;
    layer.classList.add(class_selected);

    // adapt field
    document.querySelectorAll(".field-container").forEach(field => field.classList.remove(class_selected));
    document.querySelector(`.field-container--${ layer.dataset.index }`).classList.add(class_selected);
}

function set_material_on(cell_with_position) {
    if (!cell_with_position || !selected_material || !selected_layer) { return; }

    const cell = get_cell_of_selected_layer_in_same_position(cell_with_position);

    cell.style.backgroundImage = `url(${selected_material.querySelector("img").src})`;
    cell.dataset.material_id = selected_material.dataset.id;
}
function delete_material_on(cell_with_position) {
    if (!cell_with_position || !selected_material || !selected_layer) { return; }

    const cell = get_cell_of_selected_layer_in_same_position(cell_with_position);

    cell.style.backgroundImage = "";
    delete cell.dataset.material_id;
}

function get_field_of_selected_layer() {
    if (!selected_layer) { return undefined; }

    return document.querySelector(`.field-container--${ selected_layer.dataset.index }`);
}
function get_cell_of_selected_layer_in_same_position(cell_with_position) {
    if (!cell_with_position || !selected_material || !selected_layer) { return undefined; }

    const x = cell_with_position.dataset.x_pos;
    const y = cell_with_position.dataset.y_pos;

    const field_container = get_field_of_selected_layer();
    return field_container.querySelector(`[data-x_pos="${x}"][data-y_pos="${y}"]`);
}

function create_empty_field() {
    height = parseInt(field_height_input.value || 0);
    width = parseInt(field_width_input.value || 0);
    return Array.from({length: height}, () => Array.from({length: width}, () => null));
}

function submit() {
    const name = document.querySelector("#name").value;
    if (!name) {
        alert("Name missing");
        return;
    }

    const fields = [...document.querySelectorAll(".field-container")].reduce((acc, field) => {

        // get list of cells, map them to their material_ids (or null) and x/y positions
        const cells = [...field.querySelectorAll(".cell")].map(cell => ({
            material_id: parseInt(cell.dataset.material_id || 0) || null,
            x: parseInt(cell.dataset.x_pos),
            y: parseInt(cell.dataset.y_pos)
        }));

        // assign them to key = layer.id
        acc[field.dataset.layer_id] = cells;
        return acc;
    }, {});
    

    // fill 2D field
    const fields_2D = Object.entries(fields).reduce((acc, layer) => {
        const [layer_id, field] = layer;

        // convert linear field to 2D
        const field_2D = field.reduce((field_acc, cell) => {
            field_acc = field_acc || create_empty_field();

            field_acc[cell.y][cell.x] = cell.material_id;
            return field_acc;
        }, undefined);

        // assign it to key = layer_id
        acc[layer_id] = field_2D;
        return acc;
    }, {});
    console.log(fields_2D)

    post({ name, fields: fields_2D }) //, () => window.location.href = `/mining`);
}

function prepopulate_field() {
    const prepopulated_cells = [...document.querySelectorAll(".cell")].filter(cell => cell.hasAttribute("data-material_id"));
    const material_images = [...document.querySelectorAll(".material")]
        .reduce((acc, material) => {
            acc[material.dataset.id] = material.querySelector("img").src;
            return acc;
        }, {});
    prepopulated_cells.forEach(cell => cell.style.backgroundImage = `url(${material_images[cell.dataset.material_id]})`);
}

function toggle_field_border() {
    const border_toggle_checkbox = document.querySelector('#border-toggle');
    border_toggle_checkbox.classList.toggle('checked');

    const is_border = border_toggle_checkbox.classList.contains("checked");
    document.documentElement.style.setProperty("--field-border-width", `${is_border ? 1 : 0}px`);
}

function toggle_delete_mode() {
    const delete_toggle_checkbox = document.querySelector('#delete-toggle');
    delete_mode = delete_toggle_checkbox.classList.toggle('checked');
}

function update_unselected_field_opacity() {
    const opacity = document.querySelector('#unselected-field-opacity').value;
    document.documentElement.style.setProperty("--unselected-field-opacity", `${opacity}`);
}

function update_field_bg_color() {
    const bg_color = document.querySelector('#field-bg-color').value;
    document.documentElement.style.setProperty("--field-bg-color", `${bg_color}`);
}