class Grid {

    private tiles: (EditorTile | null)[][] = [[]];

    public get(x: number, y: number): EditorTile | null {
        if (this.tiles.length <= y) { return null; }
        if (this.tiles[y]!.length <= x) { return null; }
        return this.tiles[y]![x]!;
    }

    public set(x: number, y: number, tile: EditorTile | null): void {
        if (this.tiles.length <= y) { return; }
        if (this.tiles[y]!.length <= x) { return; }
        this.tiles[y]![x] = tile;
    }

    public all(): Tile[] {
        return this.tiles.reduce((tiles, row) => [...tiles, ...row.filter(tile => tile)], [] as any[]);
    }


    constructor() {
        this.set_dimensions(GRID_WIDTH, GRID_HEIGHT);
    }
    
    public set_dimensions(width: number, height: number): void {
        canvas.setAttribute("width", `${width * TILE_SIZE}px`);
        canvas.setAttribute("height", `${height * TILE_SIZE}px`);

        const tiles: (EditorTile | null)[][] = Array.from({length: GRID_HEIGHT}, () => Array.from({length: GRID_WIDTH}));
        for (let x = 0; x < GRID_WIDTH; x++) {
            for (let y = 0; y < GRID_HEIGHT; y++) {
                tiles[y]![x] = this.get(x, y);
            }
        }
        this.tiles = tiles;
        this.draw_empty_grid();
        this.all().forEach(tile => tile.draw());
    }


    public draw_empty_grid() {

        // draw background & wipe previous things
        ctx.beginPath();
        ctx.fillStyle = BACKGROUND_COLOR;
        ctx.fillRect(0, 0, GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE);
        ctx.closePath();
    
        // draw grid
        ctx.beginPath();
        ctx.lineWidth = LINE_WIDTH;
        ctx.strokeStyle = GRID_COLOR;
        for (let x = 0; x <= GRID_WIDTH * TILE_SIZE; x += TILE_SIZE) {
            for (let y = 0; y <= GRID_HEIGHT * TILE_SIZE; y += TILE_SIZE) {
                ctx.moveTo(0, y);
                ctx.lineTo(GRID_WIDTH * TILE_SIZE, y);
    
                ctx.moveTo(x, 0);
                ctx.lineTo(x, GRID_HEIGHT * TILE_SIZE);
            }
        }
        ctx.stroke();
        ctx.closePath();
    }

    public clear(pos: Position): void {
        this.fill(pos);
        this.set(pos.x, pos.y, null);
    }

    public createTile(type: TileType, pos: Position, _stufe?: number, _connective_tags?: ConnectiveTag[], _converter_config?: Converter.ConverterConfig): EditorTile | null {
        if (pos.y >= GRID_HEIGHT || pos.x >= GRID_WIDTH || pos.y < 0 || pos.x < 0) {
            logger.error(`Out of game bounds (${pos.x}, ${pos.y})`);
            return null;
        }
        
        const tile: EditorTile = new EditorTile(type, pos);
        this.set(pos.x, pos.y, tile);

        // TODO
        // , stufe?: number, connective_tags?: ConnectiveTag[], converter_config?: Converter.ConverterConfig


        return tile;
    }

    public fill(pos: Position, color: string = BACKGROUND_COLOR): void {
        ctx.beginPath();
        ctx.fillStyle = GRID_COLOR;
        ctx.fillRect(pos.x * TILE_SIZE, pos.y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
        ctx.closePath();

        ctx.beginPath();
        ctx.fillStyle = color;
        const grid_offset = Math.ceil(LINE_WIDTH / 2)
        ctx.fillRect(pos.x * TILE_SIZE + grid_offset, pos.y * TILE_SIZE + grid_offset, TILE_SIZE - 2*grid_offset, TILE_SIZE - 2*grid_offset);
        ctx.closePath();
    }

    // TODO
    public test_grid(): boolean {
        return true;
    }


    public async save(event: SubmitEvent) {
        event.preventDefault();

        const name: string | null = (document.querySelector("[name=levelName]") as any)?.value;
        const width: number | null = parseInt((document.querySelector("[name=width]") as any)?.value);
        const height: number | null = parseInt((document.querySelector("[name=height]") as any)?.value);
        if (!name || width === null || height === null || !this.test_grid()) {
            alert("Nicht fertig");
            return false;
        }

        // grab all tiles
        const registered_tiles: TileConfig[] = grid.all().map(tile => ({
            pos: {...tile.pos},
            type: tile.TYPE
        }));
        // remember phenomenon spot for spawning a new one if this got destroyed
        const additional_placeholders: TileConfig[] = grid.all()
        .filter(tile =>
            Object.entries(TimeFissureType).includes(tile.TYPE as any) ||    
            Object.entries(AnomalyType).includes(tile.TYPE as any) ||    
            Object.entries(SpaceFissureType).includes(tile.TYPE as any)    
        ).map(tile => ({
            pos: tile.pos,
            type: PlaceholderType.GENERAL
        }));

        const form = event.target as HTMLFormElement;
        const tile_tag = document.createElement("input");
        tile_tag.name = "tiles";
        tile_tag.hidden = true;
        tile_tag.value = JSON.stringify([...registered_tiles, ...additional_placeholders]);
        form.appendChild(tile_tag);
        form.submit();
    }
}