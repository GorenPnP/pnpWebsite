/** (DEBUG) CONFIG */
const DISPLAY_LOS_FIELDS = true;
/** 1 ^= length of 1 cell */
const steps_line_of_sight = 0.25;

/** "PLAYER" | "ENEMY" */
let turn = "PLAYER";

const grid_size = JSON.parse(document.querySelector("#grid_size").innerHTML);


function fight_won() {
    return Pawn.get_enemies().length === 0;
}

function exit() {
    // update loot display
    document.querySelector("#loot-display").innerHTML = Object.values(Loot.acquired_loot)
        .sort((a, b) => a.item.name <= b.item.name ? -1 : 1)
        .map(loot => `<div class="item"><img src="${loot.item.icon_url}">${loot.num}x ${loot.item.name}</div>`)
        .join("");

    // loot in form
    document.querySelector("[name='loot']").value = JSON.stringify(
        Object.values(Loot.acquired_loot).reduce((acc, loot) => ({...acc, [loot.item.id]: loot.num}), {})
    );

    // display loot, save loot and let BE redirect
    document.querySelector("#exit-btn").click();
}


// enum PawnType {
//     PLAYER,
//     ENEMY
// }

// enum AttackType {
//     n, f, m
// }


class Cell {


    get classList() {
        return this.cell_tag.classList;
    }
    get pos() {
        return {x: parseInt(this.cell_tag.dataset.x), y: parseInt(this.cell_tag.dataset.y)}
    }
    get is_obstacle() {
        return this.cell_tag.dataset.obstacle === "";
    }
    get is_exit() {
        return this.cell_tag.dataset.exit === "";
    }
    get is_spawn() {
        return this.cell_tag.dataset.spawn === "";
    }
    get is_enemy_spawn() {
        return this.cell_tag.dataset.enemy_spawn === "";
    }
    constructor(cell_tag) {
        this.cell_tag = cell_tag;
        this.pawn = null;
        this.visible_pos = [];

        Cell.instances[this.pos.x] = {...(Cell.instances[this.pos.x] || {}), [this.pos.y]: this};        
    }

    is_blocked(include_pawns=false) {
        return this.is_obstacle || (!fight_won() && this.is_exit) || (include_pawns && !!this.pawn);
    }
    can_see(pos) {
        return this.visible_pos.some(p => p.x === pos.x && p.y === pos.y);
    }

    init_line_of_sight() {
        for (const cell of Cell.all()) {
    
            // calc dist between cells
            const dist = Cell.get_exact_distance(this, cell);
            const num_steps = (dist * 1.0) / steps_line_of_sight;
            let step = 0;
            let x, y, previous_cell_has_pawn = false, previously_blocked = false, fully_blocked = false;
            while (dist && Math.floor(num_steps) >= step) {
    
                // calc next position
                x = this.pos.x + 0.5 + (cell.pos.x - this.pos.x) * steps_line_of_sight * step / (dist * 1.0);
                y = this.pos.y + 0.5 + (cell.pos.y - this.pos.y) * steps_line_of_sight * step / (dist * 1.0);
    
                const passover_cell = Cell.get_cell({x: Math.floor(x), y: Math.floor(y)});
                if (passover_cell.is_blocked(false)) {
                    if (previously_blocked) fully_blocked = true;
                    previously_blocked = true;
                }
    
                if (previous_cell_has_pawn && !passover_cell.pawn) fully_blocked = true;
                if (!!passover_cell.pawn && !Cell.is_same_pos(passover_cell, this)) previous_cell_has_pawn = true;
    
                if (fully_blocked) { break; }

                step++;
            }
            
            if (!fully_blocked) { this.visible_pos.push(cell.pos); }
        }
    }

    static instances = {};

    static all() {
        return Object.values(Cell.instances).reduce((acc, row) => [...acc, ...Object.values(row)], []);
    }

    static get_cell(pos) {
        return Cell.instances[pos.x]?.[pos.y] || null;
    }

    static is_same_pos(a, b) {
        return a.pos.x === b.pos.x && a.pos.y === b.pos.y;
    }
    static get_exact_distance(a, b) {
        return Math.sqrt(Math.pow(a.pos.x - b.pos.x, 2) + Math.pow(a.pos.y - b.pos.y, 2));
    }
    static get_distance(a, b) {
        return Math.ceil(Cell.get_exact_distance(a, b));
    }

