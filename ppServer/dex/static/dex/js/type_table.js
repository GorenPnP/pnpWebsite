const attacks = [];
const victims = [];
let table;


function draw_show() {
    // draw marks
    table.querySelectorAll("th, td").forEach(cell => cell.classList.remove("show", "show--attack", "show--victim"));

    attacks.forEach(attack => 
        table.querySelectorAll(`[data-type-attack="${attack}"]`).forEach(cell => cell.classList.add("show", "show--attack"))
    );
    victims.forEach(victim => 
        table.querySelectorAll(`[data-type-victim="${victim}"]`).forEach(cell => cell.classList.add("show", "show--victim"))
    );

    // calc score
    const score_prep =
        [...table.querySelectorAll(".show--attack.show--victim")]
        .map(cell => cell.innerHTML.trim())
        .reduce((acc, cell) => {
            acc[cell]++;
            return acc;
        }, {"x": 0, "+": 0, "-": 0});
    
    let score = score_prep["x"] ? 0 : 1;
    if (score_prep["+"]) { score *= 2* score_prep["+"]; }
    if (score_prep["-"]) { score /= 2* score_prep["-"]; }
    document.querySelector("#efficiency").innerHTML = ""+score;
}

document.addEventListener("DOMContentLoaded", () => {
    table = document.querySelector("table");

    // select 1 type
    table.querySelectorAll(".tag").forEach(type => type.addEventListener("click", function(e) {
        const type = e.target.closest("td, th").dataset.typeAttack || e.target.closest("td, th").dataset.typeVictim;

        if (attacks.includes(type) && victims.includes(type)) {
            attacks.splice(attacks.indexOf(type), 1);
            victims.splice(victims.indexOf(type), 1);
        } else {
            attacks.push(type);
            victims.push(type);
        }
        draw_show();
    }));

    // select 1 cell inside
    table.querySelectorAll("table :where(th, td):not(.tag)").forEach(type => type.addEventListener("click", function(e) {
        const attack = parseInt(e.target.dataset.typeAttack) || null;
        const victim = parseInt(e.target.dataset.typeVictim) || null;

        if (attacks.includes(attack) && victims.includes(victim)) {
            attacks.splice(attacks.indexOf(attack), 1);
            victims.splice(victims.indexOf(victim), 1);
        } else {
            attacks.push(attack);
            victims.push(victim);
        }
        draw_show();
    }));

    
    // highlight table rows & cols on hover
    table.addEventListener("pointerover", function(e) {
        const attack = e.target.dataset.typeAttack;
        const victim = e.target.dataset.typeVictim;

        this.querySelectorAll("th, td").forEach(cell => cell.classList.remove("highlight", "highlight--attack", "highlight--victim"));
        this.querySelectorAll(`[data-type-attack="${attack}"]`).forEach(cell => cell.classList.add("highlight", "highlight--attack"));
        this.querySelectorAll(`[data-type-victim="${victim}"]`).forEach(cell => cell.classList.add("highlight", "highlight--victim"));
    });
});