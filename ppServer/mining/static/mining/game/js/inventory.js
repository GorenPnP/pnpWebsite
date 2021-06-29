// startup
document.addEventListener("DOMContentLoaded", () => {
    
    // TODO continue here
    // document.querySelector(".backdrop").style.display = 'grid';
    window.addEventListener("resize", Inventory.resize);

    Inventory.init();
    Inventory.updateGrid(9, 9);

    const items = []
    //     Array.from({length: 10}).map((_, i) => ({
    //         id: i+1,
    //         bg_color: '#555',
    //         amount: i+1,
    //         w: Math.floor(Math.random() * Inventory.col_num / 3) + 1,
    //         h: Math.floor(Math.random() * Inventory.row_num / 3) + 1,
    // }));
    // items.push({
    //     id: 500,
    //     x: 6,
    //     y: 4,
    //     w: 4,
    //     h: 4,
    //     bg_color: '#555',
    //     amount: 500
    // });
    // items.push({
    //     id: 400,
    //     x: 6,
    //     y: 1,
    //     w: 4,
    //     h: 4,
    //     bg_color: '#555',
    //     amount: 400
    // });

    Array.from({length: 9}).map((_, x) =>
        Array.from({length: 9}).map((_, y) => 
            items.push({
                id: 10 * (x+1) + y+1,
                x: x+1,
                y: y+1,
                w: 1,
                h: 1,
                bg_color: '#555',
                amount: 10 * (x+1) + y+1
            })
        )
    );
    // items.push({
    //     id: 1,
    //     x: 1,
    //     y: 2,
    //     w: 1,
    //     h: 1,
    //     bg_color: '#555',
    //     amount: 12
    // });
    // items.push({
    //     id: 2,
    //     x: 8,
    //     y: 4,
    //     w: 1,
    //     h: 1,
    //     bg_color: '#555',
    //     amount: 84
    // });
    items.forEach(item => Inventory.setItem(item));
});


class Inventory {

    static col_num = 1;
    static row_num = 1;
    
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

    static setItem(item) {  // item = {...rect, bg-color, image-href, id, amount}

        if (!Inventory.isPlaceFree(item)) {
            console.log("already occupied. Cannot place ", item);
            return;
        }

        const items = Inventory.inventory.querySelector(".items");
        let tag = items.querySelector(`#item-${item.id}`);
        let amount;

        // create new tag
        if (!tag) {
            tag = document.createElement('div');
            tag.id = `item-${item.id}`;
            tag.classList.add('item');

            amount = document.createElement('span');
            amount.classList.add('amount');

            tag.appendChild(amount);
            items.appendChild(tag);
        } else { amount = tag.querySelector(".amount"); }

        // set properties
        if (item.x) tag.style.gridColumnStart = item.x;
        if (item.w) tag.style.gridColumnEnd = `span ${item.w}`;
        
        if (item.y) tag.style.gridRowStart = item.y;
        if (item.h) tag.style.gridRowEnd = `span ${item.h}`;

        tag.style.setProperty('--bg-color', item.bg_color);
        amount.innerHTML = item.amount || amount.innerHTML;

        Inventory.updateItemGridPlacement(item);
    }

    static updateItemGridSize() {
        // TODO
    }
    static isPlaceFree(item) {

        // collect all cells that would be covered by the item
        return Inventory.item_grid.reduce((cells, row, row_index) => {

            // decide by y-axis
            const y = row_index + 1;
            if (y < item.y || y >= item.y + item.h) { return cells; }

            // decide by x-axis
            const row_cells = row.filter((_, col_index) => {
                const x = col_index + 1;
                return x >= item.x && x < item.x + item.w;
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
                return isPointInRect({x: col_index + 1, y: row_index + 1}, item) ? item.id : cell;
            })
        );

        console.table(Inventory.item_grid)
    }
}

function isPointInRect(point, rect) {
    return (point.x >= rect.x && point.x < rect.x + rect.w) &&
           (point.y >= rect.y && point.y < rect.y + rect.h);
}