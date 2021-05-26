var char_layer_index;

var selected_layer;
var selected_material;

function initSidebars() {

    // init globals
    canvas = document.querySelector("canvas");
    ctx = canvas.getContext("2d");

    char_layer_index = JSON.parse(document.querySelector("#char-layer-index").innerHTML);

    // material bar listeners
    document.querySelectorAll('.materialgroup')
        .forEach(group => group.querySelector('.groupname').addEventListener('click', () => select_materialgroup(group)));
    document.querySelectorAll('.material')
        .forEach(material => material.addEventListener('click', () => select_material(material)));

    // layer bar listeners
    document.querySelectorAll('.layer')
        .forEach(layer => layer.addEventListener('click', () => select_layer(layer)));

    // submit listener
    document.querySelector(".button--ok").addEventListener("click", submit);


    // create initial status
    // select first in bars
    select_materialgroup(document.querySelector('.materialgroup'));
    select_layer(document.querySelector('.layer'));
}


// HELPERS //



// MATERIAL BAR CALLBACKS //

function select_materialgroup(materialgroup_tag) {

    document.querySelectorAll(`.materialgroup.${class_selected}`).forEach(tag => tag.classList.remove(class_selected));
    materialgroup_tag.classList.add(class_selected);

    select_material(materialgroup_tag.querySelector('.material'));

    if (materialgroup_tag.classList.contains("materialgroup--character")) {
        document.querySelectorAll(`.materialgroup--character`).forEach(tag => tag.style.display = "block");
        document.querySelectorAll(`.materialgroup--noncharacter`).forEach(tag => tag.style.display = "none");
    } else {
        document.querySelectorAll(`.materialgroup--noncharacter`).forEach(tag => tag.style.display = "block");
        document.querySelectorAll(`.materialgroup--character`).forEach(tag => tag.style.display = "none");
    }
}

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
    if (!selected_layer || old_layer_is_char_layer !== new_layer_is_char_layer) {
        select_materialgroup(document.querySelector(!new_layer_is_char_layer ? ".materialgroup--noncharacter" : ".materialgroup--character"));
    }

    selected_entities.clear();

    selected_layer = layer;
    layer.classList.add(class_selected);
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