    static init_grid() {
        [...document.querySelectorAll("#grid .cell")].forEach((cell, i) => {
            cell.dataset.x = i % grid_size;
            cell.dataset.y = Math.floor(i/grid_size);
        
            new Cell(cell);
        });

        Cell.all().forEach(cell => cell.init_line_of_sight());
    }
}

class Pawn {
    visible_pos = [];
    /**
     * {
     *   weapons: {[type: AttackType]: {
     *      "accuracy": number,
     *      "damage": number,
     *      "crit_chance": number,
     *      "crit_damage": number,
     *      "min_range": number,
     *      "max_range": number,
     *   }},
     *   defense: number,
     *   difficulty: number,
     *   hp: number,
     *   wounded: 0,
     *   loot: {
     *       num: number,
     *       chance: number,
     *       item: { id: number, name: string, icon_url: string },
     *   }[],
     *   name: string,
     *   speed: number,
     *   sprite: string,
     * };
     */
    stats = {wounded: 0, steps_left: 0};
    has_attacked = false;
    is_killed = false;

    get pos() {
        const style = window.getComputedStyle(this.pawn_tag);
        const x = parseInt(style.getPropertyValue("--x"));
        const y = parseInt(style.getPropertyValue("--y"));
        return {x: isNaN(x) ? null : x, y: isNaN(y) ? null : y};
    }

    get cell() {
        return Cell.get_cell(this.pos);
    }

    get classList() {
        return this.pawn_tag.classList;
    }

    get steps_left() {
        return this.stats.steps_left;
    }
    set steps_left(steps) {
        this.stats.steps_left = steps;

        // update_steps_display
        this.pawn_tag.querySelector(".steps-left").innerText = steps ?  ""+steps : "";
    }

    constructor(type, stats, visualize_LOS=false) {
        // create html-tag
        const dummy = document.createElement("div");
        dummy.innerHTML = `<div class="pawn pawn--${type.toLowerCase()}">
            <div class="stats">
                <small class="difficulty">${Array.from({length: stats.difficulty || 0}, () => "★").join("")}</small>
                <div class="progress" role="progressbar" aria-label="Health bar" aria-valuenow="${stats.hp}" aria-valuemin="0" aria-valuemax="${stats.hp}">
                    <div class="progress-bar"></div>
                </div>
                <small class="steps-left"></small>
            </div>
            <img src="${stats.sprite}">
        </div>`;
        this.pawn_tag = dummy.firstChild;
        document.querySelector("#grid").appendChild(this.pawn_tag);
        dummy.remove();

        // assign all other initial fields
        this.type = type;
        this.visualize_LOS = visualize_LOS;

        this.aim_at = null;
        this.stats = {...this.stats, ...stats};
        if (stats.speed !== undefined && stats.speed !== null) this.stats.speed = stats.speed /100;
        this.update_health_bar();
        this.steps_left = this.stats.speed;

        // save instance ref on class
        this.id = Pawn.instances.push(this);
        this.pawn_tag.id = `pawn-${this.id}`;
    }

    can_attack(pos, from_cell=this.cell) {
        const {min_range, max_range} = Object.values(this.stats.weapons).reduce((acc, weapon) => ({
            min_range: Math.min(acc.min_range, weapon.min_range),
            max_range: Math.max(acc.max_range, weapon.max_range),
        }), {min_range: Infinity, max_range: 0});

        const dist = Cell.get_distance(from_cell, Cell.get_cell(pos));
        return min_range <= dist && dist <= max_range && from_cell.can_see(pos);
    }

    movable_to() {
        if (this.pos.x === null || this.pos.y === null) { return null; }

        return [
            {x: this.pos.x+1, y: this.pos.y},
            {x: this.pos.x, y: this.pos.y+1},
            {x: this.pos.x, y: this.pos.y-1},
            {x: this.pos.x-1, y: this.pos.y},
        ].filter(pos => !Cell.get_cell(pos).is_blocked(true));
    }

