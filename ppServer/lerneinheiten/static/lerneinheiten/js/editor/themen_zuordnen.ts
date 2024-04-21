interface Item {
    id: number,
    label: string,
}

document.querySelectorAll<HTMLTextAreaElement>("#form textarea").forEach(element => {

    if (element.id !== "id_content") {
        element.parentElement!.classList.add("hidden");
    } else {
        let initialValue = element.value?.trim() || "";
        try {
            initialValue = JSON.parse(initialValue)["text"] || " ";
        } catch {};
        
        new EasyMDE({
            ...MDEditorConfig,
            element,
            initialValue
        })
    }
});



function generate_random_id(): number {

    // generate unique id for new item
    let randomId = Math.ceil(Math.random() * 10000);
    while (document.querySelector(`.item[data-id="${randomId}"]`)) {
        randomId = Math.ceil(Math.random() * 10000);
    }
    return randomId;
}


function render_category(id: number, label: string = "", items: Item[] = []) {
    const row = document.createElement("div");
    row.classList.add("category");
    row.dataset.id = ""+id;
    row.innerHTML = `
        <div class="head item">
            <input type="text" class="category-input" value="${label}" required form="form">
            <button class="btn btn-danger" onclick="delete_category(${id})">
                <!-- trash -->
                <svg style="width:1em; margin: auto; display: block;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                    <!--! Font Awesome Pro 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. -->
                    <path fill="#ffffff" d="M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z"/>
                </svg>
            </button>
        </div>
        
        <div class="content">
            <ul class="content__list"></ul>
            <button class="btn btn-primary" onclick="add_item(${id})">+ Item</button>
        </div>`;

    document.querySelector("#category-container")!.insertBefore(row, document.querySelector("#add-cat-btn"));

    const content = document.querySelector(`.category[data-id="${id}"] .content__list`)!;
    if (!items?.length) {
        add_item(""+id);
    } else {
        items.forEach(item => render_item(content, ""+item.id, item.label));
    }

}


function render_item(category_content: Element, id: string, label: string = ""): void {
    const row = document.createElement("div");
    row.classList.add("radio-row");
    row.innerHTML = `
        <li data-id="${id}" class="item">
            <input type="text" class="item-input" value="${label}" required form="form">
            <button class="btn btn-danger" onclick="delete_item(${id})">
                <!-- trash -->
                <svg style="width:1em; margin: auto; display: block;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                    <!--! Font Awesome Pro 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. -->
                    <path fill="#ffffff" d="M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z"/>
                </svg>
            </button>
        </li>`;
    category_content.appendChild(row);
}

function add_category(id: number = generate_random_id(), label: string = "", items: Item[] = []): void {
    render_category(id, label, items);
}
function delete_category(category_id: string): void {
    document.querySelector(`.category[data-id="${category_id}"]`)?.remove();
}


function add_item(category_id: string): void {
    const category_content = document.querySelector(`.category[data-id="${category_id}"] .content__list`)!;

    // generate unique id for new item
    let randomId = Math.ceil(Math.random() * 10000);
    while (category_content.querySelector(`.item[data-id="${randomId}"]`)) {
        randomId = Math.ceil(Math.random() * 10000);
    }

    render_item(category_content, ""+randomId);
}
function delete_item(item_id: string): void {
    document.querySelector(`[data-id="${item_id}"]`)?.remove();
}



/************** INITIALLY RENDER *******************/

// get JSON
const solution: {categories: {[category_id: number]: number[]}} = JSON.parse(document.querySelector("#solution")!.innerHTML);
let content: {categories: Item[], items: Item[]};
try {
    content = JSON.parse(document.querySelector("#content")!.innerHTML);
} catch {};

// render
if (!content?.categories?.length) {
    add_category();
} else {
    content.categories.forEach(cat => {
        const items: Item[] = solution.categories[cat.id].map(item_id => content.items.find(item => item.id === item_id)!);
        add_category(cat.id, cat.label, items);
    })
}



/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {

    const categories: Item[] = [...document.querySelectorAll(".category")]
        .map((row: any) => ({
            id: parseInt(row.dataset.id),
            label: (row.querySelector(".category-input[type=text]")! as HTMLInputElement).value,
        }))
        .sort((a, b) => a.label < b.label ? -1 : 1);;

    const items: Item[] = [...document.querySelectorAll(".category .content .item")]
        .map((item: any) => ({
            id: parseInt(item.dataset.id),
            label: (item.querySelector(".item-input[type=text]")! as HTMLInputElement).value
        }))
        .sort((a, b) => a.label < b.label ? -1 : 1);

    const solution: {[category_id: number]: number[]} = [...document.querySelectorAll(".category")].reduce((acc, cat: any) => {
        const cat_id = parseInt(cat.dataset.id);
        acc[cat_id] = [...cat.querySelectorAll(".content .item")].map(item => parseInt(item.dataset.id));
        return acc;
    }, {} as {[category_id: number]: number[]});


    this.content.value = JSON.stringify({text: this.content.value, categories, items});
    this.solution.value = JSON.stringify({...JSON.parse(this.solution.value), categories: solution});
});
