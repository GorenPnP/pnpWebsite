const initial_fert = parseInt(document.querySelector("#fert_pool").innerHTML || 0);
const initial_sp = parseInt(document.querySelector("#sp_pool").innerHTML);
const initial_wp = parseInt(document.querySelector("#wp_pool").innerHTML || 0);
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

    // handle wp
    const wp = wp_spent() - spent_wp;
    if (document.querySelector("#wp_calc")) {
        let text = " WP übrig";
        if (wp === 0) { text = `<b>${initial_wp}</b>` + text; }
        else if (wp <= initial_wp) { text = `<del>${initial_wp}</del> <b>${initial_wp-wp}</b>` + text; }
        else { text = `<b>${wp-initial_wp}</b> WP zu viel ausgegeben!`; }

        document.querySelector("#wp_calc").innerHTML = text;
    }

    // handle fert / sp
    const initial = payment_method === "points" ? initial_fert : initial_sp;
    const fert = fert_chosen() - spent_fert;
console.log(payment_method)
    if (payment_method === "points") {
        // sp
        document.querySelector("#sp_calc").innerHTML = `<b>${initial_sp}</b> SP`;

        // points
        const payment_name = `Fertigkeit${Math.abs(initial - fert) !== 1 ? "en" : ''}`;
        let text = `${payment_name} übrig`;

        if (fert === 0) { text = `<b>${initial_fert}</b> ${text}`; }
        else if (fert <= initial_fert) { text = `<del>${initial_fert}</del> <b>${initial_fert-fert}</b> ` + text; }
        else { text = `<b>${fert-initial_fert}</b> ${payment_name} zu viel ausgegeben!`; }

        document.querySelector("#fert_calc").innerHTML = text;
    } else {
        // points
        const fert_slug = `Fertigkeit${Math.abs(initial) !== 1 ? "en" : ''}`
        document.querySelector("#fert_calc").innerHTML = `<b>${initial_fert}</b> ${fert_slug} übrig`;

        // sp
        let text = "SP";

        if (fert === 0) { text = `<b>${initial_sp}</b> ${text}`; }
        else if (fert <= initial_sp) { text = `<del>${initial_sp}</del> <b>${initial_sp-fert}</b> ` + text; }
        else { text = `<b>${fert-initial_sp}</b> SP zu viel ausgegeben!`; }

        document.querySelector("#sp_calc").innerHTML = text;
    }
    
    // disable submit button?
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

    // start on min value for spF
    document.querySelectorAll(".spezial-input").forEach(input => {
        // save val
        input.dataset.old = input.value;
        
        // register change listener
        input.addEventListener("input", function() {
            if (!this.dataset.old?.length && this.value) {
                this.value = this.min || 0;
            }
            this.dataset.old = this.value;
        })
    });

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
    calc_pools();
});
