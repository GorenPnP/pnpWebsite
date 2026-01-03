Dropzone.autoDiscover = false;

const root_element = document.querySelector("#content-grid")!;

enum Direction {
    ROW = "grid-row",
    COL = "grid-column"
}
namespace Direction {
    export function reverse(direction: Direction): Direction {
        return direction === Direction.ROW ? Direction.COL : Direction.ROW;
    }
}

/** always have a container around a single (or multiple) content-boxes! */
interface ContainerBoxConfig {
    type: "container";
    children: BoxConfig[];
}
interface TextBoxConfig {
    type: "text";
    text: string;
}
interface ImageBoxConfig {
    type: "image";
    src: string;
}
interface VideoBoxConfig {
    type: "video";
    iframe: string;
}
type BoxConfig = ContainerBoxConfig | TextBoxConfig | ImageBoxConfig | VideoBoxConfig;


abstract class Box {
    private static next_id: number = 1;
    private static boxes: {[id: number]: Box} = {};

    public id: number;
    protected parent: Box | null;
    protected direction: Direction;
    protected html_string: string = "";

    constructor(parent_id: number | null, direction: Direction) {
        this.parent = parent_id ? Box.get_Box(parent_id) : null;
        this.direction = direction;

        this.id = Box.next_id++;
        Box.boxes[this.id] = this;
    }

    public render(): string {
        return this.html_string;
    }
    public abstract init_editor(): void;
    public reverse_direction() {
        this.direction = Direction.reverse(this.direction);
    }

    public remove(): void {
        Box.get_DOM_element(this.id)?.remove();
        delete Box.boxes[this.id];
        (this.parent as ContainerBox).remove_child(this.id);
    }

    public abstract as_json(): BoxConfig | null;

    static get_Box(id: number): Box | null {
        return Box.boxes[id] || null;
    }
    static get_DOM_element(id: number): Element | null {
        return document.querySelector(`#box-${id}`) || null;
    }
    static create(parent_id: number | null, direction: Direction, config: BoxConfig): Box {
        switch (config.type) {
            case "container": return new ContainerBox(parent_id, direction, config);
            case "text": return new TextBox(parent_id, direction, config);
            case "image": return new ImageBox(parent_id, direction, config);
            case "video": return new VideoBox(parent_id, direction, config);
        }
    }
    static remove(id: number): void {
        Box.get_Box(id)?.remove();
    }
}

class TextBox extends Box {
    private md_editor: EasyMDE | null = null;
    private text: string;

    constructor(parent_id: number | null, direction: Direction, config: TextBoxConfig) {
        super(parent_id, direction);
        this.text = config.text || "";
        this.html_string = `<div id="box-${this.id}" class="${this.direction} box--text"><textarea id="md-editor-${this.id}"></textarea></div>`;
    }

    public init_editor(): void {
        if (this.md_editor) {
            this.md_editor.toTextArea();
        }

        this.md_editor = new EasyMDE({
            ...MDEditorConfig,
            element: document.querySelector(`#md-editor-${this.id}`) as HTMLElement,
            toolbar: [
                ...(MDEditorConfig.toolbar as []), "|", "|",
                {
                    name: 'remove', // remove text-box
                    action: () => this.remove(),
                    className: 'fa fa-times',
                    title: 'remove whole textblock',
                } as EasyMDE.ToolbarIcon
            ]
        });
        this.md_editor.value(this.text);
        this.md_editor.codemirror.on("change", () => {
            this.text = this.md_editor!.value();
        });
    }
    public as_json(): TextBoxConfig {
        return {
            type: "text",
            text: this.text
        };
    }
}
class NewBox extends Box {

    private static clicked: NewBox | null = null;

    constructor(parent_id: number | null, direction: Direction) {
        super(parent_id, direction);
        this.html_string = `<button id="box-${this.id}" class="${this.direction} box--new btn" data-bs-toggle="modal" data-bs-target="#new-block-modal" onclick="NewBox.add(${this.id})">+</button>`;
    }

    public init_editor(): void { }
    public as_json(): BoxConfig | null {
        return null;
    }


    public static add(id: number) {
        const new_box = Box.get_Box(id);
        if (!new_box) {
            console.error("NewBow not found, id: ", id);
            return;
        }

        NewBox.clicked = new_box;
    }
    public static replace() {
        const type: "text" | "image" | "video" = document.querySelector<HTMLSelectElement>("#new-box-type")!.value as "text" | "image" | "video";

        const new_box = NewBox.clicked;
        NewBox.clicked = null;
        if (!new_box) {
            console.error("No NewBox.clicked available");
            return;
        }
        
        const element = Box.get_DOM_element(new_box.id);
        if (!element) {
            console.error("No DOM-element available");
            return;
        }

        const parent_id = new_box.parent?.id;
        if (!parent_id) {
            console.error("No parent_id available");
            return;
        }
        
        const box = Box.create(parent_id, new_box.direction, {type: "container", children: [{type} as BoxConfig]});
        (new_box.parent as ContainerBox).replace_child(new_box.id, box);
    }
}
class ImageBox extends Box {
    static default_src = "https://www.maketecheasier.com/assets/uploads/2020/02/Lorem-Ipsum-Featured-800x400.jpg";

