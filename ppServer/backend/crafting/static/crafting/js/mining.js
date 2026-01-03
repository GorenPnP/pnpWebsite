// A cross-browser requestAnimationFrame
// See https://hacks.mozilla.org/2011/08/animating-with-javascript-from-setinterval-to-requestanimationframe/
const requestAnimFrame = (function() {
    return window.requestAnimationFrame    ||
        window.webkitRequestAnimationFrame ||
        window.mozRequestAnimationFrame    ||
        window.oRequestAnimationFrame      ||
        window.msRequestAnimationFrame     ||
        function(callback){
            window.setTimeout(callback, 1000 / 60);
        };
})();

/** tool_types: string[] */
const tool_types = JSON.parse(document.querySelector("#tool_types").innerHTML);
/** tools: {[tool_type: string]: HTMLElement} */
const tools = tool_types.reduce((acc, tool_type) => {
    const fastest_tool = [...document.querySelectorAll(`.tool`)]
        .filter(tag => tag.dataset.type.split(", ").includes(tool_type))
        .reduce((max, tool) => {
            if (!max || parseInt(max.dataset.speed) < parseInt(tool.dataset.speed)) { return tool; }
            return max;
        }, null);

    return { ...acc, [tool_type]: fastest_tool}
}, {});

/** blocks: {[block_id: number]: {
    icon: string,
    name: string,
    effective_tool: tool_types as string-concat with ', ',
    hardness: number,
    
    duration: number,               // after calling init()
    toolType: tool_type as string   // after calling init()
}} */
const blocks = JSON.parse(document.querySelector("#blocks").innerHTML);
/** items: {[item_id: number]: {
    id: number,
    name: string,
    icon_url: string,
}} */
const items = Object.values(blocks).reduce((acc, block) => {
    block.drops
        .map(drop => drop.item)
        .forEach(droppable_item => acc[droppable_item.id] = droppable_item);
    return acc;
}, {});
/** drops: {[item_id: number]: number} */
let drops = {};

/** block_pool: number */
const block_pool = JSON.parse(document.querySelector("#block_pool").innerHTML);
/** block_pool: number */
const block_count = parseInt(document.querySelector("#block_count").innerHTML);

/** perks: {
    item: number,
    effect: string,
    tool_type__name: string | null,
    effect_increment: {[stufe: number]: number},
    stufe_wooble_price: {[stufe: number]: number},
}[] */
const perks = JSON.parse(document.querySelector("#perks").innerHTML);
/** multidrop_percentage: {[tool_type & '': string]: number} */
const multidrop_percentage = tool_types.reduce((acc, type) => ({...acc, [type]: 0.0}), {});
/** spread_percentage: {[tool_type & '': string]: number} */
const spread_percentage = tool_types.reduce((acc, type) => ({...acc, [type]: 0.0}), {});
const save_spinner = document.querySelector("#save-spinner");

/** active_block_index: number | null  // null if not currently mining */
let active_block_index = null;
/** current_block: Block[] (s. blocks) */
let current_block = Array.from({length: block_count});
/** passed_block_duration: number[] */
let passed_block_duration = Array.from({length: block_count});
let time_elapsed = 0;


function mining_set_block() {
    // update mining time for finished block
    time_elapsed += current_block[active_block_index]?.duration || 0;

    for (let i = 0; i < block_count; i++) {
        const block_tag = document.querySelector(`#mining .mining-btn#mining-btn--${i}`)

        // randomly get new block
        const block = blocks[block_pool[Math.floor(Math.random() * block_pool.length)]];

        // set block display
        block_tag.querySelector(".mining-btn__block-texture").src = block.icon;
        block_tag.querySelector(".mining-btn__block-texture").alt = block.name;

        // update block mining duration
        current_block[i] = block;
        passed_block_duration[i] = 0;
    }
}

function mining_get_drops(index) {
    _mining_get_drops_of_block(index);

    /* mining spread */

    // indices of all possible blocks
    let other_block_indices = current_block.map((block, i) => ({
            index: i,
            pick: i !== index &&
                block.toolType === current_block[index].toolType &&
                block.hardness <= current_block[index].hardness
        }))
        .filter(e => e.pick)
        .map(e => e.index);

    // how many blocks?
    let runs = Math.floor(spread_percentage[current_block[index].toolType] / 100) + (Math.random() * 100 < spread_percentage[current_block[index].toolType] % 100 ? 1 : 0);

    // spread to blocks
    while(runs-- && other_block_indices.length) {
        const other_index = other_block_indices[Math.floor(Math.random() * other_block_indices.length)];

        other_block_indices = other_block_indices.filter(i => i !== other_index);
        _mining_get_drops_of_block(other_index);
    }

    // update inventory
    mining_update_drops();
}

