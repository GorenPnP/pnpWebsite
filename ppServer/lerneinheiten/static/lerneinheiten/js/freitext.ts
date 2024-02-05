// init MD-Editors
[...(document.querySelectorAll("main textarea") as any)].map((element: any) =>

    new EasyMDE({
        ...MDEditorConfig,
        element: element as any as HTMLElement,
        initialValue: JSON.parse(element.value || "{}")["text"] || ""
    })
);

/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {
    this.querySelectorAll("textarea").forEach((textarea: any) => textarea.value = `{"text":"${textarea.value}"}`);
});
