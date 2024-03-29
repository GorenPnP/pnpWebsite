function _replaceSelection(cm: any, active: boolean, startEnd: any[], url: string) {
    if(/editor-preview-active/.test(cm.getWrapperElement().lastChild.className))
        return;

    var text;
    var start = startEnd[0];
    var end = startEnd[1];
    var startPoint = cm.getCursor("start");
    var endPoint = cm.getCursor("end");
    if(url) {
        end = end.replace("#url#", url);
    }
    if(active) {
        text = cm.getLine(startPoint.line);
        start = text.slice(0, startPoint.ch);
        end = text.slice(startPoint.ch);
        cm.replaceRange(start + end, {
            line: startPoint.line,
            ch: 0
        });
    } else {
        text = cm.getSelection();
        cm.replaceSelection(start + text + end);

        startPoint.ch += start.length;
        if(startPoint !== endPoint) {
            endPoint.ch += start.length;
        }
    }
    cm.setSelection(startPoint, endPoint);
    cm.focus();
}
function drawGap(editor: any) {
    const ids: number[] = [...editor.value().matchAll(/\<id:(\d+)\>/gi)].map((match: string[]) => parseInt(match[1]));
    const next_id = Math.max(...ids, 0) +1;

	var cm = editor.codemirror;
	var options = [`¿¿<id:${next_id}> .`, ".. | ... ??"];
	_replaceSelection(cm, false //stat.table
    , options, "");
}


function get_previewLückentextRender(editor: EasyMDE) {
    return (markdownPlaintext: string, previewElement?: HTMLElement) => {
        const text: string = markdownPlaintext.replace(/¿¿\<id:(\d+)\>([^?]*)\?\?/gi, function (whole_snippet: string, gap_id: string, content: string) {
            const formatted_content = content.split("|")
                .map(option => `<code>${option.trim()}</code>`)
                .join("");

            return `<span class="md-gap">${formatted_content}</span>`;
        });

        return (editor as any).markdown(text);
    }
}