function _mining_get_drops_of_block(index) {
    let num_block_drops = 0;
    for (const drop of current_block[index].drops) {
        let runs = 1 + Math.floor((multidrop_percentage[current_block[index].toolType] || 0) / 100) + (Math.random() * 100 < (multidrop_percentage[current_block[index].toolType] || 0) % 100 ? 1 : 0);

        while (runs--) {

            // no luck, sorry
            if (Math.ceil(Math.random() * 100) > drop.chance) { continue; }

            // add drop
            drops[drop.item.id] = (drops[drop.item.id] || 0) + 1;

            // add particle
            const particle = document.createElement("span");
            particle.classList.add("particle--drop");
            if (runs) particle.classList.add("particle--multidrop");
            particle.innerText = "+ " + drop.item.name;
            const delay = num_block_drops++ * 150;
            particle.style.animationDelay = delay + "ms";
            document.querySelector(`.mining-btn#mining-btn--${index}`).appendChild(particle);

            const timeout = parseInt(window.getComputedStyle(particle).getPropertyValue("--timeout") || "1000");
            setTimeout(() => particle.remove(), delay + timeout -100);
        }
    }
}

// The mining loop
let lastTime;
function mine() {
    if (active_block_index === null) {
        lastTime = null;
        return;
    }

    let now = Date.now();
    let dt = lastTime ? now - lastTime : 0.0; // delta time in ms

    passed_block_duration[active_block_index] += dt;
    if (passed_block_duration[active_block_index] >= current_block[active_block_index].duration) {
        mining_get_drops(active_block_index);
        mining_set_block();
        mining_update_progressbar();

    } else {
        mining_update_progressbar(active_block_index);
    }

    // set active tool
    document.querySelectorAll(".tool.tool--active").forEach(tool => tool.classList.remove("tool--active"));
    tools[current_block[active_block_index].toolType]?.classList.add("tool--active");


    lastTime = now;
    requestAnimFrame(mine);
};

function start_mining(event) {
    if (!event || event.button !== 0 || !event.isTrusted) { return; }

    active_block_index = parseInt(event.target.closest(".mining-btn").id.replace("mining-btn--", ""));

    mine();
}

function stop_mining() {
    active_block_index = null;
}

function mining_update_progressbar(index=null) {

    const indices = index !== null ? [index] : Array.from({length: block_count}, (_, i) => i);

    for (let i of indices) {

        // progress in %
        const progress = Math.floor(passed_block_duration[i] / current_block[i].duration *100);
        const progress_tag = document.querySelector(`#mining .mining-btn#mining-btn--${i} .progress`);
        const progressbar_tag = progress_tag.querySelector(".progress-bar");
        progress_tag.setAttribute("aria-valuenow", progress);
        progressbar_tag.style.width =  `${progress}%`;

        // hardness-color
        let color = "--bs-dark-rgb";
        if (current_block[i].hardness < 10) color = "--bs-info-rgb";
        else if (current_block[i].hardness < 50) color = "--bs-success-rgb";
        else if (current_block[i].hardness < 200) color = "--bs-warning-rgb";
        else if (current_block[i].hardness < 1000) color = "--bs-danger-rgb";
        else color = "--bs-dark-rgb";

        progressbar_tag.style.setProperty("--bs-dark-rgb", `var(${color})`);
    }
}

function mining_update_drops() {
    for (const [item_id, num] of Object.entries(drops)) {
        const item = items[item_id];

        // get or create displayed html-element
        let element = document.querySelector(`#inventory .grid--drops [data-drop-id="${item.id}"]`);
        if (!element) {
            const dummy = document.createElement("div");
            dummy.innerHTML = `<div class=item data-drop-id="${item.id}" onclick="openDetails(${item.id})">
                <img src="${item.icon_url}" alt="${item.name}" loading="lazy">
                <span class="num">0</span>
            </div>`;
            element = dummy.firstChild;
            document.querySelector(`#inventory .grid--drops`).appendChild(element);
            dummy.remove();
        }

        // update num (or remove if 0)
        num ? element.querySelector(".num").innerText = num : element.remove();
    }
}