    move_to(pos) {
        const allowed_pos = this.movable_to();
        if (this.steps_left <= 0 || (allowed_pos !== null && !allowed_pos.some(p => p.x === pos.x && p.y === pos.y))) {
            alert(`${this.type} darf nicht auf (${pos.x}, ${pos.y})`);
            return;
        }

        if (this.cell) this.cell.pawn = null;
        Cell.get_cell(pos).pawn = this;
    
        this.pawn_tag.style.setProperty("--x", pos.x);
        this.pawn_tag.style.setProperty("--y", pos.y);

        this.steps_left--;
        this.update_line_of_sight();

        // update aim
        Pawn.instances
            .filter(pawn => pawn.aim_at === this)
            .forEach(pawn => pawn.aim(pawn.can_attack(this.pos) ? this : null))
        this.aim(this.aim_at && this.can_attack(this.aim_at.pos) ? this.aim_at : null);
    }

    update_line_of_sight(visualize=this.visualize_LOS) {
    
        // rm cell visualization marks
        document.querySelectorAll(`#grid .cell--visible.cell--visible--${this.id}`).forEach(cell => {
            cell.classList.remove(`cell--visible--${this.id}`);
            const has_other = cell.classList.values().some(cls => cls.startsWith(`cell--visible--`));
            if (!has_other) cell.classList.remove(`cell--visible`);
        });
            
        if (visualize && DISPLAY_LOS_FIELDS) {
            this.cell.visible_pos.forEach(pos => Cell.get_cell(pos).classList.add("cell--visible", `cell--visible--${this.id}`));
        }
    }

    aim(target_pawn = null) {

        // check if target_pawn is in range for weapons
        if (target_pawn && !this.can_attack(target_pawn.pos)) {
            alert("cannot attack", this.id, target_pawn.id)
            return;
        }

        this.aim_at = target_pawn;

        document.querySelectorAll(`#grid .LOS--wooble.LOS--wooble--${this.id}`).forEach(wooble => wooble.remove());
        document.querySelectorAll(`#grid .pawn--targeted.pawn--targeted--${this.id}`).forEach(pawn_tag => {
            pawn_tag.classList.remove(`pawn--targeted--${this.id}`);
            const has_other = pawn_tag.classList.values().some(cls => cls.startsWith(`pawn--targeted--`));
            if (!has_other) pawn_tag.classList.remove(`pawn--targeted`);
        });
    
        if (target_pawn) {
            target_pawn.classList.add("pawn--targeted", `pawn--targeted--${this.id}`);
    
            const cell_size = parseInt(window.getComputedStyle(document.querySelector("#grid")).getPropertyValue("--cell-size"));
    
            // calc dist between cells
            const dist = Cell.get_exact_distance(this.cell, target_pawn.cell);
            const num_steps = (dist * 1.0) / steps_line_of_sight;
            let step = 0;
            let {x, y} = {x: this.pos.x + .5, y: this.pos.y + .5};
            while (dist && Math.floor(num_steps) >= step) {
    
                // calc next position
                x += (target_pawn.pos.x - this.pos.x) / num_steps;
                y += (target_pawn.pos.y - this.pos.y) / num_steps;
    
                // add wooble
                const wooble = document.createElement("div");
                wooble.classList.add("LOS--wooble", `LOS--wooble--${this.id}`);
                wooble.style.top = `${y*cell_size}px`;
                wooble.style.left = `${x*cell_size}px`;
                document.querySelector("#grid").appendChild(wooble);
    
                step++;
            }
        }
    }

    attack() {
        if (!this.aim_at || this.has_attacked) { return; }
        this.has_attacked = true;
        
        const dist = Cell.get_distance(this.cell, this.aim_at.cell);
        let attack_vectors = Object.values(this.stats.weapons).filter(weapon => weapon.min_range <= dist && dist <= weapon.max_range);
        if (!attack_vectors?.length) {
            this.aim_at = null;
            alert("Not in reach, should not have happened")
            return;
        }

        let attack_with = attack_vectors[0];
        if (attack_vectors.length > 1) {
            // TODO ask player what to attack with
        }

        // TODO animate

        // TODO remove ammunition where necessary

        // dice rolls (w100)
        const attack_roll = Math.floor(1 + Math.random() * 100) - (100 - attack_with.accuracy);
        const defense_roll = Math.floor(1 + Math.random() * 100) + this.aim_at.stats.defense;

        // crit -> hits harder!
        if (attack_roll >= 100 - attack_with.crit_chance) {
            this.aim_at.inflict_damage(attack_with.damage);
            this.aim_at.inflict_damage(attack_with.damage * attack_with.crit_damage / 100);
            return;
        }

        // failure -> hits itself
        if (attack_roll < 0) return this.inflict_damage(attack_with.damage);

        // hit -> hits target
        if (defense_roll < attack_roll) return this.aim_at.inflict_damage(attack_with.damage);

        // miss -> nothing happens
        return this.aim_at.inflict_damage(0);
    }

