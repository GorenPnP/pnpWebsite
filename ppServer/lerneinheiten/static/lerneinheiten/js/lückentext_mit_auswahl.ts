interface Option {
    label: string;
    correct: boolean;
};

function render_item(element: HTMLSelectElement, item: Option): void {
    const option_tag = document.createElement("option");
    option_tag.value = item.label;   // TODO replace with other id?
    option_tag.innerHTML = item.label;
    element.appendChild(option_tag);
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
    return `<select data-gap_id="${gap_id}" form="form" required><option value="" disabled selected>--------</option></select>`;
}

// render md to html for text
const element = document.querySelector<HTMLDivElement>(".markdown--lücken")!;
const rendered_text = (element as any).dataset.text.replace(/<id:(\d+)>/gi, gap_replacement);

// display gap properly
element.innerHTML = md_to_html(rendered_text);


// set all select options
const solution_selects: {[gap_id: number]: {label: string, correct: boolean}[]} = JSON.parse(document.querySelector("#solution")!.innerHTML)["gaps"];
Object.entries(solution_selects).forEach(([gap_id, items]) => {
    const select = document.querySelector<HTMLSelectElement>(`[data-gap_id="${gap_id}"]`)!;
    items
        .sort(() => Math.floor(Math.random()*3-1))
        .forEach(item => render_item(select, item));
});


// set spieler's answers
const user_selection: {[gap_id: number]: string} = JSON.parse(answer_textarea.value).gaps || {};
Object.entries(user_selection).forEach(([gap_id, item]) => {
    document.querySelectorAll<HTMLOptionElement>(`select[data-gap_id="${gap_id}"] option`).forEach(option => option.selected = option.value === item);
});



/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {
    const gaps = [...document.querySelectorAll<HTMLSelectElement>("select[data-gap_id]")].reduce((acc, select) => {
        acc[parseInt(select.dataset.gap_id!)] = select.value;
        return acc;
    }, {} as {[gap_id: number]: string});

    answer_textarea.value = JSON.stringify({ ...JSON.parse(answer_textarea.value), gaps });
});
