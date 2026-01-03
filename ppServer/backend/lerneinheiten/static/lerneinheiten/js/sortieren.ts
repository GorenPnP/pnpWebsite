// hide textarea
document.querySelectorAll<HTMLTextAreaElement>("#form textarea").forEach(element => {
    element.parentElement!.classList.add("hidden");
});


// Loop through each nested sortable element
const sortable_list = document.querySelector<HTMLUListElement>("ul.sortable-list")!;
const list = new Sortable(sortable_list, {
    handle: '.handle', // handle's class
    animation: 150,
    fallbackOnBody: true,
    swapThreshold: 0.65,
});


// check spieler-selected order
try {
    const answer: number[] = JSON.parse(document.querySelector<HTMLTextAreaElement>("#form #id_answer")!.value)["order"];

    if (answer?.length) {
        ([...sortable_list.children] as HTMLLIElement[])
            .sort((a, b) => Math.sign(answer.indexOf(parseInt(a.dataset.id!)) - answer.indexOf(parseInt(b.dataset.id!))))
            .forEach(node => sortable_list.appendChild(node));
    }
} catch { }


// set musterlösung
const solution_order: number[] = JSON.parse(document.querySelector("#solution")!.innerHTML);
const solution_labels: string[] = solution_order
    .map(id => document.querySelector<HTMLInputElement>(`[data-id="${id}"] span`)!.textContent || "");

document.querySelector("#musterlösung result")!.innerHTML = "<ul><li>" + solution_labels.join("</li><li>") + "</li></ul>";



/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {
    this.answer.value = JSON.stringify({order: list.toArray().map((id: string) => parseInt(id))});
});
