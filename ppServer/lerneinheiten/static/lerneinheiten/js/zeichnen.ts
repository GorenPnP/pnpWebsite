// init MD-Editors
document.querySelectorAll<HTMLTextAreaElement>("#form textarea").forEach(element => {
    element.parentElement!.classList.add("hidden");
});

/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {
    this.querySelectorAll<HTMLTextAreaElement>("textarea").forEach(textarea => textarea.value = JSON.stringify({text: textarea.value}));
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

// send content data to BE to save
document.querySelector<HTMLFormElement>("#dummy-form")!.addEventListener("submit", function (e) {
    e.preventDefault();

    const form = document.querySelector<HTMLFormElement>("#form")!;
    submit(form);
});

async function submit(form: HTMLFormElement): Promise<void> {
    form.answer_drawn.files = await canvasToFileList(canvas, "drawn");
    form.answer_bg.files = await canvasToFileList(bg_canvas, "bg");

    form.submit();
}