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

// init required resources
const textarea = document.createElement("textarea");
textarea.hidden = true;
document.querySelector("body").appendChild(textarea);

const editor = new EasyMDE({ element: textarea });
document.querySelector(".EasyMDEContainer").setAttribute("hidden", true);

// render md to html for text
document.querySelectorAll(".markdown").forEach(element =>
    element.innerHTML = editor.markdown(element.dataset.text)
);

// add bootstrap table styling
document.querySelectorAll(".markdown table").forEach(table => {
    
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

// cleanup
editor.toTextArea();
textarea.remove();