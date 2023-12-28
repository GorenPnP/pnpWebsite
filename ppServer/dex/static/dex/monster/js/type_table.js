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
    
    if (score_prep["x"]) { return document.querySelector("#efficiency").innerHTML = "0.00"; }
        
    
    const factor = score_prep["+"] - score_prep["-"];
    let score = 1;
    if (factor < 0) { score /= Math.pow(2, Math.abs(factor)); }
    else { score += (factor * 0.5); }

    document.querySelector("#efficiency").innerHTML = score.toFixed(2);
}

document.addEventListener("DOMContentLoaded", () => {
    table = document.querySelector("table");

    // select 1 type of victim
    table.querySelectorAll("th.tag").forEach(type => type.addEventListener("click", function(e) {
        const type = parseInt(e.target.closest("th").dataset.typeVictim);

        if (victims.includes(type)) {
            victims.splice(victims.indexOf(type), 1);
        } else {
            victims.push(type);
        }
        draw_show();
    }));
    // select 1 type of attack
    table.querySelectorAll("td.tag").forEach(type => type.addEventListener("click", function(e) {
        const type = parseInt(e.target.closest("td").dataset.typeAttack);

        if (attacks.includes(type)) {
            attacks.splice(attacks.indexOf(type), 1);
        } else {
            attacks.push(type);
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