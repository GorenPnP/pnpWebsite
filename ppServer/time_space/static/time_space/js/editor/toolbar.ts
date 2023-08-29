class Toolbar {
    private activeType!: TileType;
    private tiles: EditorTile[] = [];

    get active(): TileType {
        return this.activeType;
    }

    set active(type: TileType) {
        this.activeType = type;
        document.querySelectorAll(".tile.active").forEach(tile => tile.classList.remove("active"));
        document.querySelector(`.tile.tile-${this.activeType.replaceAll(" ", "_")}`)?.classList.add("active");
    }

    constructor() {
        this.init();
        this.active = this.tiles[0]!.TYPE;
    }

    private init() {
        const all_types =
            ([] as TileType[]).concat(
                Object.values(PlaceholderType),
                Object.values(WireType),
                Object.values(GateType),
                Object.values(TimeFissureType),
                Object.values(AnomalyType),
                Object.values(SpaceFissureType),
            )
        for (const type of all_types) {
            this.tiles.push(new EditorTile(type));
        }
    }
}
