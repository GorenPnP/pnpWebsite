let active_type = null;

const types = JSON.parse(document.querySelector("#cell_types").innerHTML);
const empty_type_object = types.find(t => t.pk === parseInt(document.querySelector("#empty_type_pk").innerHTML));

// init grid
const dummy = document.createElement("div");
JSON.parse(document.querySelector("#id_grid").value).forEach(cell => {
    dummy.innerHTML = `<button type="button" class="cell"
            data-type="${cell}"
            onpointerover="set_grid_cell(event)"
            onpointerdown="set_grid_cell(event)"
            oncontextmenu="return false;"
        ></button>`;
    document.querySelector("#grid").appendChild(dummy.firstChild);
});
dummy.remove();

// show grid cells with images/textual types for users
document.querySelectorAll("#grid .cell").forEach(cell => {
    set_grid_cell_to_type(cell, parseInt(cell.dataset.type));
});

// set sprites in toolbar buttons
types.filter(type_object => type_object.sprite)
    .forEach(type_object => document.querySelector(`#toolbar .cell--type[data-type='${type_object.pk}']`).style.backgroundImage = `url('${type_object.sprite}')`);

// set_active_type(); on first in toolbar
document.querySelector("#toolbar .cell--type").dispatchEvent(new Event("click"));

function set_grid_cell_to_type(cell, type) {
    const type_entry = types.find(t => t.pk === type);
    const img_url = type_entry?.sprite ? `url("${type_entry.sprite}")` : "";

    cell.style.backgroundImage = img_url;
    cell.innerText = img_url || !type_entry ? "" : type_entry.name;
    cell.dataset.type = type;
}

function set_active_type(event, type) {
    active_type = type;

    document.querySelectorAll("#toolbar .cell--type").forEach(cell => cell.classList.remove("cell--active"));
    event.target.classList.add("cell--active");
}

function set_grid_cell(event) {
    const cell = event.target;
    let type = null;
    if (event.buttons === 1) { type = active_type; }
    if (event?.buttons === 2) { type = empty_type_object?.pk || null; }
    if (type === null) { return; }

    set_grid_cell_to_type(cell, type);
}

function previewFile({ target }, type) {
    const type_object = types.find(t => t.pk === type);
    const file    = target.files[0];
    const reader  = new FileReader();
  
    reader.onloadend = () => {
        // save for later
        type_object.sprite = reader.result;

        // set toolbar button
        document.querySelector(`#toolbar .cell--type[data-type='${type_object.pk}']`).style.backgroundImage = `url('${type_object.sprite}')`;
        
        // set grit cells
        document.querySelectorAll(`#grid .cell[data-type="${type_object.pk}"]`).forEach(cell =>
            set_grid_cell_to_type(cell, type_object.pk)
        );
    };
    
    if (file) { reader.readAsDataURL(file); }
}

function intercept_submit() {
    const cells = [...document.querySelectorAll("#grid .cell")].map(cell => parseInt(cell.dataset.type));
    document.querySelector("input[name='grid']").value = JSON.stringify(cells);
}