    private src: string = "";

    constructor(parent_id: number | null, direction: Direction, config: ImageBoxConfig) {
        super(parent_id, direction);
        this.update_internal_state(config.src);
    }
    private update_internal_state(src: string = "") {
        this.src = src;
        this.html_string = `<div id="box-${this.id}" class="${this.direction} box--image"><img src="${this.src || ImageBox.default_src}" loading="lazy"></div>`;
    }

    public init_editor(): void {

        // construct form for image
        const parent = document.createElement("div");
        parent.classList.add("editor-form", "image-form");
        const csrf_token = document.querySelector("#csrf_token")?.innerHTML || "";
        const img_upload_url = document.querySelector("#image-upload-url")?.innerHTML || "";
        const form_id = `image-form-${this.id}`;
        parent.innerHTML = `<form id="${form_id}" class="editor-form image-form dropzone" action="${img_upload_url}"><button class="btn btn-outline-light del-btn" onclick=Box.remove(${this.id})>X</button>${csrf_token}</form>`;

        const form = parent.querySelector("form")!;

        // display form
        const box_element = Box.get_DOM_element(this.id)!;
        box_element.querySelectorAll(".editor-form").forEach(form => form.remove());
        box_element.appendChild(form);

        // add dropzone
        const dropzone = new Dropzone("#"+form_id, {
            maxFiles: 1,
            acceptedFiles: "image/*",
            resizeWidth: 1000,
            resizeHeight: 1000,
            dictDefaultMessage: "Bild auswählen"
        });

        dropzone.on("success", (file) => {
            const src = JSON.parse(file.xhr?.response || "{}").uri || this.src;
            this.update_internal_state(src);

            // render (with changed iframe)
            (this.parent as ContainerBox).replace_child(this.id, this);
        });
    }

    public as_json(): ImageBoxConfig {
        return {
            type: "image",
            src: this.src,
        }
    }
}
class VideoBox extends Box {
    private static default_iframe = '<iframe src="https://www.youtube.com/embed/wDchsz8nmbo" title="1 Minute Sample Video" frameborder="0" referrerpolicy="strict-origin-when-cross-origin"></iframe>';

    // changed on setting new iframe in editor
    private iframe: string = "";

    constructor(parent_id: number | null, direction: Direction, config: VideoBoxConfig) {
        super(parent_id, direction);
        this.update_internal_state(config.iframe);
    }
    private update_internal_state(iframe: string = "") {
        this.iframe = iframe;
        this.html_string = `<div id="box-${this.id}" class="${this.direction} box--video">${this.iframe || VideoBox.default_iframe}</div>`;
    }

    public init_editor(): void {
        
        // add form for iframe
        const iframe_form = document.createElement("form");
        iframe_form.classList.add("editor-form", "iframe-form");
        iframe_form.innerHTML = `
        <button class="btn btn-outline-light del-btn" onclick=Box.remove(${this.id})>X</button>
            <label for="iframe-input-${this.id}">Youtube-Einbettungscode</label>
            <input id="iframe-input-${this.id}" pattern='<iframe .*src=\x22https://www.youtube.com/embed/.+\x22.*></iframe>' required>
            <button type="submit" class="btn btn-primary">Speichern</button>`;
        iframe_form.addEventListener("submit", VideoBox.replace(this.id))

        // display form
        const box = Box.get_DOM_element(this.id);
        box?.querySelectorAll(".iframe-form").forEach(form => form.remove());
        box?.appendChild(iframe_form);
    }

    public as_json(): VideoBoxConfig {
        return {
            type: "video",
            iframe: this.iframe
        }
    }


    public static replace(id: number): (event: SubmitEvent) => void {
        return (event: SubmitEvent) => {
            event?.preventDefault();

            const element = Box.get_DOM_element(id);
            if (!element) {
                console.error(`No Element with id ${id} available`);
                return;
            }
            
            const box = Box.get_Box(id) as VideoBox;
            if (!box) {
                console.error(`No VideoBox with id ${id} available`);
                return;
            }
            
            // adapt internal state
            const new_iframe = element.querySelector<HTMLInputElement>(`.iframe-form #iframe-input-${id}`)!.value;
            box.update_internal_state(new_iframe);

            // render (with changed iframe)
            (box.parent as ContainerBox).replace_child(id, box);
        }
    }
}
class ContainerBox extends Box {
    private child_boxes: Box[];

