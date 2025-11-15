const initial_sp = parseInt(document.querySelector("#initial_sp").innerHTML);
const konzentration_input = document.querySelector("input#id_konzentration");
let max_box = null;

// konzentration
konzentration_input?.addEventListener("input", update_display);

// skilltree
document.querySelectorAll("table input[type='checkbox']:disabled").forEach(check => check.parentNode.addEventListener("click", function() {
    document.querySelectorAll("table input[type='checkbox']:not(:disabled)").forEach(box => box.checked = false);
}));

document.querySelectorAll("table input[type='checkbox']").forEach(check => check.addEventListener("input", function() {

    // uncheck max only
    if (this === max_box) {
        this.checked = false;
        const checked_boxes = [...document.querySelectorAll("table input[type='checkbox']:checked")].reverse();
        max_box = checked_boxes.length ? checked_boxes[0] : null;

        return update_display();
    }

    // changed other than max_box
    max_box = this;

    // unselect all
    [...document.querySelectorAll("table input[type='checkbox']")]
    .forEach(box => box.checked = box.disabled);
    
    // select all lower & clicked
    let lower = true;
    [...document.querySelectorAll("table input[type='checkbox']")]
        .filter(box => {
            if (box === max_box) { lower = false; }
            
            return !box.disabled && (lower || box === max_box);
        })
        .forEach(box => box.checked = true);

    return update_display();
}));

// update pools & submit-btn
function update_display() {
    const sp_spent = [...document.querySelectorAll("table input[type='checkbox']:checked:not(:disabled)")]
        .map(box => parseInt(box.closest("tr").querySelector(".sp").innerHTML))
        .reduce((sum, sp) => sum + sp, 0) + (konzentration_input ? (konzentration_input.value - konzentration_input.min) / 2 : 0);

    document.querySelector("#sp_pool").innerHTML = sp_spent ? `<del>${initial_sp}</del> <b>${initial_sp-sp_spent}</b>` : `<b>${initial_sp}</b>`;
    document.querySelector("#sub-btn").disabled = initial_sp < sp_spent;
}