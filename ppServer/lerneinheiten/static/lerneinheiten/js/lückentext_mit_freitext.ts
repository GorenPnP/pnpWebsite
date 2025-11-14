// init MD-Editors
const answer_textarea = document.querySelector<HTMLTextAreaElement>("#form textarea#id_answer")!;
answer_textarea.closest("p")!.classList.add("hidden");



/**
 * Renders Markdown-text in data-text of tags as innerHTML of tags with class .markdown--lücken
 * 
 * !!! REPLACES GAPS WITH INPUT TAGS
 * 
 * needs to include as deps:
 * <script src="{% static 'res/js/markdown.js' %}" defer></script>
 * 
 * Use like this:
 * <div class="markdown--lücken" data-text="..."></div>
 */

// render md to html for text
const element = document.querySelector<HTMLDivElement>(".markdown--lücken")!;
let text = (element as any).dataset.text.replace(/<id:(\d+)>/gi, (full_match: string, gap_id: string) => {
    const value = JSON.parse(answer_textarea.innerHTML).gaps?.[gap_id] || "";
    return `<input class="input-gap form-control d-inline" style="width: unset" data-gap_id="${gap_id}" value="${value}" form="form" required>`;
});

// display gap properly
element.innerHTML = md_to_html(text);




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
