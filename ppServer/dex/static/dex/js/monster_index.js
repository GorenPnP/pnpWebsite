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

function filter_and_sort() {
    
    // collect filter & sort directions
    const filter = {
        name: (name.value || "").toLowerCase() || null,
        typ: (document.querySelector("#filter-typ .dropdown-item.active").dataset.value || "").toLowerCase() || null,
        known: JSON.parse(document.querySelector("#filter-known .dropdown-item.active").dataset.value),
    }
    const sort = document.querySelector("#sort .dropdown-item.active").dataset.value || null;


    // apply filter for visibility of monsters
    Array.from(document.querySelectorAll(".monster.card"))
        .map(monster => { monster.classList.remove("hidden"); return monster; })
        .filter(monster =>
            (filter.name && !monster.querySelector(".monster__name").innerHTML.toLowerCase().includes(filter.name)) ||
            (filter.typ && !monster.querySelector(".monster__types").innerHTML.toLowerCase().includes(filter.typ)) ||
            (filter.known !== null && monster.classList.contains("monster--dummy") == filter.known)
        )
        .forEach(monster => monster.classList.add("hidden"));

    // apply sort for sorting of monsters
    const list = document.querySelector("#monster-list");
    [...list.children]
        .sort((a, b) => {
            if (!sort) { return parseInt(/\d+/.exec(a.querySelector(".monster").id)) - parseInt(/\d+/.exec(b.querySelector(".monster").id)); }

            if (sort.startsWith("name")) {
                const a_name = a.querySelector(".monster__name").innerHTML.toLowerCase();
                const b_name = b.querySelector(".monster__name").innerHTML.toLowerCase();
                
                if (sort == "name asc") { return a_name > b_name ? -1 : (a_name === b_name ? 0 : 1); }
                if (sort == "name desc") { return a_name < b_name ? -1 : (a_name === b_name ? 0 : 1); }
            }
            
            if (sort.startsWith("rang")) {
                const a_rank = parseInt(a.querySelector(".monster").dataset.rank) || null;
                const b_rank = parseInt(b.querySelector(".monster").dataset.rank) || null;
                
                if (sort == "rang asc") { return a_rank - b_rank; }
                if (sort == "rang desc") { return b_rank - a_rank; }
            }
        })
        .forEach(node => list.appendChild(node));
}