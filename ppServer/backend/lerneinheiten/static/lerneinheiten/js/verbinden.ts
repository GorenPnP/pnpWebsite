/************** UTILS ****************/

interface Choice {
    id: number,
    label: string,
}


function render_pair(left: Choice, right: Choice) {
    const left_child = document.createElement("li");
    left_child.dataset.id = ""+left.id;
    left_child.classList.add("list-group-item");
    left_child.innerHTML =  left.label;
    document.querySelector(".list--left")!.appendChild(left_child);

    const row = document.createElement("div");
    row.classList.add("pair-line");
    document.querySelector("#line-container")!.appendChild(row);
    
    const right_child = document.createElement("li");
    right_child.dataset.id = ""+right.id;
    right_child.classList.add("sortable-item", "list-group-item");
    right_child.innerHTML = `
        <!-- handle -->
        <svg class="handle" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
            <!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.-->
            <path d="M128 136c0-22.1-17.9-40-40-40L40 96C17.9 96 0 113.9 0 136l0 48c0 22.1 17.9 40 40 40H88c22.1 0 40-17.9 40-40l0-48zm0 192c0-22.1-17.9-40-40-40H40c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40H88c22.1 0 40-17.9 40-40V328zm32-192v48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V136c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM288 328c0-22.1-17.9-40-40-40H200c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V328zm32-192v48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V136c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM448 328c0-22.1-17.9-40-40-40H360c-22.1 0-40 17.9-40 40v48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V328z"/>
        </svg>

        <span>${ right.label }</span>`;
    document.querySelector(".list--right")!.appendChild(right_child);
}






/************** INIT ****************/


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


// initially render pairs
const content: {choices: Choice[], text: string} = JSON.parse(document.querySelector("#content")!.innerHTML);
const solution_orders: {left: number[], right: number[]} = JSON.parse(document.querySelector("#solution")!.innerHTML);
const right_random_choices = content.choices.filter(c => solution_orders.right.includes(c.id));
solution_orders.left.forEach((left_id, index) =>
    render_pair(content.choices.find(c => c.id === left_id)!, right_random_choices[index])
);


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
const pair_labels: string[] = solution_orders.left
    .reduce((pairs, left_id, index) => {
        const pair = {
            left: content.choices.find(c => c.id === left_id)!.label,
            right: content.choices.find(c => c.id === solution_orders.right[index])!.label,
        };
        pairs.push(pair);
        return pairs;
    }, [] as {left: string, right: string}[])
    .map(pair => `<tr><td>${pair.left}</td><td><b>${pair.right}</b></td></tr>`);

document.querySelector("#musterlösung result")!.innerHTML = '<div class="table-responsive"><table class="table"><tbody>' + pair_labels.join("") + "</tbody></table></div>";



/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {
    this.answer.value = JSON.stringify({order: list.toArray().map((id: string) => parseInt(id))});
});
