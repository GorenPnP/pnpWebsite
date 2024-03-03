// init MD-Editors
[...(document.querySelectorAll("#form textarea") as any)].forEach((element: any) => {

    let initialValue = element.value?.trim() || "";
    try {
        initialValue = JSON.parse(initialValue)["text"];
    } catch {};

    new EasyMDE({
        ...MDEditorConfig,
        element: element as any as HTMLElement,
        initialValue
    })
});

/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {
    this.querySelectorAll("textarea").forEach((textarea: any) => textarea.value = JSON.stringify({text: textarea.value}));
});
