interface Clickable {
    click(): any;
}
const isClickable = (tile: any): tile is Clickable => {
    return 'click' in tile;
}

abstract class Tile {
    public abstract readonly is_phenomenon: boolean;
    public abstract readonly TYPE: TileType;
    public connective_tags: ConnectiveTag[];

    protected img!: HTMLImageElement;
    public pos: Position;
    public stufe: number | null = null;

    constructor(pos: Position, connective_tags: ConnectiveTag[] = []) {
        this.pos = pos;
        this.connective_tags = connective_tags;
    }

    protected set_image(img_url: string): void {
        this.img = new Image(TILE_SIZE, TILE_SIZE);
        this.img.onload = () => this.draw();  // Draw when image has loaded
        this.img.src = img_url;
    }

    public abstract incoming(...inputs: Input[]): TileInput[] | null
    public abstract after_round(): void;

    public draw() {
        ctx.drawImage(this.img, this.pos.x * TILE_SIZE, this.pos.y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
    }

    public abstract has_input_at(direction: Direction): boolean;
    public abstract has_output_at(direction: Direction): boolean;

    public get_neighbors(directions: Direction[] = [Direction.B, Direction.T, Direction.L, Direction.R]): Tile[] {
        const coords = [];
        if (directions.includes(Direction.B)) { coords.push({x: this.pos.x, y: this.pos.y+1 }); }
        if (directions.includes(Direction.T)) { coords.push({x: this.pos.x, y: this.pos.y-1 }); }
        if (directions.includes(Direction.L)) { coords.push({x: this.pos.x-1, y: this.pos.y }); }
        if (directions.includes(Direction.R)) { coords.push({x: this.pos.x+1, y: this.pos.y }); }

        return coords
            .filter(pos => pos.y < GRID_HEIGHT && pos.x < GRID_WIDTH && pos.y >= 0 && pos.x >= 0)
            .map(pos => game_board.get(pos.x, pos.y))
            .filter(tile => tile)

            // if this is wire: use all defined. Else: only use wire neighbors
            .filter(tile => this instanceof Wire || tile instanceof Wire) as Tile[]
    }
}


/**
 * blocky tiles such as gates, fissures and so on. Basically everything except wires.
 * Determines in- and outputs based on the neighboring wires.
 */
abstract class BlockTile extends Tile {
    public is_blurred: boolean = false;

    protected get_input_directions(): (Direction.B | Direction.L | Direction.R)[] {
        let inputs: (Direction.B | Direction.L | Direction.R)[] = [];
        for (const direction of [Direction.B, Direction.L, Direction.R]) {

            const n = this.get_neighbors([direction]);
            if (n.length === 1 && n[0]!.has_output_at(reverse_direction([direction])[0]!)) { inputs.push(direction as any); }
        }
        return inputs;
    }

    protected get_output_directions(): (Direction.T | Direction.L | Direction.R)[] {
        let outputs: (Direction.T | Direction.L | Direction.R)[] = [];
        for (const direction of [Direction.T, Direction.L, Direction.R]) {

            const n = this.get_neighbors([direction]);
            if (n.length === 1 && n[0]!.has_input_at(reverse_direction([direction])[0]!)) { outputs.push(direction as any); }
        }
        return outputs;
    }

    public has_input_at(direction: Direction): boolean {
        return this.get_input_directions().includes(direction as any);
    }
    public has_output_at(direction: Direction): boolean {
        return this.get_output_directions().includes(direction as any);
    }

    public destroy() {
        const inputs = this.get_input_directions();
        const outputs = this.get_output_directions();

        game_board.remove_draw(this.pos);
        document.querySelector(`.blur.blur-${this.pos.x}-${this.pos.y}`)?.remove();

        if (inputs.length && outputs.length) {
            game_board.createTile(get_wire(inputs, outputs)!, this.pos);

        } else {
            game_board.set(this.pos.x, this.pos.y, null);
        }
    }

    public draw(): void {
        super.draw();

        // add text of type
        if (DEBUG) {
            ctx.beginPath();
            ctx.font = "bold 12px verdana, sans-serif ";
            ctx.fillStyle = "black";
            ctx.textAlign = "center";
            ctx.fillText(this.TYPE, this.pos.x * TILE_SIZE + TILE_SIZE/2, this.pos.y *TILE_SIZE + TILE_SIZE/2, TILE_SIZE);
            ctx.closePath();
        }

        // handle blurring

        const blur = document.querySelector(`.blur.blur-${this.pos.x}-${this.pos.y}`);
        
        // add blur if not already existent
        if (this.is_blurred && !blur) {
            const new_blur = document.createElement("div");
            new_blur.classList.add("blur", `blur-${this.pos.x}-${this.pos.y}`, isClickable(this) ? "clickable" : "");
            new_blur.style.setProperty("--x", `${this.pos.x}`);
            new_blur.style.setProperty("--y", `${this.pos.y}`);
            canvas_container.appendChild(new_blur);
        }
        
        // remove blur overlay
        if (!this.is_blurred && blur) {
            blur!.remove();
        }
    }
}
