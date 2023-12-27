// write number in boobles
document.querySelectorAll(".booble").forEach((booble, i) => booble.innerHTML = i+1);

// get amount of polls
const amount_polls = parseInt(document.querySelector("#amount_polls").innerHTML);

// disable sub-rangchanges btn
document.querySelectorAll(".btn-check").forEach(stat_checkbox => stat_checkbox.addEventListener("input", function(e) {
    document.querySelector("#stat-sub-btn").disabled = document.querySelectorAll(".btn-check:checked").length != amount_polls;
}));

// auto-roll
document.querySelector("#auto-roll-btn").addEventListener("click", function() {
    const stat_checkboxes = document.querySelectorAll(".btn-check");

    // get values to prep pool
    const weights = {
        base: parseInt(document.querySelector("#weight_base").innerHTML),
        skilled: parseInt(document.querySelector("#weight_skilled").innerHTML),
        trained: parseInt(document.querySelector("#weight_trained").innerHTML),
    };
    const skilled = JSON.parse(document.querySelector("#skilled").innerHTML).split(" ").map(stat => stat.trim()).filter(stat => stat);
    const trained = JSON.parse(document.querySelector("#trained").innerHTML).split(" ").map(stat => stat.trim()).filter(stat => stat);

    // construct pool
    let stat_pool = JSON.parse(document.querySelector("#all_stats").innerHTML).reduce((acc, stat) => {
        let i = weights.base;
        i += skilled.includes(stat) ? weights.skilled : 0;
        i += trained.includes(stat) ? weights.trained : 0;
        while (i--) { acc.push(stat); }

        return acc;
    }, []);

    // poll
    polls = new Set()
    while (stat_pool.length && polls.size < amount_polls) {
        const index = Math.floor(Math.random() * stat_pool.length);
        polls.add(stat_pool[index]);

        stat_pool = stat_pool.filter(stat => !polls.has(stat));
    }

    // set poll result & dis-/enable stuff
    stat_checkboxes.forEach(box => box.checked = polls.has(box.name));
    this.disabled = true;
    document.querySelector("#stat-sub-btn").disabled = false;
});