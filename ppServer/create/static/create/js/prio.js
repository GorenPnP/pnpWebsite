document.addEventListener("DOMContentLoaded", () => {

    /** chosen fields, key is type (IP, AP, ...) */
    let selected_fields = {};

    const apDebt = document.querySelector("#ap-debt");
    const apLeft = document.querySelector("#ap-left");
    const apDebtText = document.querySelector("#ap-debt-text");
    const apLeftText = document.querySelector("#ap-left-text")
    const points = document.querySelector("#points")
    const pointText = document.querySelector("#point-text")
    const submit_btn  = document.querySelector("#submit");
    
    const num_cols = document.querySelectorAll("#priotable tr:first-child td:not([data-type='prio'])").length;
    const gfs_cost = parseInt(apDebt.innerText);
    const max_points = parseInt(points.innerText);
    const selected = 'selected';
    const blocked = 'blocked';


    function update_currencies() {

        /* ap cost */
        ap = gfs_cost - parseInt(/\d+/.exec(document.querySelector("#priotable td[data-type='ap'].selected")?.innerText || 0));
        apDebt.innerText = ap;
        apLeft.innerText = ap * -1;

        // display dept or ap left text?
        apDebtText.style.display = ap <= 0 ? "none" : "inline-block";
        apLeftText.style.display = ap <= 0 ? "inline-block" : "none";

        /* point cost */
        const costs = [...document.querySelectorAll("#priotable td.selected")].map(td => parseInt(td.closest("tr").querySelector(".prio--cost").innerText));
        points.innerText = max_points - costs.reduce((sum, cost) => sum + cost, 0);
        pointText.style.display = parseInt(points.innerText) === 0 ? "none" : "block";
    }
    update_currencies();


    /* start of event handlers */
    document.querySelectorAll("#priotable td:not([data-type='prio'])").forEach(td => {

        td.addEventListener('click', function () {

            // element is blocked or has no (numeral) content => do nothing
            this.classList.toggle(blocked, false);

            // update selected_fields with prio on selected or remove the key otherwise
            if (this.classList.toggle(selected)) {
                selected_fields[this.dataset.type] = this.closest("tr").querySelector(".prio--name").innerText;
            }
            else {
                delete selected_fields[this.dataset.type];
            }

            // handle blocked
            document.querySelectorAll(`#priotable td[data-type="${this.dataset.type}"]`).forEach(td => {
                // set class "blocked" if this has been selected
                if (td !== this) {
                    td.classList.toggle(blocked, this.classList.contains(selected));
                    td.classList.toggle(selected, false);
                }
        });

            // handle ap-debt/ap-left & points
            update_currencies();

            // form submittable?
            submit_btn.disabled = Object.keys(selected_fields).length !== num_cols || parseInt(apDebt.innerText) > 0 || parseInt(points.innerText) !== 0;
        });
    });

    submit_btn.form.addEventListener("submit", function(e) {
        e.preventDefault();
        post(selected_fields);
    })
});