function save_progress(on_success=() => {}, on_error=() => {}) {
    // nothing to save? -> Skip
    if (!Object.values(drops).some(num => num)) {
        on_success();
        return;
    }

    save_spinner.classList.add("visible");
    
    const save_drops = JSON.parse(JSON.stringify(drops));
    const save_time = time_elapsed;
    post(
        { drops: save_drops, time: save_time },
        _ => {
            save_spinner.classList.remove("visible");
            
            // TODO make atomic
            for (const item_id of Object.keys(save_drops)) {
                const mined_num = save_drops[item_id];

                // remove saved drops from local ones
                drops[item_id] -= mined_num;

                // add saved drops to inventory:
                const item = items[item_id];

                // get or create displayed html-element
                let element = document.querySelector(`#inventory .grid--current-inv [data-drop-id="${item.id}"]`);
                if (!element) {
                    const dummy = document.createElement("div");
                    dummy.innerHTML = `<div class="item" data-drop-id="${item.id}" onclick="openDetails(${item.id})">
                        <img src="${item.icon_url}" alt="${item.name}" loading="lazy">
                        <span class="num">0</span>
                    </div>`;
                    element = dummy.firstChild;
                    document.querySelector(`#inventory .grid--current-inv`).appendChild(element);
                    dummy.remove();
                }

                // update its num
                element.querySelector(".num").innerText = parseInt(element.querySelector(".num").innerText) + mined_num;
            }
            time_elapsed -= save_time;

            // update drops' display
            mining_update_drops();

            on_success();
	    },
        _ => {
            save_spinner.classList.remove("visible");

            // notify on erroneous (Auto-)save
            const dummy = document.createElement("div");
            dummy.innerHTML =
                `<div class="alert alert-danger d-flex align-items-center justify-content-between" role="alert">
                    <span><b>Fehler:</b> Dein Fortschritt konnte nicht gespeichert werden. Bist du offline?</span>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Schließen"></button>
                </div>`;

            const container = document.querySelector(".main-container .infos");
            container.appendChild(dummy.firstChild);
            dummy.remove();

            on_error();
        }
    )
}

function init() {
    const perk_speed = tool_types.reduce((acc, type) => ({...acc, [type]: 0.0}), {});

    /* init perks */

    const get_perk_number = (effect, tool_type) => {
        return perks
            .filter(perk => perk.effect === effect && (!perk.tool_type__name || (tool_type && perk.tool_type__name.split(", ").includes(tool_type))))
            .map(perk => parseInt(document.querySelector(`#shop .grid--perks [data-drop-id="${perk.item}"] .num__effect`).dataset.effect))
            .reduce((sum, num) => sum + num, 0);
    };

    for (const type of ["", ...tool_types]) {

        /* tool speed */

        // get perk speed
        perk_speed[type] = get_perk_number("speed", type);
        if (type && perk_speed[type] && tools[type]) {

            // get tool
            const corresponding_tool = tools[type];
    
            // display perk speed
            corresponding_tool.querySelector(".num").innerHTML = `${corresponding_tool.dataset.speed} <span class="text-success"> +${perk_speed[type]}</span>`;
        }


        /* multidrop */
        multidrop_percentage[type] = get_perk_number("multidrop", type);

        /* spread */
        spread_percentage[type] = get_perk_number("spread", type);
    }


    /* init_blocks */

    for (const block of Object.values(blocks)) {

        // update preferred tool
        const fastest_tool = block.effective_tool.split(", ")
            .filter(tool_type => tool_types.includes(tool_type))
            .map(tool_type => ({
                tool_type,
                tool_tag: tools[tool_type],
            }))
            .reduce((max, tool) => {
                const num = parseInt(tool.tool_tag?.dataset.speed) || 0;
                if (num < max.max) { return max; }
                return {...tool, max: num};
            }, {tool_type: "", tool_tag: null, max: 0});
        block.toolType = fastest_tool.tool_type;

        // update block mining duration
        const toolSpeed = Math.max(fastest_tool.max, 1);
        const perkSpeed = perk_speed[fastest_tool.tool_type] || 0;
        block.duration = block.hardness / (toolSpeed + perkSpeed) * 3000; // in ms
    }
}

function perk_buy_stufe(item_id) {
    // save everything first before reloading page
    
    save_progress(on_success = () => {
        save_spinner.classList.add("visible");

        post(
            { perk_item: item_id },
            _ => {
                save_spinner.classList.remove("visible");
                location.reload();
            },
            error => {
                save_spinner.classList.remove("visible");
                alert(error.response.data.message);
            }
        );
    });
}


// init perks, blocks & more
init();

// init mining block
mining_set_block();
mining_update_progressbar();

// set autosave
const min_in_ms = 1000 * 60;
setInterval(save_progress, 5 * min_in_ms);

// prevent dragging of images
document.querySelectorAll(".main-container img").forEach(img => img.ondragstart = () => false);

// prevent contextmenu on hold on mobile
document.querySelectorAll(".mining-btn, .mining-btn *").forEach(tag => {
    tag.addEventListener("contextmenu", e => e.preventDefault());
});