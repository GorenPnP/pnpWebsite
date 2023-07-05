const initial_fert = parseInt(document.querySelector("#fert_pool")?.innerHTML || 0);
const initial_sp = parseInt(document.querySelector("#sp_pool").innerHTML);
const initial_wp = parseInt(document.querySelector("#wp_pool")?.innerHTML || 0);
const spent_fert = fert_chosen();
const spent_wp = wp_spent();
let payment_method = document.querySelector("#payment-method").value;


function fert_chosen() {
    const spezial = [...document.querySelectorAll(`.spezial-input`)].filter(tag => tag.value).length;
    const wissen = [...document.querySelectorAll(`.wissen-input`)].filter(tag => tag.value.length).length;

    return spezial + wissen;
}
function wp_spent() {
    const spezial = [...document.querySelectorAll(`.spezial-input`)]
        .filter(tag => tag.value.length)
        .map(tag => parseInt(tag.value))
        .reduce((sum, wp) => sum + wp + 5, 0);

    const wissen = [...document.querySelectorAll(`.wissen-input`)]
        .filter(tag => tag.value.length)
        .map(tag => parseInt(tag.value))
        .reduce((sum, wp) => sum + wp, 0);

    return wissen + spezial;
}

function calc_pools() {
    payment_method = document.querySelector("#payment-method").value;
    document.querySelectorAll(".spent").forEach(tag => tag.innerHTML = '');

    // handle wp
    const wp = wp_spent() - spent_wp;
    document.querySelector("#spent_wp").innerHTML = wp > 0 ? ` (-${wp})` : '';

    // handle fert / sp
    const fert = fert_chosen() - spent_fert;
    document.querySelector(payment_method === "points" ? "#spent_fert" : "#spent_sp").innerHTML = fert > 0 ? ` (-${fert})` : '';
    
    
    const initial = payment_method === "points" ? initial_fert : initial_sp;
    document.querySelector("[type=submit").disabled = fert > initial || wp > initial_wp || (wp === 0 && fert === 0);
}

function highlight_rows() {
    const highlight_class = "highlight";

    [...document.querySelectorAll(".main-container tbody tr")].forEach(tr_tag => {
        const spezial = tr_tag.querySelector(`.spezial-input`);
        spezial && parseInt(spezial.value) >= -5 ? tr_tag.classList.add(highlight_class) : tr_tag.classList.remove(highlight_class);
        if (spezial) { return; }
        
        const is_selected = tr_tag.querySelector(`.wissen-input`)?.value.length;
        is_selected ? tr_tag.classList.add(highlight_class) : tr_tag.classList.remove(highlight_class);
    });
}

document.addEventListener("DOMContentLoaded", function () {

    // update pools on change of inputs
    document.querySelectorAll(`.wissen-input, .spezial-input`).forEach(tag => tag.addEventListener("input", function() {
        highlight_rows();
        calc_pools();
    }));
    // update pools on change of payment method
    document.querySelector(`#payment-method`).addEventListener("change", function() {
        highlight_rows();
        calc_pools();
    });
    highlight_rows();
});