    inflict_damage(amount) {
        this.stats.wounded += amount;
        this.update_health_bar();


        if (this.stats.wounded >= this.stats.hp) {
            Pawn.instances = Pawn.instances.filter(pawn => pawn.id !== this.id);
        }

        // animate amount wounded
        const particle = document.createElement("span");
        particle.classList.add("particle--wounded");
        particle.innerText = "- " + amount;
        this.pawn_tag.appendChild(particle);

        const timeout = parseInt(window.getComputedStyle(particle).getPropertyValue("--timeout") || "1000");
        setTimeout(() => {
            particle.remove();

            // die?
            if (this.stats.wounded >= this.stats.hp) {
                this.kill();
            }
        }, timeout -100);

    }

    update_health_bar() {
        const percentage = Math.max(0, 100 * (this.stats.hp - this.stats.wounded) / this.stats.hp);

        this.pawn_tag.querySelector(".stats .progress").setAttribute("aria-valuenow", this.stats.hp - this.stats.wounded);
        const inner_bar = this.pawn_tag.querySelector(".stats .progress-bar");
        inner_bar.style.width = percentage +"%";
        inner_bar.classList.values().filter(cls => cls.startsWith("bg-")).forEach(cls => inner_bar.classList.remove(cls));

        if (percentage <= 25) return inner_bar.classList.add("bg-danger");
        if (percentage <= 50) return inner_bar.classList.add("bg-warning");
        return inner_bar.classList.add("bg-success");
    }

    kill() {
        if (this.is_killed) return;
        this.is_killed = true;

        Cell.all()
            .filter(cell => cell.pawn === this)
            .forEach(cell => cell.pawn = null);

        Pawn.instances
            .filter(pawn => pawn.aim_at === this)
            .forEach(pawn => pawn.aim(null));

        this.aim(null);
        Pawn.instances = Pawn.instances.filter(pawn => pawn.id !== this.id);

        if (this.type === "PLAYER") {
            confirm("game over");
            window.location.pathname = "/combat/";
        }
        if (this.type === "ENEMY") {
            // give loot
            new Loot(null, this.pos, this.stats.loot);

            // remove display of enemy
            this.pawn_tag.remove();
        }
    }

    static instances = [];

    static get_player() {
        return Pawn.instances.find(pawn => pawn.type === "PLAYER");
    }
    static get_enemies() {
        return Pawn.instances.filter(pawn => pawn.type === "ENEMY");
    }

    static init_pawns() {

        // spawn player
        const spawns = Cell.all().filter(cell => cell.is_spawn);
        const spawn = spawns[Math.floor(Math.random() * spawns.length)];
        const player_stats = JSON.parse(document.querySelector("#player_stats").innerHTML);
        new Pawn("PLAYER", player_stats, true).move_to(spawn.pos);

        // spawn enemies
        const enemy_spawns = Cell.all().filter(cell => cell.is_enemy_spawn);
        const enemies = [...JSON.parse(document.querySelector("#enemies").innerHTML)]
            .reduce((all_enemies, e) => {
                for (let i = 0; i < e.num; i++) all_enemies.push(e.enemy);
                return all_enemies;
            }, []);

            let potential_spawns = enemy_spawns;
            for (const enemy of enemies) {

                // refresh spawns
                let dist = 1;
                const max_dist = Cell.get_distance(
                    Cell.get_cell({x: 0, y: 0}),
                    Cell.get_cell({x: grid_size-1, y: grid_size-1}),
                );
                while (!potential_spawns.length && dist <= max_dist) {
                    potential_spawns = enemy_spawns
                        .map(cell => cell.visible_pos
                            .map(pos => Cell.get_cell(pos))
                            .filter(neighbor => !neighbor.pawn && Cell.get_distance(cell, neighbor) === dist)
                        )
                        .reduce((spawns, cells) => [...spawns, ...cells], [])
                        .filter((cell, cell_index, spawns) => cell_index === spawns.findIndex(s =>  Cell.is_same_pos(cell, s)));

                    dist++;
                }


                const spawn_index = Math.floor(Math.random() * potential_spawns.length);
                new Pawn("ENEMY", enemy).move_to(potential_spawns[spawn_index].pos);
                potential_spawns = potential_spawns.filter((_, i) => i !== spawn_index);

            };
    }
}

