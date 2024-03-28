// init MD-Editors
const solution_gaps: {text: string, gaps: {[gap_id: number]: string[]}} = JSON.parse(document.querySelector("#solution")!.innerHTML);

document.querySelectorAll<HTMLTextAreaElement>("#form textarea").forEach(element => {
    if (element.id !== "id_content") {
        element.parentElement!.classList.add("hidden");
    } else {

        let initialValue = element.value?.trim() || '';
        try {
            initialValue = JSON.parse(initialValue)["text"] || "";
        } catch {};
    
        const editor = new EasyMDE({
            ...MDEditorConfig,
            toolbar: [
                ...(MDEditorConfig.toolbar || []), "|",
                {
                    name: 'gap',
                    action: drawGap,
                    className: 'fa fa-pencil-square-o',
                    title: 'Insert Gap',
                },
            ],
            element
        });

        // replace gap_id with options
        initialValue = initialValue.replace(/<id:(\d+)>/gi, function (whole_snippet: string, gap_id: string) {
            const formatted_content = solution_gaps.gaps[parseInt(gap_id.trim())].join(" | ");
            return `¿¿${whole_snippet} ${formatted_content} ??`;
        });

        // set initialValue
        editor.value(initialValue);
        (editor as any).options.previewRender = get_previewLückentextRender(editor);
    }
});



/************** SUBMIT *******************/

// send content data to BE to save
document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function(e) {
    const content_textarea = this.querySelector<HTMLTextAreaElement>("textarea#id_content")!;
    
    const gaps: {[gap_id: number]: string[]} = [...content_textarea.value.matchAll(/\¿¿<id:(\d+)>([^?]*)\?\?/gi)]
    .reduce((acc, [full_match, gap_id, content]: string[]) => {
        acc[parseInt(gap_id)] = content.split("|").map(option => option.trim());
        return acc;
    }, {} as {[gap_id: number]: string[]});
    
    const content_text = content_textarea.value.replace(/¿¿\<id:(\d+)\>[^?]*\?\?/gi, (whole_snippet: string, gap_id: string) => `<id:${gap_id}>`);
    content_textarea.value = JSON.stringify({ text: content_text });
    
    const solution_textarea = this.querySelector<HTMLTextAreaElement>("textarea#id_solution")!;
    solution_textarea.value = JSON.stringify({ ...JSON.parse(solution_textarea.value), gaps });
});
