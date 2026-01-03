/**
 * Replaces Markdown-text in innerHTML of tags with class .markdown to html
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

/**
 * renders html from passed markdown text
 * 
 * @param {string} md_text 
 * @returns rendered html
 */
function md_to_html(md_text) {

    // overall HIDDEN container to work in
    const container = document.createElement("div");
    container.hidden = true;
    document.querySelector("body").appendChild(container);

    // init required resources
    const target_container = document.createElement("div");
    container.appendChild(target_container);

    const textarea = document.createElement("textarea");
    container.appendChild(textarea);

    const editor = new EasyMDE({ element: textarea });

    // render md to html for text
    target_container.innerHTML = editor.markdown(md_text);

    // add bootstrap table styling
    target_container.querySelectorAll("table").forEach(table => {
        
        // create container for responsive table
        const container = document.createElement("div");
        container.classList.add("table-responsive");
        table.replaceWith(container);
        
        // recreate table
        const new_table = table.cloneNode();
        new_table.classList.add("table");
        new_table.innerHTML = table.innerHTML;

        // add new table & delete old one
        container.appendChild(new_table);
        table.remove();
    });

    const final_text = target_container.innerHTML;

    // cleanup
    editor.toTextArea();
    container.remove();

    return final_text;
}


// render md to html for text
document.querySelectorAll(".markdown").forEach(element =>
    element.innerHTML = md_to_html(element.dataset.text)
);
