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



function render_check(id: number, label: string = "", checked: boolean = false): void {
    document.querySelector(".check")!.innerHTML += `
        <div class="check-row">
            <input type="checkbox" id="choice-${id}" name="${id}" form="form" ${checked ? 'checked' : ''}>
            <label for="choice-${id}"><input type="text" value="${label}" required form="form"></label>
            <button class="btn btn-danger" onclick="delete_check(${id})">
                <!-- trash -->
                <svg style="width:1em; margin: auto; display: block;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                    <!--! Font Awesome Pro 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. -->
                    <path fill="#ffffff" d="M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z"/>
                </svg>
            </button>
        </div>`;
}

function add_check(): void {

    // generate unique id for new check choice
    let randomId = Math.ceil(Math.random() * 10000);
    while (document.querySelector(`.check [type=checkbox]#choice-${randomId}`)) {
        randomId = Math.ceil(Math.random() * 10000);
    }

    render_check(randomId);
}
function delete_check(id: number): void {
    document.querySelector(`#choice-${id}`)?.closest(".check-row")?.remove();
}



/************** INITIALLY RENDER *******************/

// get JSON
const solution: {choice_ids: number[]} = JSON.parse(document.querySelector("#solution")!.innerHTML);
let choices: {id: number, label: string}[] = [];
try {
    choices = JSON.parse(document.querySelector("#choices")!.innerHTML);
} catch {};

// render checks
if (!choices.length) {
    add_check();
} else {
    choices.forEach(choice => render_check(choice.id, choice.label, solution.choice_ids?.includes(choice.id)))
}



/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {
    
    const solution_choice_ids = [...document.querySelectorAll<HTMLInputElement>(".check [type=checkbox]:checked")].map(checkbox => parseInt(checkbox.name));
    const choices = [...document.querySelectorAll(".check .check-row")].map(row => {
        const id = parseInt((row.querySelector("[type=checkbox]")! as HTMLInputElement).name);
        const label = (row.querySelector("[type=text]")! as HTMLInputElement).value;
        return {id, label};
    });

    this.content.value = JSON.stringify({text: this.content.value, choices});
    this.solution.value = JSON.stringify({...JSON.parse(this.solution.value), choice_ids: solution_choice_ids});
});