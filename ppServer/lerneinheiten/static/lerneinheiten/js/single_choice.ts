// hide textarea
document.querySelectorAll<HTMLTextAreaElement>("#form textarea").forEach(element => {
    element.parentElement!.classList.add("hidden");
});


// check spieler-selected radio
try {
    const answer = JSON.parse(document.querySelector<HTMLTextAreaElement>("#form #id_answer")!.value)["choice_id"];
    const radio = document.querySelector<HTMLInputElement>(`#choice-${answer}`);
    if (radio) radio.checked = true;
} catch { }


// set musterlösung
const solution_choice_id = parseInt(document.querySelector("#solution")!.innerHTML);
const solution_label = document.querySelector<HTMLInputElement>(`#choice-${solution_choice_id}`)!.labels![0].textContent || "";
document.querySelector("#musterlösung result")!.innerHTML = solution_label;



/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {
    this.answer.value = JSON.stringify({choice_id: parseInt(this.choices.value)});
});
