let initial_fp = 0
let initial_fg = 0


function fp_spent() {
    return [...document.querySelectorAll(`.fp-input`)]
        .map(tag => parseInt(tag.value) || 0)
        .reduce((sum, fp) => sum + fp, 0);
}
function fg_spent() {
    return [...document.querySelectorAll(`.fg-input`)]
        .map(tag => parseInt(tag.value) || 0)
        .reduce((sum, fg) => sum + fg, 0) / 3;
}

function calc_fp_fg_pools() {
    const fp = initial_fp - fp_spent();
    document.querySelector("#fp_pool").innerHTML = fp;

    const fg = initial_fg - fg_spent();
    document.querySelector("#fg_pool").innerHTML = fg;

    document.querySelector('[type="submit"]').disabled = fp < 0 || fg < 0;
}

function update_result(tr_tag) {

    let sum =
        (parseInt(tr_tag.querySelector(".attr_sum").innerHTML) || 0) +
        (parseInt(tr_tag.querySelector(".fp-fix")?.innerHTML) || 0) +
        (parseInt(tr_tag.querySelector(".fp-input").value) || 0) +
        (parseInt(tr_tag.querySelector(".fg-fix")?.innerHTML) || 0) +
        (parseInt(tr_tag.querySelector(".fg-input")?.value) || 0);

    tr_tag.lastChild.innerHTML = `${sum}`;
}

document.addEventListener("DOMContentLoaded", function () {
    // init fp/fg-pools
    initial_fp = parseInt(document.querySelector("#fp_pool").innerHTML) + fp_spent();
    initial_fg = parseInt(document.querySelector("#fg_pool").innerHTML) + fg_spent();

    
    // update pools on change of input
    document.querySelectorAll("[type='number'].fp-input").forEach(input_tag => input_tag.addEventListener("input", function() {
        update_result(this.parentNode.parentNode.parentNode);
        calc_fp_fg_pools();
    }));
    document.querySelectorAll("[type='number'].fg-input").forEach(input_tag => input_tag.addEventListener("input", function() {
        
        document.querySelectorAll(`[data-id="${this.dataset.id}"].fg-input`).forEach(input_tag => {
            input_tag.value = this.value;
            update_result(input_tag.parentNode.parentNode.parentNode);
        });
        calc_fp_fg_pools();
    }));
});