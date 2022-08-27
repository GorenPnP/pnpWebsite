var attrs = {};
attributes = {};
initial_ap = 0;
initializing = true;

const clamp = (min, number, max) => Math.min(Math.max(number, min), max);

function init() {
    ap_pool_tag = document.querySelector("#ap_pool");
    initial_ap = parseInt(ap_pool_tag.innerHTML);

    data = JSON.parse(document.querySelector("#attributes").textContent);
    attributes = data.reduce((acc, attr) => {
        acc[attr.pk] = attr;
        return acc;
    }, {});

    calc_ap_pool();

    // gathering data for initial_ap is done
    initializing = false;
}

function clamp_value_on_change(tag) {
    const tr_parent = tag.parentNode.parentNode;
    const id = tr_parent.dataset.id;
    const isAktuell = tr_parent.querySelector("[type='number']") === tag;
    let maxValue = Number.MAX_VALUE;
    if (isAktuell) {
        maxValue = attributes[id]["max"] + attributes[id]["max_ap"] - attributes[id]["aktuell"];
    }

    const value = clamp(0, parseInt(tag.value) || 0, maxValue);

    tag.value = value;
    attributes[id][isAktuell ? "aktuell_ap" : "max_ap"] = value;
}

function calc_ap_pool() {
    let sum = 0;

    tr_tags = document.querySelectorAll("[data-id]");
    for (const tr of tr_tags) {
        const attribute = attributes[tr.dataset.id];
        const result = [...tr.querySelectorAll("td")].reverse()[0];

        const aktuell_sum = attribute.aktuell + attribute.aktuell_ap;
        const max_sum = attribute.max + attribute.max_ap;
        result.textContent = `${aktuell_sum}/${max_sum}`;

        sum += attribute.aktuell_ap + attribute.max_ap*2;
    }

    const curr_ap = initial_ap - sum;
    if (!initializing) {
        ap_pool_tag.innerHTML = curr_ap;
    } else {
        initial_ap += sum;
    }
    // handle submit button
    document.querySelector("#submit").disabled = ap_pool_tag.innerHTML != 0;
}


function submit() {
    post(attributes)
}

document.addEventListener("DOMContentLoaded", function () {
    init();

    document.querySelectorAll("[type='number']").forEach(tag => tag.addEventListener("input", function() {
        clamp_value_on_change(this);
        calc_ap_pool();
    }));
});
