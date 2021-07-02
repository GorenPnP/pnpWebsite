// startup
document.addEventListener("DOMContentLoaded", () => {

    window.addEventListener("resize", Inventory.resize);

    Inventory.init();
    const inventory = JSON.parse(document.querySelector("#inventory").innerHTML)
    Inventory.inventory.dataset.id = inventory.id;
    Inventory.updateGrid(inventory.width, inventory.height);

    const inventory_items = JSON.parse(document.querySelector("#inventory-items").innerHTML)
        .map(inventory_item => {
            const {id, height, width, bg_color, crafting_item} = inventory_item.item;
            return {
                id,
                x: inventory_item.position ? inventory_item.position.x : undefined,
                y: inventory_item.position ? inventory_item.position.y : undefined,
                h: height,
                w: width,
                amount: inventory_item.amount,
                bg_color,
                image_href: crafting_item.icon_url
            }
        });
    inventory_items.forEach(item => Inventory.setItem(item));
});


class Inventory {

    static col_num = 1;
    static row_num = 1;
    
    static backdrop;
    static inventory;
    
    static item_grid = [[]];

        // const img_urls = [
        //     '/static/res/img/mining/char_skin_front.png',
        // ];
        // // load assets
        // resources.load(...img_urls);
        // resources.onReady(init);
    
    static init() {
        Inventory.inventory = document.querySelector(".inventory");
        Inventory.backdrop = document.querySelector(".backdrop");
        init_draggable_reorder();
    }
    
    static resize() {
        const container = document.querySelector(".backdrop");
        const slot_size = Math.min(container.offsetWidth / Inventory.col_num, container.offsetHeight / Inventory.row_num, tile_size);

        document.documentElement.style.setProperty('--slot-size', `${slot_size}px`);
    }

    static updateGrid(col_num, row_num) {
        Inventory.col_num = col_num;
        Inventory.row_num = row_num;

        const grid = Inventory.inventory.querySelector(".background-grid");
        const items = Inventory.inventory.querySelector(".items");

        // background
        grid.innerHTML = null;
        for (let i = 0; i < col_num * row_num; i++) {
            const slot = document.createElement('div');
            slot.classList.add("inventory-slot");
            grid.appendChild(slot);
        }

        // items
        items.style.width = `calc(${Inventory.col_num} * var(--slot-size))`;
        items.style.height = `calc(${Inventory.row_num} * var(--slot-size))`;

        // both
        for (let tag of [grid, items]) {
            const style = tag.style;
            style.gridTemplateColumns = `repeat(${col_num}, 1fr)`;
            style.gridTemplateRows = `repeat(${row_num}, 1fr)`;
        }

        // js-intern coverage-logic
        Inventory.item_grid = Array.from({length: Inventory.row_num}).map(() =>
                                Array.from({length: Inventory.row_num}).map(() =>
                                    null
                                )
                            );

        Inventory.resize();
        Inventory.updateItemGridSize();
    }

    static setItem(item) {  // item = {...rect, bg_color, image_href, id, amount}
        if (!Inventory.isPlaceFree(item)) {
            console.log("already occupied. Cannot place ", item);
            console.table(Inventory.item_grid)
            return;
        }

        const items = Inventory.inventory.querySelector(".items");
        let tag = items.querySelector(`#item-${item.id}`);
        let amount;

        // create new tag
        if (!tag) {
            tag = document.createElement('div');
            tag.id = `item-${item.id}`;
            tag.classList.add('item', 'reorder-container__element');
            tag.setAttribute("draggable", "true");

            amount = document.createElement('span');
            amount.classList.add('amount');

            tag.appendChild(amount);
            items.appendChild(tag);
            add_draggable(tag);
        } else { amount = tag.querySelector(".amount"); }

        // set properties
        if (item.x) tag.style.gridColumnStart = item.x;
        if (item.w) tag.style.gridColumnEnd = `span ${item.w}`;
        
        if (item.y) tag.style.gridRowStart = item.y;
        if (item.h) tag.style.gridRowEnd = `span ${item.h}`;

        if (item.bg_color) tag.style.setProperty('--bg-color', item.bg_color);
        if (item.image_href) tag.style.setProperty('--img', `url('${item.image_href}')`);
        amount.innerHTML = item.amount || amount.innerHTML;

        Inventory.updateItemGridPlacement(item);
    }

    static updateItemGridSize() {
        // TODO
    }
    static isPlaceFree(item) {
        let {x, y, w, h} = item;
        x--; y--;

        // collect all cells that would be covered by the item
        return Inventory.item_grid.reduce((cells, row, row_index) => {

            // decide by y-axis
            if (row_index < y || row_index >= y + h) { return cells; }

            // decide by x-axis
            const row_cells = row.filter((_, col_index) => {
                return col_index >= x && col_index < x + w;
            });

            // collect the cells
            return [...cells, ...row_cells];
        }, [])

        // all of them have to be empty
        .every(cell => !cell || cell === item.id);
    }
    static updateItemGridPlacement(item) {
        Inventory.item_grid = Inventory.item_grid.map((row, row_index) =>
            row.map((cell, col_index) => {
                return isPointInRect({x: col_index + 1, y: row_index + 1}, item) ? item.id : (cell === item.id ? null : cell);
            })
        );
    }
}

function isPointInRect(point, rect) {
    return (point.x >= rect.x && point.x < rect.x + rect.w) &&
           (point.y >= rect.y && point.y < rect.y + rect.h);
}


function drag_start_callback(element) { }
function drag_end_callback(element) {
    // get rect of element
    const item_id = parseInt(/\d+/.exec(element.id), 10);
    const w = parseInt(/\d+/.exec(element.style.gridColumnEnd)) || 1;
    const h = parseInt(/\d+/.exec(element.style.gridRowEnd)) || 1;
    let x = Math.floor(offsetTouchX / tile_size);
    let y = Math.floor(offsetTouchY / tile_size);
    
    // stay in inventory rect
    x = Math.max(0, x);
    y = Math.max(0, y);
    if (x + w > Inventory.col_num) x = Inventory.col_num - w;
    if (y + h > Inventory.row_num) y = Inventory.row_num - h;

    // set element
    const item = {
        x: x+1, y: y+1, w, h,
        id: item_id
    };
    Inventory.setItem(item);

    // TODO inform backend over position change
    const inventory_id = parseInt(Inventory.inventory.dataset.id, 10);
    ws_save_inventory_item_position({x: x+1, y: y+1, rotated: false, item_id: item_id, inventory_id});

}