// init MD-Editors
document.querySelectorAll<HTMLTextAreaElement>("#form textarea").forEach(element => {
    if (element.id !== "id_content") {
        element.parentElement!.classList.add("hidden");
    } else {
        let initialValue = element.value?.trim() || "";
        try {
            initialValue = JSON.parse(initialValue)["text"] || " ";
        } catch {};

        new EasyMDE({
            ...MDEditorConfig,
            element,
            initialValue
        })
    }
});

/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {
    this.querySelectorAll<HTMLTextAreaElement>("textarea").forEach(textarea => textarea.value = JSON.stringify({text: textarea.value}));
});
