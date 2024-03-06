/***************** UTILS ***********************/

function shuffle<T>(array: T[]): T[] {
    return array
        .map(value => ({ value, sort: Math.random() }))
        .sort((a, b) => a.sort - b.sort)
        .map(({ value }) => value);
}

function render_item(id: number, label: string = ""): void {
    document.querySelector(".sortable-list")!.innerHTML += `
        <li class="sortable-item list-group-item" data-id="${ id }">
        
            <!-- handle -->
            <svg class="handle" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                <!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.-->
                <path d="M128 136c0-22.1-17.9-40-40-40L40 96C17.9 96 0 113.9 0 136l0 48c0 22.1 17.9 40 40 40H88c22.1 0 40-17.9 40-40l0-48zm0 192c0-22.1-17.9-40-40-40H40c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40H88c22.1 0 40-17.9 40-40V328zm32-192v48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V136c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM288 328c0-22.1-17.9-40-40-40H200c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V328zm32-192v48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V136c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM448 328c0-22.1-17.9-40-40-40H360c-22.1 0-40 17.9-40 40v48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V328z"/>
            </svg>

            <input type="text" value="${ label }" data-choice_id="${ id }">
        
            <button class="btn btn-danger" onclick="delete_item(${id})">
                <!-- trash -->
                <svg style="width:1em; margin: auto; display: block;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                    <!--! Font Awesome Pro 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. -->
                    <path fill="#ffffff" d="M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z"/>
                </svg>
            </button>
        
            </li>`;
}





// MDEditor for question & hide solution textarea
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

// Loop through each nested sortable element
const list = new Sortable(document.querySelector<HTMLUListElement>("ul.sortable-list"), {
    handle: '.handle', // handle's class
    animation: 150,
    fallbackOnBody: true,
    swapThreshold: 0.65,
});


function add_item(): void {

    // generate unique id for new choice
    let randomId = Math.ceil(Math.random() * 10000);
    while (document.querySelector(`.sortable-item[data-id="${ randomId }"]`)) {
        randomId = Math.ceil(Math.random() * 10000);
    }

    render_item(randomId);
}
function delete_item(id: number): void {
    document.querySelector(`.sortable-item[data-id="${ id }"]`)?.remove();
}



/************** INITIALLY RENDER *******************/

// get JSON
const order: number[] = JSON.parse(document.querySelector("#solution")!.innerHTML).order || [];
let choices: {id: number, label: string}[] = [];
try {
    choices = JSON.parse(document.querySelector("#choices")!.innerHTML);
} catch {};

// render li's
if (!choices.length) {
    add_item();
} else {
    order
        .map(choice_id => choices.find(c => c.id === choice_id))
        .filter(choice => choice)
        .forEach(choice => render_item(choice!.id, choice!.label))
}



/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {

    const choices = [...document.querySelectorAll<HTMLInputElement>("ul.sortable-list input[type=text]")].map(text_input =>
        ({id: parseInt(text_input.dataset.choice_id!), label: text_input.value})
    );

    this.content.value = JSON.stringify({text: this.content.value, choices: shuffle(choices)});
    this.solution.value = JSON.stringify({...JSON.parse(this.solution.value), order: list.toArray().map((id: string) => parseInt(id))});
});