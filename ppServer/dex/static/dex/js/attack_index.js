// option in filter-dropdowns
document.querySelectorAll(".filter-container .dropdown-item").forEach(btn => btn.addEventListener("click", function() {
    
    // set siblings to inactive
    this.closest(".dropdown-menu").querySelectorAll(".active").forEach(el => {
        el.classList.remove("active");
        el.setAttribute("aria-active", false);
    });

    // set this to active
    this.classList.add("active");
    this.setAttribute("aria-active", true);

    // set button-filter
    const btn = this.closest(".dropdown").querySelector(".btn.dropdown-toggle");
    btn.classList.toggle("active", this.innerHTML !== "X");
    btn.setAttribute("aria-active", this.innerHTML !== "X");

    filter_and_sort();
}));


/******* name ********/

const name = document.querySelector("#name");
const clear_name = document.querySelector("#clear-name");
// clear-btn for name input
clear_name.addEventListener("click", function() {
    name.value = "";
    name.dispatchEvent(new InputEvent("input"));
});
// don't close dropdown on clear-btn click
document.querySelector("#name-btn-container").addEventListener("click", function(e) {
    e.stopImmediatePropagation();
});
// update btn-activeness on name input
name.addEventListener("input", function() {
    clear_name.disabled = !this.value;
    const btn = this.closest(".dropdown").querySelector(".btn.dropdown-toggle");
    btn.classList.toggle("active", !!this.value);
    btn.setAttribute("aria-active", !!this.value);

    filter_and_sort();
});


/******* cost ********/

const cost = document.querySelector("#cost");
const clear_cost = document.querySelector("#clear-cost");
// clear-btn for name input
clear_cost.addEventListener("click", function() {
    cost.value = "";
    cost.dispatchEvent(new InputEvent("input"));
});
// don't close dropdown on clear-btn click
document.querySelector("#cost-btn-container").addEventListener("click", function(e) {
    e.stopImmediatePropagation();
});
// update btn-activeness on name input
cost.addEventListener("input", function() {
    clear_cost.disabled = !this.value;
    const btn = this.closest(".dropdown").querySelector(".btn.dropdown-toggle");
    btn.classList.toggle("active", !!this.value);
    btn.setAttribute("aria-active", !!this.value);

    filter_and_sort();
});


/***** other ******/

function filter_and_sort() {
    
    // collect filter & sort directions
    const filter = {
        name: (name.value || "").toLowerCase() || null,
        cost: !isNaN(parseInt(cost.value)) ? parseInt(cost.value) : null,
        typ: (document.querySelector("#filter-typ .dropdown-item.active").dataset.value || "").toLowerCase() || null,
        stat: (document.querySelector("#filter-stat .dropdown-item.active").dataset.value || "") || null,
    }
    const sort = document.querySelector("#sort .dropdown-item.active").dataset.value || null;


    // apply filter for visibility of attacks
    Array.from(document.querySelectorAll(".attack.card"))
        .map(attack => { attack.parentNode.classList.remove("hidden"); return attack; })
        .filter(attack =>
            (filter.name && !attack.querySelector(".attack__name").innerHTML.toLowerCase().includes(filter.name)) ||
            (filter.cost !== null && parseInt(attack.querySelector(".attack__cost span").innerHTML) > filter.cost) ||
            (filter.typ && ![...attack.querySelectorAll(".attack__types div")].some(type_tag => type_tag.textContent.toLowerCase() === filter.typ)) ||
            (filter.stat && ![...attack.querySelectorAll(".attack__vector .stat-icon")].some(stat_tag => stat_tag.dataset.stat === filter.stat))
        )
        .forEach(attack => attack.parentNode.classList.add("hidden"));

    // apply sort for sorting of attacks
    const list = document.querySelector("#attack-list");
    [...list.children]
        .sort((a, b) => {
            const a_name = a.querySelector(".attack__name").innerHTML.toLowerCase();
            const b_name = b.querySelector(".attack__name").innerHTML.toLowerCase();

            if (!sort || sort == "name asc") { return a_name < b_name ? -1 : (a_name === b_name ? 0 : 1); }
            if (sort == "name desc") { return a_name > b_name ? -1 : (a_name === b_name ? 0 : 1); }
        })
        .forEach(node => list.appendChild(node));
}