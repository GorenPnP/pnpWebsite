const fert_pool_tag = document.querySelector('#fert_pool');
const wp_pool_tag = document.querySelector('#wp_pool');

let initial_fert_pool = parseInt(fert_pool_tag.textContent);
let initial_wp_pool = parseInt(wp_pool_tag.textContent);

let fertigkeiten = [];

let selected_ferts = [];

function calc_initial_pools() {

    // get/calc values
    const chosen_ferts = fertigkeiten
        .map(fert => fert.punkte)
        .filter(punkte => punkte !== null);

    const wp = chosen_ferts
        .reduce((sum, wp_points) => sum + wp_points, 0);

    const num_ferts = chosen_ferts.length;

    initial_fert_pool = parseInt(fert_pool_tag.textContent) + num_ferts;
    initial_wp_pool = parseInt(wp_pool_tag.textContent) + wp;
}

function calc() {

    // get/calc values
    const values = [...document.querySelectorAll('[type="number"]')]
        .map(tag => parseInt(tag.value))
        .filter(val => !isNaN(val) && val);

    const wp = values
        .reduce((sum, wp_points) => sum + wp_points, 0);

    const ferts = values.length;

    // update stats
    fert_pool_tag.textContent = initial_fert_pool - ferts;
    wp_pool_tag.textContent = initial_wp_pool - wp;

    selected_ferts = [...document.querySelectorAll('[type="number"]')]
        .filter(tag => !isNaN(parseInt(tag.value)) && parseInt(tag.value))
        .map(tag => {
            const id = tag.parentNode.parentNode.dataset.id;

            return {
                kind_of_fert: id.replace(/\d+/, ''),
                pk: parseInt(/\d+/.exec(id)),
                wp: parseInt(tag.value)
            };
        });

    // update submit button
    document.querySelector("#submit").disabled = fert_pool_tag.textContent != 0 ||  wp_pool_tag.textContent != 0;
}

function submit() {
    post({selected: selected_ferts});
}


document.addEventListener("DOMContentLoaded", function() {
    fertigkeiten = JSON.parse(document.querySelector("#fertigkeiten").textContent);
    calc_initial_pools();
    calc();

    document.querySelectorAll("#table [data-contains='content'] [type='number']").forEach(fert => fert.addEventListener("input", function() {
        // min of 0
        const val = parseInt(this.value);
        if (!isNaN(val) && val < 0) this.value = 0;

        // adapt to changes of values
        calc();
    }));
})
