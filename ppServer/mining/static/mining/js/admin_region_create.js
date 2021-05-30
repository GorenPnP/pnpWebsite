// prepopulated layers. Change/add which Layers should be added on load of this page
const values = [
    {
        index: -5,
        name: "Blocks",
        is_collidable: true,
        is_breakable: true
    },
    {
        index: -4,
        name: "Underground",
        is_collidable: true,
        is_breakable: true
    },
    {
        index: -3,
        name: "Decorations solid",
        is_collidable: true,
        is_breakable: true
    },
    {
        index: -2,
        name: "Decorations",
        is_collidable: false,
        is_breakable: true
    },
    {
        index: -1,
        name: "Weather",
        is_collidable: false,
        is_breakable: false
    },
    {
        index: 0,
        name: "Charakter",
        is_collidable: false,
        is_breakable: false
    },
    {
        index: 1,
        name: "Blocks",
        is_collidable: true,
        is_breakable: true
    },
    {
        index: 2,
        name: "Underground",
        is_collidable: true,
        is_breakable: true
    },
    {
        index: 3,
        name: "Decorations solid",
        is_collidable: true,
        is_breakable: true
    },
    {
        index: 4,
        name: "Decorations",
        is_collidable: false,
        is_breakable: true
    },
    {
        index: 5,
        name: "Weather",
        is_collidable: false,
        is_breakable: false
    },
]

document.addEventListener("DOMContentLoaded", () => {
    // Did already run this script. Maybe the input wasn't complete on submit, therefore coming here again.
    // Prevent adding everything again.
    if (document.querySelector("#layer_set-1")) { return; }

    wait_for("#layer_set-group .add-row a", add_rows);
});

/**
 * adds a row in LAYERS for each entry in "values"
 */
function add_rows() {
    const add_link = document.querySelector("#layer_set-group .add-row a")

    // clone from example and add to DOM-tree
    values.forEach((value, row_id) => {
        add_link.click();
        wait_for(`#layer_set-${row_id}`, set_values_into_row, [row_id, value]);
    });
}

/**
 * sets "values" into input fields of row with "row_id"
 * @param {*} row_id 
 * @param {*} values 
 */
function set_values_into_row(row_id, values) {
    const row = document.querySelector(`#layer_set-${row_id}`);

    // change ids of elements which have a value
    Object.entries(values).forEach(([id, value]) => {
        const field = row.querySelector(`#id_layer_set-${row_id}-${id}`);

        field.type === "checkbox" ? field.checked = value : field.value = value;
    });
}


/**
 * Waits until element determined by "identifier" appears in the DOM and executes "func" with parameters "args"
 */
function wait_for(identifier, func, args=[]) {
    setTimeout(() => {
        if (!document.querySelector(identifier)) {  return wait_for(identifier); }

        func(...args);
    }, 100)
}
