/************** UTILS ****************/
interface Item {
    id: number,
    label: string,
}


function render_item(container: Element, item: Item) {
    
    const child = document.createElement("li");
    child.dataset.id = ""+item.id;
    child.classList.add("sortable-item", "list-group-item");
    child.innerHTML = `
        <!-- handle -->
        <svg class="handle" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
            <!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.-->
            <path d="M128 136c0-22.1-17.9-40-40-40L40 96C17.9 96 0 113.9 0 136l0 48c0 22.1 17.9 40 40 40H88c22.1 0 40-17.9 40-40l0-48zm0 192c0-22.1-17.9-40-40-40H40c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40H88c22.1 0 40-17.9 40-40V328zm32-192v48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V136c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM288 328c0-22.1-17.9-40-40-40H200c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V328zm32-192v48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V136c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM448 328c0-22.1-17.9-40-40-40H360c-22.1 0-40 17.9-40 40v48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V328z"/>
        </svg>

        <span>${ item.label }</span>`;
    container.appendChild(child);
}




/************** INIT ****************/


// hide textarea
document.querySelectorAll<HTMLTextAreaElement>("#form textarea").forEach(element => {
    element.parentElement!.classList.add("hidden");
});



// Loop through each nested sortable element
const category_lists = [...document.querySelectorAll<HTMLUListElement>("ul.sortable-list")].reduce((acc, sortable_list) => {
    const sortable = new Sortable(sortable_list, {
        handle: '.handle', // handle's class
        // group: 'shared',
        group: { name: "category", pull: true, put: true },
        animation: 150,
        fallbackOnBody: true,
        swapThreshold: 0.65,
    });

    const category_id = sortable_list.dataset.category!;
    if (category_id) { acc[category_id] = sortable; }
    return acc;
}, {} as {[category_id: string]: Sortable});


// initially render pairs
const content_categories: {categories: Item[], items: Item[], text: string} = JSON.parse(document.querySelector("#content")!.innerHTML);

// check spieler-selected order
let user_item_ids: number[] = [];
try {
    const answer: {[category_id: string]: number[]} = JSON.parse(document.querySelector<HTMLTextAreaElement>("#form #id_answer")!.value)["categories"];

    if (answer && Object.keys(answer).length) {
        user_item_ids = Object.values(answer).reduce((acc, item_ids) => [...acc, ...item_ids], []);
        Object.entries(answer).forEach(([category_id, item_ids]) => {
            const category_container = document.querySelector(`ul[data-category="${ category_id }"]`)!;
            item_ids
                .map(item_id => content_categories.items.find(i => i.id === item_id)!)
                .forEach(item => render_item(category_container, item));
        });
    }
} catch { }

const container_remaining = document.querySelector("ul[data-category='']")!;
content_categories.items
    .filter(item => !user_item_ids.includes(item.id))
    .forEach(item => render_item(container_remaining, item));

const solution_categories: {[category_id: number]: number[]} = JSON.parse(document.querySelector("#solution")!.innerHTML).categories;

// set musterlösung
const musterlösung_cols: Item[][] = Object.entries(solution_categories).reduce((acc, [cat_id, item_ids]) => {
        const col: Item[] = [
            content_categories.categories.find(cat => cat.id === parseInt(cat_id))!,
            ...item_ids
                .map(item_id => content_categories.items.find(item => item.id === item_id)!)
                .sort((a, b) => a.label < b.label ? -1 : 1)
        ];
        acc.push(col);

        return acc;
    }, [] as Item[][])
    .sort((a, b) => a[0].label < b[0].label ? -1 : 1);

let solution_table = "<thead><tr><th>" + musterlösung_cols.map(col => col.shift()?.label || "").join(`</th><th>`) + "</th></tr></thead><tbody>";
while(musterlösung_cols.some(col => col.length)) {
    solution_table += "<tr><td>" + musterlösung_cols.map(col => col.shift()?.label || "").join(`</td><td>`) + "</td></tr>";
}

document.querySelector("#musterlösung result")!.innerHTML = '<div class="table-responsive"><table class="table">' + solution_table + "</tbody></table></div>";



/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {

    const categories = Object.entries(category_lists).reduce((acc, [category_id, sortable]) => {
        const item_ids: number[] = sortable.toArray()
            .map((id: string) => parseInt(id))
            .sort((a: number, b: number) => content_categories.items.find(item => item.id === a)!.label < content_categories.items.find(item => item.id === b)!.label ? -1 : 1);

        if (item_ids.length) { acc[parseInt(category_id)] = item_ids; }
        return acc;
    }, {} as {[category_id: number]: number[]});

    this.answer.value = JSON.stringify({ categories });
});
