/**
 * Is a default config for EasyMDE objects of type EasyMDE.Options
 * Should import <script src="{% static 'res/js/easymde@2.18.0.min.js' %}"></script> first.
 * 
 * Import/use like this:
 * <script src="{% static 'res/js/easymde@2.18.0.min.js' %}"></script>
 * <script src="{% static 'res/js/markdown_editorconfig.js' %}"></script>
 * 
 * <script src="custom.js" defer></script>
 * 
 * Use like this (in custom.js):
 * 
 *  new EasyMDE({
 *       ...MDEditorConfig,
 *       element: element as any as HTMLElement,
 *  });
 */

const MDEditorConfig = {
    spellChecker: false,
    toolbar: [
        "undo", "redo", "|",
        "bold", "italic", "heading-1", "heading-2", "heading-3", "|",
        "unordered-list", "ordered-list", {
            name: 'tables', // need to be verbose on "table"-option, because its class "table" gets all the styles from bootstrap -> use "tables" instead
            action: EasyMDE.drawTable,
            className: 'fa fa-table',
            title: 'Insert Table',
        }, "|",
        "link", "quote", "|",
        "preview", "side-by-side", "fullscreen", "|",
        "guide"
    ],
    forceSync: true,
}