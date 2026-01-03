class Placeholder extends BlockTile {
    public readonly is_phenomenon: boolean = false;
    public TYPE: PlaceholderType;
    private color: string | null = null;

    public incoming(..._: Input[]): TileInput[] | null {
        return null;
    }
    public after_round() { }

    public draw(): void {

        if (this.color) {
            ctx.beginPath();
            ctx.fillStyle = this.color;
            ctx.fillRect(this.pos.x * TILE_SIZE, this.pos.y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
            ctx.closePath();
        }
    }

    constructor(pos: Position, type: PlaceholderType) {
        super(pos);

        this.TYPE = type;
        if (DEBUG) {
            this.color = determine_img_url(this.TYPE).color;
            this.draw();
        }
    }
}
