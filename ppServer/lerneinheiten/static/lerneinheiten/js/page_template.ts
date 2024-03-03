// init MD-Editors
document.querySelectorAll("#inquiry-form textarea").forEach((textarea: any) => {

    let initialValue = textarea.value?.trim() || "";
    try {
        initialValue = JSON.parse(initialValue)["text"];
    } catch {};

    new EasyMDE({
        ...MDEditorConfig,
        element: textarea as HTMLElement,
        initialValue
    });
});