class Loot {
    /**
     * loot_table: {
     *   num: number,
     *   chance: number,
     *   item: {
     *     id: number,
     *     name: string,
     *     icon_url: string,
     *   }
     * }[]
     */
    loot_table = [];

    get classList() {
        return this.cell_tag.classList;
    }
    get pos() {
        const style = window.getComputedStyle(this.loot_tag);
        const x = parseInt(style.getPropertyValue("--x"));
        const y = parseInt(style.getPropertyValue("--y"));
        return {x: isNaN(x) ? null : x, y: isNaN(y) ? null : y};
    }

    get cell() {
        return Cell.get_cell(this.pos);
    }
    constructor(sprite_url="", pos, loot_table) {
        this.id = Loot.next_id++;
        Loot.instances.push(this);

        // create html-tag
        const dummy = document.createElement("div");
        dummy.innerHTML = `<div class="loot" id="loot-${this.id}" style="--x: ${pos.x}; --y: ${pos.y}"><img src="${sprite_url || '/static/combat/img/loot.png'}"></div>`;
        this.loot_tag = dummy.firstChild;
        document.querySelector("#grid").appendChild(this.loot_tag);
        dummy.remove();

        this.loot_table = loot_table;
    }

    /**
     * acquired_loot: {[item_id: number]: {num: number, item: {id: number, name: string, icon_url: string}}}
     */
    static acquired_loot = {};
    static instances = [];
    static next_id = 1;

    collect() {
        this.loot_tag.remove();
        Loot.instances = Loot.instances.filter(loot => loot.id !== this.id);

        // acquire loot
        const loots = this.loot_table.filter(loot_table => loot_table.chance >= 1 + Math.floor(Math.random() * 100));

        loots.forEach(loot => Loot.acquired_loot[loot.item.id] = {item: loot.item, num: (Loot.acquired_loot[loot.item.id]?.num || 0) + loot.num});
        const html_tags = Object.values(Loot.acquired_loot)
            .map(loot => `<div class="loot-item" style="background-icon: url('${loot.item.icon_url}')">${loot.num}</div>`)
            .join("");

        const dummy = document.createElement("div");
        dummy.innerHTML = html_tags;
        document.querySelector("#loot").innerHTML = "";
        dummy.childNodes.forEach(item => document.querySelector("#loot").appendChild(item));
        dummy.remove();
    }
}



// init game
const player_weapons = JSON.parse(document.querySelector("#player_stats").innerHTML).weapons;
if (!Object.keys(player_weapons).length) {
    confirm("Keine Waffen ausgewählt!");
    window.location.pathname = "/combat/";
}
const weapon_types = Object.keys(player_weapons);
const weapon_fields = Object.keys(Object.values(player_weapons)[0]);
document.querySelector("#attack-table").innerHTML = `
    <thead><tr><th></th><th>${weapon_types.join("</th><th>")}</th></tr></thead>
    <tbody>${weapon_fields.map(field => `<tr><td>${field.replace("_", " ")}:</td><td>${weapon_types.map(type => player_weapons[type][field]).join("</td><td>")}</td></tr>`).join("")}</tbody>`;

Cell.init_grid();
Pawn.init_pawns();
player_turn();





// move player with arrows & WASD
document.addEventListener('keydown', function(event) {
    if ([38, 87, 39, 68, 37, 65, 40, 83].includes(event.keyCode)) event.preventDefault();

    const player = Pawn.get_player();
    if (event.repeat || turn !== "PLAYER" || player.steps_left <= 0) { return; }

    
    let new_pos = player.pos;
    if ([38, 87].includes(event.keyCode)) new_pos.y -= 1;   // up
    if ([39, 68].includes(event.keyCode)) new_pos.x += 1;   // right
    if ([37, 65].includes(event.keyCode)) new_pos.x -= 1;   // left
    if ([40, 83].includes(event.keyCode)) new_pos.y += 1;   // down

    // move player
    if (player.movable_to().some(p => p.x === new_pos.x && p.y === new_pos.y)) {
        player.move_to(new_pos);
        document.querySelector("#turn_overview--speed").innerHTML = `${player.steps_left} Schritt/e`;
    }

    // get loot
    const loot = Loot.instances.find(l => l.pos.x === player.pos.x && l.pos.y === player.pos.y);
    if (loot) loot.collect();

    // exit?
    if (fight_won() && player.cell.is_exit) exit();

    // is turn over?
    if (player.steps_left <= 0 && player.has_attacked) { enemy_turn(); }
});

