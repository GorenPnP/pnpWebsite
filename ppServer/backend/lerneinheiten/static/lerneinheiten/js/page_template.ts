// init MD-Editors
document.querySelectorAll<HTMLTextAreaElement>("#inquiry-form textarea").forEach(element => {

    let initialValue = element.value?.trim() || "";
    try {
        initialValue = JSON.parse(initialValue)["text"] || " ";
    } catch {};

    new EasyMDE({
        ...MDEditorConfig,
        element,
        initialValue
    });
});
