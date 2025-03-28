const block_pool = JSON.parse(document.querySelector("#block_pool").innerHTML);
const blocks = JSON.parse(document.querySelector("#blocks").innerHTML);
const items = Object.values(blocks).reduce((acc, block) => {
    block.drops
        .map(drop => drop.item)
        .forEach(droppable_item => acc[droppable_item.id] = droppable_item);
    return acc;
}, {});

const mining_img = document.querySelector("#mining-btn__block-texture");
const mining_hardness = document.querySelector("#mining-btn__hardness");
const save_spinner = document.querySelector("#save-spinner");
const mining_progressbar = document.querySelector("#mining .progress");

let current_block;
let hardness_left = 0;
let drops = {};

// A cross-browser requestAnimationFrame
// See https://hacks.mozilla.org/2011/08/animating-with-javascript-from-setinterval-to-requestanimationframe/
const requestAnimFrame = (function(){
    return window.requestAnimationFrame       ||
        window.webkitRequestAnimationFrame ||
        window.mozRequestAnimationFrame    ||
        window.oRequestAnimationFrame      ||
        window.msRequestAnimationFrame     ||
        function(callback){
            window.setTimeout(callback, 1000 / 60);
        };
})();
let total_block_duration = 0;
let passed_block_duration = 0;
let currently_mining_flag = false;
let stop_mining_flag = false;

function mining_set_block() {

    // randomly get new block
    current_block = blocks[block_pool[Math.floor(Math.random() * block_pool.length)]];

    // set block display
    mining_img.src = current_block.icon;
    mining_img.alt = current_block.name;

    // update preferred tool
    let type;
    if (current_block.effective_pick) type = "pick"
    else if (current_block.effective_axe) type = "axe"
    else type = "shovel"

    document.querySelectorAll(".tool.tool--active").forEach(tool => tool.classList.remove("tool--active"));
    const tool = document.querySelector(`.tool[data-type="${type}"]`);
    tool?.classList.add("tool--active");

    // update block mining duration
    const tool_speed = Math.max(parseInt(tool?.dataset.speed) || 0, 1);
    passed_block_duration = 0;
    total_block_duration = current_block.hardness / (tool_speed+1) * 3000 // in ms
}

function mining_get_drops() {
    let num_block_drops = 0;
    for (const drop of current_block.drops) {
        // no lock, sorry
        if (Math.ceil(Math.random() * 100) > drop.chance) { continue; }
        
        // add drop
        drops[drop.item.id] = (drops[drop.item.id] || 0) + 1;

        // add particle
        const particle = document.createElement("span");
        particle.classList.add("particle--drop");
        particle.innerText = "+ " + drop.item.name;
        const delay = num_block_drops++ * 150;
        particle.style.animationDelay = delay + "ms";
        document.querySelector("#mining-btn").appendChild(particle);

        const timeout = parseInt(window.getComputedStyle(particle).getPropertyValue("--timeout") || "1000");
        setTimeout(() => particle.remove(), delay + timeout -100);
    }

    // update inventory
    mining_update_drops();
}


// The mining loop
let lastTime;
function start_mining() {
    if (stop_mining_flag) {
        stop_mining_flag = false;
        currently_mining_flag = false;
        lastTime = null;
        return;
    }
    currently_mining_flag = true;

    let now = Date.now();
    let dt = lastTime ? now - lastTime : 0.0; // delta time in ms

    passed_block_duration += dt;
    if (passed_block_duration >= total_block_duration) {
        mining_get_drops();
        mining_set_block();
    }

    mining_update_progressbar();

    lastTime = now;
    requestAnimFrame(start_mining);
};

function stop_mining() {
    stop_mining_flag = currently_mining_flag;
}

function mining_update_progressbar() {

    // progress in %
    const mining_progress = Math.floor(passed_block_duration / total_block_duration *100);
    mining_progressbar.setAttribute("aria-valuenow", mining_progress);
    mining_progressbar.querySelector(".progress-bar").style.width =  `${mining_progress}%`;

    // hardness-color
    let color = "--bs-dark-rgb";
    if (current_block.hardness < 10) color = "--bs-info-rgb";
    else if (current_block.hardness < 50) color = "--bs-success-rgb";
    else if (current_block.hardness < 200) color = "--bs-warning-rgb";
    else if (current_block.hardness < 1000) color = "--bs-danger-rgb";
    else color = "--bs-dark-rgb";

    mining_progressbar.querySelector(".progress-bar").style.setProperty("--bs-dark-rgb", `var(${color})`);
}

function mining_update_drops() {
    for (const [item_id, num] of Object.entries(drops)) {
        const item = items[item_id];

        // get or create displayed html-element
        let element = document.querySelector(`#inventory .grid--drops [data-drop-id="${item.id}"]`);
        if (!element) {
            const dummy = document.createElement("div");
            dummy.innerHTML = `<div class=item data-drop-id="${item.id}" onclick="openDetails(${item.id})">
                <img src="${item.icon_url}" alt="${item.name}">
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

function save_progress() {
    // nothing to save? -> Skip
    if (!Object.values(drops).some(num => num)) { return; }

    save_spinner.classList.add("visible");
    
    const save_drops = JSON.parse(JSON.stringify(drops));
    post(
        { drops: save_drops },
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
                        <img src="${item.icon_url}" alt="${item.name}">
                        <span class="num">0</span>
                    </div>`;
                    element = dummy.firstChild;
                    document.querySelector(`#inventory .grid--current-inv`).appendChild(element);
                    dummy.remove();
                }

                // update its num
                element.querySelector(".num").innerText = parseInt(element.querySelector(".num").innerText) + mined_num;
            }

            // update drops' display
            mining_update_drops();
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
        }
    )
}


// init mining block
mining_set_block();
mining_update_progressbar();

// autosave
const min_in_ms = 1000 * 60;
setInterval(save_progress, 5 * min_in_ms);

// prevent dragging of images
document.querySelectorAll(".main-container img").forEach(img => img.ondragstart = () => false);