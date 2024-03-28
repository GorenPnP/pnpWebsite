/**
 * Replaces Markdown-text in innerHTML of tags with class .markdown--lückentext to html
 * Needs to import <script src="{% static 'res/js/easymde@2.18.0.min.js' %}"></script> first.
 * 
 * Import/use like this:
 * 
 * <script src="{% static 'res/js/easymde@2.18.0.min.js' %}"></script>
 * <script src="{% static 'res/js/markdown.js' %}" defer></script>
 * 
 * <!-- musterlösung -->
 * {{ object.content|json_script:"content" }}
 * {{ object.solution|json_script:"solution" }}
 * <script src="{% static 'lerneinheiten/js/lückentext_musterlösung.js' %}" defer></script>
 * 
 * Use like this:
 * <div class="markdown--lückentext"></div>
 */

// init required resources
const textarea_lückentext = document.createElement("textarea");
textarea_lückentext.hidden = true;
document.querySelector("body")!.appendChild(textarea_lückentext);

const editor_lückentext = new EasyMDE({ element: textarea_lückentext });

// render md to html for text
let solution_text: string = JSON.parse(document.querySelector("#content")!.innerHTML)["text"];
const gaps: {[gap_id: number]: string[]} = JSON.parse(document.querySelector("#solution")!.innerHTML)["gaps"];

// display gap properly
solution_text = solution_text.replace(/<id:(\d+)>/gi, (full_match, gap_id: string) =>
    `<span class="md-gap"><code>${gaps[parseInt(gap_id.trim())].join("</code><code>")}</code></span>`
);
document.querySelector(".markdown--lückentext")!.innerHTML = (editor_lückentext as any).markdown(solution_text);


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
editor_lückentext.toTextArea();
textarea_lückentext.remove();