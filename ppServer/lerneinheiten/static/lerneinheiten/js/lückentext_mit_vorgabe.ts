function render_item(element: HTMLUListElement, item: string): void {
    const li = document.createElement("li");
    li.dataset.id = item;   // TODO replace with other id?
    li.classList.add("sortable-item", "list-group-item");
    li.innerHTML = `
        <!-- handle -->
        <svg class="handle" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
            <!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.-->
            <path d="M128 136c0-22.1-17.9-40-40-40L40 96C17.9 96 0 113.9 0 136l0 48c0 22.1 17.9 40 40 40H88c22.1 0 40-17.9 40-40l0-48zm0 192c0-22.1-17.9-40-40-40H40c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40H88c22.1 0 40-17.9 40-40V328zm32-192v48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V136c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM288 328c0-22.1-17.9-40-40-40H200c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V328zm32-192v48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V136c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM448 328c0-22.1-17.9-40-40-40H360c-22.1 0-40 17.9-40 40v48c0 22.1 17.9 40 40 40h48c22.1 0 40-17.9 40-40V328z"/>
        </svg>
        <span>${item}</span>`;
    element.appendChild(li);
}




// init MD-Editors
const answer_textarea = document.querySelector<HTMLTextAreaElement>("#form textarea#id_answer")!;
answer_textarea.closest("p")!.classList.add("hidden");



/**
 * Replaces Markdown-text in innerHTML of tags with class .markdown--lücken to html
 * 
 * !!! REPLACES GAPS WITH INPUT TAGS
 * 
 * needs to include as deps:
 * <script src="{% static 'res/js/markdown.js' %}" defer></script>
 * 
 * Use like this:
 * <div class="markdown--lücken" data-text="..."></div>
 */
function gap_replacement(full_match: string, gap_id: string): string {
    const value = JSON.parse(answer_textarea.value).gaps?.[gap_id] || "";      // TODO
    return `<ul class="sortable-list list-group" data-gap_id="${gap_id}"></ul>`;
}

// render md to html for text
const element = document.querySelector<HTMLDivElement>(".markdown--lücken")!;
const rendered_text = (element as any).dataset.text.replace(/<id:(\d+)>/gi, gap_replacement);

// display gap properly
element.innerHTML = md_to_html(rendered_text);




/************ Loop through each nested sortable element ******************/
const gap_lists = [...document.querySelectorAll<HTMLUListElement>(".sortable-list")].reduce((acc, sortable_list) => {
    const sortable = new Sortable(sortable_list, {
        handle: '.handle', // handle's class
        // group: 'shared',
        group: { name: "gap_id", pull: true, put: true },
        sort: false,
        animation: 150,
        fallbackOnBody: true,
        swapThreshold: 0.65,
    });

    const gap_id = sortable_list.dataset.gap_id;
    if (gap_id) { acc[gap_id] = sortable; }
    return acc;
}, {} as {[gap_id: string]: Sortable});



// set spieler's answers
const user_answers = JSON.parse(answer_textarea.value).gaps || {};
Object.entries(user_answers).forEach(([gap_id, item]) => {
    const list = document.querySelector(`[data-gap_id="${gap_id}"]`)!;
    render_item(list, item as string);
});

// set remaining items
const free_gaps = Object.keys(JSON.parse(document.querySelector("#solution")!.innerHTML).gaps)
    .filter(gap_id => !Object.keys(user_answers).includes(gap_id))
    .map(gap_id => parseInt(gap_id));

const remaining_items = document.querySelector("#remaining-items")!;
Object.entries(JSON.parse(document.querySelector<HTMLTextAreaElement>("#solution")!.innerHTML).gaps as {[gap_id: number]: string[]})
    .filter(([gap_id, items]) => free_gaps.includes(parseInt(gap_id)))
    .forEach(([gap_id, items]) =>
        items.forEach(item => render_item(remaining_items, item))
    );



/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function(e) {
    if (Object.values(gap_lists).some(list  => list.toArray()?.length !== 1)) {
        e.preventDefault();

        Object.keys(gap_lists)
            .forEach(gap_id => document.querySelector(`[data-gap_id="${gap_id}"]`)!.classList.add("error--required"));
        return;
     }

    const gaps = Object.entries(gap_lists)
        .reduce((acc, [gap_id, list]) => {
            acc[parseInt(gap_id)] = list.toArray()[0];
            return acc;
        }, {} as {[gap_id: number]: string})

    answer_textarea.value = JSON.stringify({ ...JSON.parse(answer_textarea.value), gaps });
});
