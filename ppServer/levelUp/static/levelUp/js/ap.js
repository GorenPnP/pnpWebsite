let initial_ap = 0;


function ap_spent() {
    const ap_aktuell = [...document.querySelectorAll(`.aktuell-input`)]
        .map(tag => parseInt(tag.value) || 0)
        .reduce((sum, ap) => sum + ap, 0);
    
    const ap_max = [...document.querySelectorAll(`.max-input`)]
        .map(tag => parseInt(tag.value) || 0)
        .reduce((sum, ap) => sum + ap, 0);

    return ap_aktuell + 2* ap_max;
}
function calc_ap_pool() {
    const ap = initial_ap - ap_spent();
    document.querySelector("#ap_pool").innerHTML = ap;
    document.querySelector('[type="submit"]').disabled = ap < 0;
}

function update_result(tr_tag) {

    const aktuell = 
        (parseInt(tr_tag.querySelector(".aktuell-fix")?.innerHTML) || 0) +
        (parseInt(tr_tag.querySelector(".aktuell-input").value) || 0);
    const max =
        (parseInt(tr_tag.querySelector(".max-fix")?.innerHTML) || 0) +
        (parseInt(tr_tag.querySelector(".max-input").value) || 0);

    tr_tag.lastChild.innerHTML = `${aktuell} / ${max}`;
}

document.addEventListener("DOMContentLoaded", function () {
    // init ap-pool
    initial_ap = parseInt(document.querySelector("#ap_pool").innerHTML) + ap_spent();

    // adapt aktuell-input max on max-input change
    document.querySelectorAll("[type='number'].max-input").forEach(max_tag => max_tag.addEventListener("input", function() {
        const id = this.dataset.id;
        const max =
            (parseInt(document.querySelector(`[data-id="${id}"].max-fix`)?.innerHTML) || 0) +
            (parseInt(this.value) || 0) -
            (parseInt(document.querySelector(`[data-id="${id}"].aktuell-fix`)?.innerHTML) || 0);

        document.querySelector(`[data-id="${id}"].aktuell-input`).setAttribute("max", max);

        update_result(this.parentNode.parentNode.parentNode);
        calc_ap_pool();
    }));
    
    // update ap-pool on change of aktuell-input
    document.querySelectorAll("[type='number'].aktuell-input").forEach(aktuell_tag => aktuell_tag.addEventListener("input", function() {
        update_result(this.parentNode.parentNode.parentNode);
        calc_ap_pool();
    }));
});
