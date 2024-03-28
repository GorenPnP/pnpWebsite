// init MD-Editors
const answer_textarea = document.querySelector<HTMLTextAreaElement>("#form textarea#id_answer")!;
answer_textarea.closest("p")!.classList.add("hidden");



/**
 * Replaces Markdown-text in innerHTML of tags with class .markdown to html
 * 
 * !!! REPLACES GAPS WITH INPUT TAGS
 * 
 * Needs to import <script src="{% static 'res/js/easymde@2.18.0.min.js' %}"></script> first.
 * 
 * Import/use like this:
 * 
 * <script src="{% static 'res/js/easymde@2.18.0.min.js' %}"></script>
 * <script src="{% static 'res/js/markdown.js' %}" defer></script>
 * 
 * Use like this:
 * <div class="markdown" data-text="..."></div>
 */

// init required resources
const textarea_lücken = document.createElement("textarea");
textarea_lücken.hidden = true;
document.querySelector("body")!.appendChild(textarea_lücken);

const editor_lücken = new EasyMDE({ element: textarea_lücken });

// render md to html for text
const element = document.querySelector<HTMLDivElement>(".markdown--lücken")!;
let text = (element as any).dataset.text.replace(/<id:(\d+)>/gi, (full_match: string, gap_id: string) => {
    const value = JSON.parse(answer_textarea.innerHTML).gaps?.[gap_id] || "";
    return `<input class="input-gap" data-gap_id="${gap_id}" value="${value}" form="form" required>`;
})
text = (editor_lücken as any).markdown(text);

// display gap properly
element.innerHTML = text;


// add bootstrap table styling
document.querySelectorAll(".markdown table").forEach(table => {
    
    // create container for responsive table
    const container = document.createElement("div");
    container.classList.add("table-responsive");
    table.replaceWith(container);
    
    // recreate table
    const new_table: any = table.cloneNode();
    new_table.classList.add("table");
    new_table.innerHTML = table.innerHTML;

    // add new table & delete old one
    container.appendChild(new_table);
    table.remove();
});

// cleanup
editor_lücken.toTextArea();
textarea_lücken.remove();



/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {
    const gaps = [...document.querySelectorAll<HTMLInputElement>("input.input-gap")]
        .reduce((acc, input_tag) => {
            acc[parseInt((input_tag as any).dataset.gap_id)] = input_tag.value;
            return acc;
        }, {} as {[gap_id: number]: string})

    answer_textarea.value = JSON.stringify({ ...JSON.parse(answer_textarea.value), gaps });
});