    constructor(parent_id: number | null, direction: Direction, config: ContainerBoxConfig) {
        super(parent_id, direction);
        
        const child_direction = Direction.reverse(this.direction);
        this.child_boxes = config.children.map(child_config => Box.create(this.id, child_direction, child_config));
        this.format_children();
    }
    private format_children() {
        this.child_boxes = this.child_boxes.filter(box => !(box instanceof NewBox));

        if (this.child_boxes.length > 1) {
            this.child_boxes = this.child_boxes.map(box => {
                if (box instanceof ContainerBox) { return box; }

                const new_container = Box.create(this.id, Direction.reverse(this.direction), {type: "container", children: []}) as ContainerBox;
                box.reverse_direction();
                new_container.add_child(box);
                return new_container;
            });
        }
        
        // add "NewBox"es in between other elements
        const child_direction = Direction.reverse(this.direction);
        this.child_boxes = this.child_boxes.reduce((acc, box) => [...acc, box, new NewBox(this.id, child_direction)], [new NewBox(this.id, child_direction)]);

        this.child_boxes.forEach(box => box instanceof ContainerBox && box.format_children());
    }

    public init_editor(): void {
        this.child_boxes.forEach(box => box.init_editor());
    }

    public render(): string {
        return `<div id="box-${this.id}" class="${this.direction} box--container">${this.child_boxes.map(box => box.render()).join("")}</div>`;
    }

    public remove(): void {
        this.child_boxes.forEach(box => box.remove());
        super.remove();
    }

    public reverse_direction() {
        super.reverse_direction();
        this.child_boxes.forEach(box => box.reverse_direction());
    }
    public as_json(): ContainerBoxConfig {
        return {
            type: "container",
            children: this.child_boxes.filter(box => !(box instanceof NewBox)).map(box => box.as_json()!)
        }
    }

    private rerender_with_children() {
        this.format_children();

        const parent = document.createElement("div");
        parent.innerHTML = this.render();
        Box.get_DOM_element(this.id)?.replaceWith(parent.firstChild!);
        this.init_editor();
    }
    public add_child(new_child: Box) {
        this.child_boxes.push(new_child);
        this.rerender_with_children();
    }
    public replace_child(former_child_id: number, new_child: Box) {
        this.child_boxes = this.child_boxes.map(box => box.id === former_child_id ? new_child : box);
        this.rerender_with_children();
    }
    public remove_child(child_id: number) {
        this.child_boxes = this.child_boxes.filter(box => box.id !== child_id);
        if (this.child_boxes.some(box => !(box instanceof NewBox))) {
            this.rerender_with_children();
        } else {
            (this.parent as ContainerBox).remove_child(this.id);
            this.remove();
        }

    }
}



/************** INIT *******************/

let config: ContainerBoxConfig = JSON.parse(document.querySelector("#content")!.innerHTML);
let root = Box.create(null, Direction.COL, config);

// fallback config
if (!root) {
    config = {
        type: "container",
        children: [{
            type: "container",
            children: [{
                type: "text",
                text: "# " + (document.querySelector(".topic")?.innerHTML.trim() || "Beispielüberschrift")
            }]
        }]
    };
    root = Box.create(null, Direction.COL, config);
}
root_element.innerHTML = root.render();
root.init_editor();

// hide textareas content & musterlösung
document.querySelectorAll<HTMLTextAreaElement>("#form textarea").forEach(element =>
    element.parentElement!.classList.add("hidden")
);

// send content data to BE to save
document.querySelector("#form")!.addEventListener("submit", function() {
    document.querySelector<HTMLTextAreaElement>("#id_content")!.value = JSON.stringify(root.as_json());
});


// sample_configs:
//     {"type":"container","children":[]},
//     {"type":"image","src":"https://safesearch.lol/image_proxy?url=https%3A%2F%2Fcdn.photographylife.com%2Fwp-content%2Fuploads%2F2014%2F06%2FNikon-D810-Image-Sample-6.jpg&h=888637128c8c682c22a88c3d3a7d9a6077a940c5406a8b52a20836f91781804b"},
//     {"type":"text","text":"<p><b>Lorem ipsum</b> dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.</p>"},
//     {"type":"video","iframe":"<iframe width=\\"880\\" height=\\"495\\" src=\\"https://www.youtube.com/embed/Y4fOc_YyKNE\\" title=\\"Zauberarten - Goren Pen and Paper/ LARP\\" frameborder=\\"0\\" allow=\\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share\\" allowfullscreen=\\"\\"></iframe>"}
