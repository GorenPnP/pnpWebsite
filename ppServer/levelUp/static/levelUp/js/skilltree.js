const initial_sp = parseInt(document.querySelector("#initial_sp").innerHTML);


document.querySelectorAll("table input[type='checkbox']:disabled").forEach(check => check.parentNode.addEventListener("click", function() {
    document.querySelectorAll("table input[type='checkbox']:not(:disabled)").forEach(box => box.checked = false);
}));

document.querySelectorAll("table input[type='checkbox']").forEach(check => check.addEventListener("input", function() {
    
    // unselect all
    [...document.querySelectorAll("table input[type='checkbox']")]
    .forEach(box => box.checked = box.disabled);
    
    // select all lower & clicked
    let lower = true;
    const sp_spent = [...document.querySelectorAll("table input[type='checkbox']")]
        .filter(box => {
            if (box === this) { lower = false; }
            
            return !box.disabled && (lower || box === this);
        })
        .map(box => {
            box.checked = true;
            return parseInt(box.closest("tr").querySelector(".sp").innerHTML);
        })
        .reduce((sum, sp) => sum + sp, 0);

    // update pools & submit-btn
    document.querySelector("#sp_pool").innerHTML = sp_spent ? `<del>${initial_sp}</del> <b>${initial_sp-sp_spent}</b>` : `<b>${initial_sp}</b>`;

    document.querySelector("#sub-btn").disabled = initial_sp < sp_spent;
}));
