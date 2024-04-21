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


// render md to html for text
let solution_text: string = JSON.parse(document.querySelector("#content")!.innerHTML)["text"];
const gaps: {[gap_id: number]: string[]} = JSON.parse(document.querySelector("#solution")!.innerHTML)["gaps"];

// display gap properly
solution_text = solution_text.replace(/<id:(\d+)>/gi, (full_match, gap_id: string) =>
    `<span class="md-gap"><code>${gaps[parseInt(gap_id.trim())].join("</code><code>")}</code></span>`
);
document.querySelector(".markdown--lückentext")!.innerHTML = md_to_html(solution_text);
