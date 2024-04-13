// init MD-Editors
const mdeditors: EasyMDE[] = [...document.querySelectorAll<HTMLTextAreaElement>("#form textarea")].map(element => {

    let initialValue = element.value?.trim() || "";
    try {
        initialValue = JSON.parse(initialValue)["text"] || " ";
    } catch {};

    return new EasyMDE({
        ...MDEditorConfig,
        element,
        initialValue
    });
});

function canvasToFileList(canvas: HTMLCanvasElement, img_name: string): Promise<FileList> {
    return new Promise(function(resolve, reject) {
        canvas.toBlob((blob) => {
            if (!blob) { reject(); }

            const dt = new DataTransfer();
            dt.items.add(new File([blob!], img_name+".png"));
            resolve(dt.files);
        }, 'image/png');
    });
}

/************** SUBMIT *******************/
document.querySelector<HTMLButtonElement>('[type="submit"][form="form"]')?.setAttribute("form", "dummy-form");

// send content data to BE to save
document.querySelector<HTMLFormElement>("#dummy-form")!.addEventListener("submit", function (e) {
    e.preventDefault();

    const form = document.querySelector<HTMLFormElement>("#form")!;
    submit(form);
});

async function submit(form: HTMLFormElement): Promise<void> {
    form.solution_drawn.files = await canvasToFileList(canvas, "drawn");
    form.solution_bg.files = await canvasToFileList(bg_canvas, "bg");

    form.submit();
}