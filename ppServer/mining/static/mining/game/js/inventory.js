// startup
document.addEventListener("DOMContentLoaded", () => {

    window.addEventListener("resize", Inventory.resize);

    Inventory.init();
    const inventory = JSON.parse(document.querySelector("#inventory").innerHTML)
    Inventory.inventory.dataset.id = inventory.id;
    Inventory.updateGrid(inventory.width, inventory.height);

    const inventory_stacks = JSON.parse(document.querySelector("#inventory-items").innerHTML)
        .map(stack => {
            const {id, height, width, bg_color, crafting_item} = stack.item;
            return {
                id: stack.id,
                item_id: id,
                x: stack.position ? stack.position.x : undefined,
                y: stack.position ? stack.position.y : undefined,
                h: height,
                w: width,
                amount: stack.amount,
                max_amount: stack.item.max_amount,
                bg_color,
                image_href: crafting_item.icon_url
            }
        });
        
    inventory_stacks.forEach(stack => Inventory.setStack(stack));
});


class Inventory {

    static col_num = 1;
    static row_num = 1;
    
    static backdrop;
    static inventory;
    
    static stack_grid = [[]];

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
        const stacks = Inventory.inventory.querySelector(".stacks");

        // background
        grid.innerHTML = null;
        for (let i = 0; i < col_num * row_num; i++) {
            const slot = document.createElement('div');
            slot.classList.add("inventory-slot");
            grid.appendChild(slot);
        }

        // stacks
        stacks.style.width = `calc(${Inventory.col_num} * var(--slot-size))`;
        stacks.style.height = `calc(${Inventory.row_num} * var(--slot-size))`;

        // both
        for (let tag of [grid, stacks]) {
            const style = tag.style;
            style.gridTemplateColumns = `repeat(${col_num}, 1fr)`;
            style.gridTemplateRows = `repeat(${row_num}, 1fr)`;
        }

        // js-intern coverage-logic
        Inventory.stack_grid = Array.from({length: Inventory.row_num}).map(() =>
                                Array.from({length: Inventory.row_num}).map(() =>
                                    null
                                )
                            );

