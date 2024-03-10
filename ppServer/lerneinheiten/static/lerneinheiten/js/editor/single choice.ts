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



function render_radio(id: number, label: string = "", checked: boolean = false): void {
    const row = document.createElement("div");
    row.classList.add("radio-row");
    row.innerHTML = `
        <input type="radio" id="choice-${id}" name="choices" value="${id}" form="form" required ${checked ? 'checked' : ''}>
        <label for="choice-${id}"><input type="text" value="${label}" required form="form"></label>
        <button class="btn btn-danger" onclick="delete_radio(${id})">
            <!-- trash -->
            <svg style="width:1em; margin: auto; display: block;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                <!--! Font Awesome Pro 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. -->
                <path fill="#ffffff" d="M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z"/>
            </svg>
        </button>`;
    document.querySelector(".radio")!.appendChild(row);
}

function add_radio(): void {

    // generate unique id for new radio choice
    let randomId = Math.ceil(Math.random() * 10000);
    while (document.querySelector(`.radio [type=radio]#choice-${randomId}`)) {
        randomId = Math.ceil(Math.random() * 10000);
    }

    render_radio(randomId);
}
function delete_radio(id: number): void {
    document.querySelector(`#choice-${id}`)?.closest(".radio-row")?.remove();
}



/************** INITIALLY RENDER *******************/

// get JSON
const solution: {choice_id: number} = JSON.parse(document.querySelector("#solution")!.innerHTML);
let choices: {id: number, label: string}[] = [];
try {
    choices = JSON.parse(document.querySelector("#choices")!.innerHTML);
} catch {};

// render radios
if (!choices.length) {
    add_radio();
} else {
    choices.forEach(choice => render_radio(choice.id, choice.label, choice.id === solution.choice_id))
}



/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {

    const choices = [...document.querySelectorAll(".radio .radio-row")].map(row => {
        const id = parseInt((row.querySelector("[type=radio]")! as HTMLInputElement).value);
        const label = (row.querySelector("[type=text]")! as HTMLInputElement).value;
        return {id, label};
    });

    this.content.value = JSON.stringify({text: this.content.value, choices});
    this.solution.value = JSON.stringify({...JSON.parse(this.solution.value), choice_id: parseInt(this.choices.value)});
    this.choices.value = null;
});