let initial_fert = 0;
let initial_wp = 0;


function fert_chosen() {
    return [...document.querySelectorAll(`.wissen-input, .spezial-input`)].filter(tag => parseInt(tag.value) || 0).length;
}
function wp_spent() {
    return [...document.querySelectorAll(`.wissen-input, .spezial-input`)]
        .map(tag => parseInt(tag.value) || 0)
        .reduce((sum, wp) => sum + wp, 0);
}

function calc_pools() {
    const fert = initial_fert - fert_chosen();
    document.querySelector("#fert_pool").innerHTML = fert;
    
    const wp = initial_wp - wp_spent();
    document.querySelector("#wp_pool").innerHTML = wp;
    
    document.querySelector("[type=submit").disabled = fert < 0 || wp < 0;
}

function highlight_rows() {
    const highlight_class = "highlight";

    [...document.querySelectorAll(".main-container tbody tr")].forEach(tr_tag => {
        const is_selected = parseInt(tr_tag.querySelector(`.wissen-input, .spezial-input`).value);
        is_selected ? tr_tag.classList.add(highlight_class) : tr_tag.classList.remove(highlight_class);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    // init pools
    initial_fert = parseInt(document.querySelector("#fert_pool").innerHTML) + fert_chosen();
    initial_wp = parseInt(document.querySelector("#wp_pool").innerHTML) + wp_spent();

    
    // update ap-pool on change of aktuell-input
    document.querySelectorAll(`.wissen-input, .spezial-input`).forEach(tag => tag.addEventListener("input", function() {
        highlight_rows();
        calc_pools();
    }));
    highlight_rows();
});