        Inventory.resize();
        Inventory.updateStackGridSize();
    }

    static setStack(stack) {  // stack = {...rect, bg_color, image_href, id, amount, max_amount}
        
        // divide stack into several if exceeds stack size
        while (stack.amount > stack.max_amount) {
            const new_stack = {
                ...stack,
                amount: stack.max_amount,
                id: get_random_hash(),
            };
            stack.amount -= stack.max_amount;
            Inventory.setStack(new_stack);
        }
        
        // pin position
        let has_valid_pos = !(
            [stack.x, stack.y].some(coord => [undefined, null].includes(coord)) ||    // ..none given
            stack.x < 1 || stack.x > Inventory.col_num - stack.w + 1 ||                // ..invalid position 
            stack.y < 1 || stack.y > Inventory.row_num - stack.h + 1 ||                //   that's not in grid
            !Inventory.isPlaceFree(stack)
        );
        
        // find a position if invalid
        if (!has_valid_pos) {                                         // ..pos is already occupied
            stack = {...stack, x: undefined, y: undefined};

            for (let y = 1; !has_valid_pos && y <= Inventory.row_num - stack.h + 1; y++) {
                for (let x = 1; !has_valid_pos && x <= Inventory.col_num - stack.w + 1; x++) {
                    if (Inventory.isPlaceFree({...stack, x, y})) {
                        stack = {...stack, x, y};
                        has_valid_pos = true;
                    }
                }
            }
        }

        // if no free space left
        if (!has_valid_pos) {
            console.log("already occupied. Cannot place ", stack);
            console.table(Inventory.stack_grid)
            return;
        }

        const stacks = Inventory.inventory.querySelector(".stacks");
        let tag = stacks.querySelector(`#stack-${stack.id}`);
        let amount;

        // create new tag
        if (!tag) {
            tag = document.createElement('div');
            tag.id = `stack-${stack.id}`;
            tag.classList.add('stack', 'reorder-container__element');
            tag.setAttribute("draggable", "true");
            tag.dataset.item_id = stack.item_id;

            amount = document.createElement('span');
            amount.classList.add('amount');

            tag.appendChild(amount);
            stacks.appendChild(tag);
            add_draggable(tag);
        } else { amount = tag.querySelector(".amount"); }

        // set properties
        tag.style.gridColumnStart = stack.x;
        tag.style.gridColumnEnd = `span ${stack.w}`;
        
        tag.style.gridRowStart = stack.y;
        tag.style.gridRowEnd = `span ${stack.h}`;

        if (stack.bg_color) tag.style.setProperty('--bg-color', stack.bg_color);
        if (stack.image_href) tag.style.setProperty('--img', `url('${stack.image_href}')`);
        amount.innerHTML = stack.amount || amount.innerHTML;

        Inventory.updateStackGridPlacement(stack);
    }


    static removeStack(id) {
        document.querySelector(`#stack-${id}`).remove();

        Inventory.stack_grid = Inventory.stack_grid.map(row =>
            row.map(cell => cell == id ? null : cell)
        );
    }

    static updateStackGridSize() {
        // TODO
    }
    static isPlaceFree(stack) {
        let {x, y, w, h} = stack;
        x--; y--;

        // collect all cells that would be covered by the stack
        return Inventory.stack_grid.reduce((cells, row, row_index) => {

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
        .every(cell => !cell || cell === stack.id);
    }
    static updateStackGridPlacement(stack) {
        Inventory.stack_grid = Inventory.stack_grid.map((row, row_index) =>
            row.map((cell, col_index) => {
                return isPointInRect({x: col_index + 1, y: row_index + 1}, stack) ? stack.id : (cell == stack.id ? null : cell);
            })
        );
    }
}

function isPointInRect(point, rect) {
    return (point.x >= rect.x && point.x < rect.x + rect.w) &&
           (point.y >= rect.y && point.y < rect.y + rect.h);
}

function drag_start_callback() { }
function drag_end_callback(element, _) {

    // get id of element
    let id = element.id.split('-').reverse()[0];

    // get drag vector
    let offset_grid_x = Math.floor(offsetX / tile_size);
    let offset_grid_y = Math.floor(offsetY / tile_size);
    
    // apply it & stay in grid
    const element_rect = get_element_rect_in_grid(element);
    element_rect.x = Math.min(Math.max(1, element_rect.x + offset_grid_x), Inventory.col_num - element_rect.w + 1);
    element_rect.y = Math.min(Math.max(1, element_rect.y + offset_grid_y), Inventory.row_num - element_rect.h + 1);

    // set element
    const item_id = parseInt(element.dataset.item_id, 10);
    const amount = parseInt(element.querySelector('.amount').innerHTML, 10);
    const stack = {
        ...element_rect,
        id,
        item_id,
        amount
    };
    Inventory.setStack(stack);

    // inform backend over position change
    const stack_id = id;
    id = parseInt(id, 10) || undefined;
    const inventory_id = parseInt(Inventory.inventory.dataset.id, 10);
    ws_save_inventory_item_position({
            ...stack,
            rotated: false,
            inventory_id,
            id,
            stack_id
        },
        element);
}

function get_element_rect_in_grid(element) {
    const bounds_rect = element.getBoundingClientRect();
    return {
        x: parseInt(/\d+/.exec(element.style.gridColumnStart)) || bounds_rect.x || 1,
        y: parseInt(/\d+/.exec(element.style.gridRowStart)) || bounds_rect.y || 1,
        w: parseInt(/\d+/.exec(element.style.gridColumnEnd)) || bounds_rect.width / tile_size || 1,
        h: parseInt(/\d+/.exec(element.style.gridRowEnd)) || bounds_rect.height / tile_size || 1
    };
}
