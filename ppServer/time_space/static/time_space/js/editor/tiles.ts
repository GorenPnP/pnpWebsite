class EditorTile {
    public readonly TYPE: TileType;
    public connective_tags: ConnectiveTag[] = [];

    protected img: HTMLImageElement | undefined;
    protected img_url: string | null;
    protected color: string;

    public pos: Position | null;
    public stufe: number | null = null;


    constructor(type: TileType, pos?: Position) {
        this.TYPE = type;
        this.pos = pos || null;
        const display = determine_img_url(this.TYPE);
        this.img_url = display.url;
        this.color = display.color;

        if (this.img_url) {
            this.set_image(this.img_url);
        } else {
            this.draw();
        }
    }

    protected set_image(img_url: string): void {
        this.img = new Image(TILE_SIZE, TILE_SIZE);
        this.img.onload = () => this.draw();  // Draw when image has loaded
        this.img.src = img_url;
    }

    public draw() {
        // main grid
        if (this.pos) {
            if (this.color) {
                grid.fill(this.pos, this.color);
            }
            if (this.img) {
                ctx.drawImage(this.img, this.pos.x * TILE_SIZE, this.pos.y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
            }

            // add text of type
            if (!Object.values(WireType).includes(this.TYPE as any)) {
                ctx.beginPath();
                ctx.font = "bold 10px sans-serif";
                ctx.fillStyle = "black";
                ctx.textAlign = "center";
                ctx.fillText(this.TYPE, this.pos.x * TILE_SIZE + TILE_SIZE/2, this.pos.y *TILE_SIZE + TILE_SIZE/2, TILE_SIZE);
                ctx.closePath();
            }
        } else {
            // toolbar
            const type = this.TYPE.replaceAll(" ", "_");

            if (document.querySelector(`.tile-${type}`)) { return; }

            const tile_button = document.createElement("button");
            tile_button.classList.add("tile", `tile-${type}`);
            if (this.img_url) { tile_button.style.setProperty("--bg-image", `url('${this.img_url}')`); }
            tile_button.type = "button";
            tile_button.style.setProperty("--bg-color", this.color);
            tile_button.style.setProperty("--text", Object.values(WireType).includes(this.TYPE as any) ? "" : `"${this.TYPE}"`);
            
            tile_button.onclick = () => { tb.active = this.TYPE; }
            
            document.querySelector("#fields")!.appendChild(tile_button);
        }
    }
}