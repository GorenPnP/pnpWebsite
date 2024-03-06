// hide textarea
document.querySelectorAll<HTMLTextAreaElement>("#form textarea").forEach(element => {
    element.parentElement!.classList.add("hidden");
});


// check spieler-selected check
try {
    const answer = JSON.parse(document.querySelector<HTMLTextAreaElement>("#form #id_answer")!.value)["choice_id"];
    const check = document.querySelector<HTMLInputElement>(`#choice-${answer}`);
    if (check) check.checked = true;
} catch { }


// set musterlösung
const solution_choice_ids: number[] = JSON.parse(document.querySelector("#solution")!.innerHTML);
const solution_labels = solution_choice_ids.map(choice_id => document.querySelector<HTMLInputElement>(`#choice-${choice_id}`)!.labels![0].textContent || "");
document.querySelector("#musterlösung result")!.innerHTML = "<ul><li>" + solution_labels.join("</li><li>") + "</li></ul>";



/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {
    this.answer.value = JSON.stringify({choice_id: parseInt(this.choices.value)});
});
