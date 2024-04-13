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

// use dummy-form as trigger for saving solution-images. Submit #form afterwards.
document.querySelector<HTMLButtonElement>("[type='submit'][form='form']")?.setAttribute("form", "dummy-form");

/************** SUBMIT *******************/


async function save_canvas(canvas: HTMLCanvasElement, img_name: string, endpoint: string) {
    return new Promise(function(resolve, reject) {
        // convert to Blob (async)
        canvas.toBlob(blob => {
            if (!blob) {
                reject();
                return;
            }

            const file = new File([blob], img_name);
            const dT = new DataTransfer();
            dT.items.add(file);

            const data = new FormData()
            data.append('file', dT.files[0])

            fetch(endpoint, {
                method: 'post',
                headers: [['X-CSRFToken', document.querySelector<HTMLInputElement>('[name="csrfmiddlewaretoken"]')!.value]],
                body: data
            })
            .then(res => res.json())
            .then(e => resolve(e.uri))
            .catch(reject);
        });
    });
}

// send content data to BE to save
document.querySelector<HTMLFormElement>("#dummy-form")!.addEventListener("submit", function (e: SubmitEvent) {
    e.preventDefault();
    // mdeditors.forEach(e => e.toTextArea());

    const form = document.querySelector<HTMLFormElement>("form#form")!;
    const endpoint = document.querySelector("#image_upload_endpoint")!.innerHTML;
    
    Promise.allSettled([
        save_canvas(canvas, "solution_drawing.png", endpoint),
        save_canvas(bg_canvas, "solution_bg.png", endpoint),
    ]).then(res => {
        
        const solution = {
            drawn: res[0].status === "fulfilled" ? res[0].value : "",
            bg: res[1].status === "fulfilled" ? res[1].value : "",
        };
        
        form.querySelector<HTMLTextAreaElement>("#id_content")!.setAttribute("value", JSON.stringify({text: form.content.value}));
        form.querySelector<HTMLTextAreaElement>("#id_solution")!.setAttribute("value", JSON.stringify({text: form.solution.value, ...solution}));

        console.log(form.content.value, form.solution.value)
        form.submit();
    });
});