// target visible enemy with mouse
document.querySelector("#grid").addEventListener("mousemove", function(event) {
    if (turn !== "PLAYER") { return; }

    const pawn_id = parseInt(event.target.closest(".pawn--enemy")?.id.replace("pawn-", "")) || null;
    const enemy = Pawn.get_enemies().find(enemy => enemy.id === pawn_id);
    const player = Pawn.get_player();

    player.aim(enemy && player.can_attack(enemy.pos) ? enemy : null);
});

// attack targeted enemy or loot
document.querySelector("#grid").addEventListener("click", function(event) {
    if (turn !== "PLAYER") { return; }

    const pawn_id = parseInt(event.target.closest(".pawn--enemy")?.id.replace("pawn-", "")) || null;
    const enemy = Pawn.get_enemies().find(enemy => enemy.id === pawn_id);
    const player = Pawn.get_player();

    if (enemy && player.aim_at === enemy && !player.has_attacked) {
        player.attack();

        document.querySelector("#turn_overview--attack").innerHTML = `0 Angriffe`;
    }

    if (player.steps_left <= 0 && player.has_attacked) { enemy_turn(); }
});



function player_turn() {
    turn = "PLAYER";
    Pawn.instances.forEach(pawn => {
        pawn.has_attacked = false;
        pawn.steps_left = pawn.type === turn ? pawn.stats.speed : 0;
    });
    document.querySelector("#turn_overview--speed").innerHTML = `${Pawn.get_player().steps_left} Schritt/e`;
    document.querySelector("#turn_overview--attack").innerHTML = `1 Angriff`;

    document.querySelector("#btn-end_player_turn").classList.remove("disabled");
}
async function enemy_turn() {
    document.querySelector("#btn-end_player_turn").classList.add("disabled");

    turn = "ENEMY";
    Pawn.instances.forEach(pawn => {
        pawn.has_attacked = false;
        pawn.steps_left = pawn.type === turn ? pawn.stats.speed : 0;
    });

    const player = Pawn.get_player();

    for (const enemy of Pawn.get_enemies().sort((a,b) => b.stats.speed - a.stats.speed || b.stats.difficulty - a.stats.difficulty)) {

        while(enemy.steps_left) {
            if (enemy.can_attack(player.pos)) { break; }

            const movable_cells = enemy.movable_to()
                .map(pos => Cell.get_cell(pos))
                .sort((a, b) => Cell.get_distance(a, player.cell) - Cell.get_distance(b, player.cell));

            // find cell to attack player
            const attack_cells = movable_cells.filter(cell => enemy.can_attack(player.pos, cell));
            const move_to_cell = attack_cells.length ? attack_cells[0] : (movable_cells.length ? movable_cells[0] : null);
            if (!move_to_cell) { break; }
    
            if (!attack_cells.length && Cell.get_distance(move_to_cell, player.cell) > Cell.get_distance(enemy.cell, player.cell)) { break; }
            enemy.move_to(move_to_cell.pos);
            await delay(200);
        }

        if (enemy.can_attack(player.pos)) {
            // aim
            enemy.aim(player);
        
            // attack
            enemy.attack();
            await delay(200);
        }

        while(enemy.steps_left) {
            const movable_cells = enemy.movable_to()
                .map(pos => Cell.get_cell(pos))
                .sort((a, b) => Cell.get_distance(b, player.cell) - Cell.get_distance(a, player.cell));

            // find cell where player can not attack back
            const attack_cells = movable_cells.filter(cell => !player.can_attack(cell.pos));
            const move_to_cell = attack_cells.length ? attack_cells[0] : (movable_cells.length ? movable_cells[0] : null);
            if (!move_to_cell) { break; }
    
            enemy.move_to(move_to_cell.pos);
            await delay(200);
        }
    }

    player_turn();
}


function delay(milliseconds) {
    return new Promise(resolve => {
        setTimeout(resolve, milliseconds);
    });
}