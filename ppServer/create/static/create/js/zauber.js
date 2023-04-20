var initial_zauber = 0;


function zauber_chosen() {
    return document.querySelectorAll(`.zauber-input:checked`).length;
}
function calc_zauber() {
    const zauber_left = initial_zauber - zauber_chosen();
    document.querySelector("#zauber_pool").innerHTML = zauber_left;
    document.querySelector('[type="submit"]').disabled = zauber_left < 0;
}

function highlight_rows() {
    const highlight_class = "highlight";

    [...document.querySelectorAll(".main-container tbody tr")].forEach(tr_tag => {
        const is_selected = tr_tag.querySelector(".zauber-input:checked");
        is_selected ? tr_tag.classList.add(highlight_class) : tr_tag.classList.remove(highlight_class);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    // init ap-pool
    initial_zauber = parseInt(document.querySelector("#zauber_pool").innerHTML) + zauber_chosen();

    // adapt on checkbox-input
    document.querySelectorAll(".zauber-input").forEach(tag => tag.addEventListener("input", function() {
        highlight_rows();
        calc_zauber();
    }));
});
