class Wire extends Tile {
    public readonly is_phenomenon: boolean = false;
    public readonly TYPE: WireType;
    private routes: {[input in Direction]?: Direction[]} = {};

    public incoming(...inputs: Input[]): TileInput[] | null {
        inputs = inputs.filter(input => this.has_input_at(input.from_direction));
        if (!inputs.length) { return null; }

        // just pass it on to the next tiles in output direction
        const new_inputs: TileInput[] = [];
        for (const {from_direction, command} of inputs) {

            const new_input_tiles = this.routes[from_direction]!
                .map(dir => {
                    const neighbor = this.get_neighbors([dir]);
                    if (neighbor?.length === 1) {
                        return {command, tile: neighbor[0]!, from_direction: reverse_direction([dir])[0]! };
                    }
                    return null;
                })
                .filter(out => out) as TileInput[];

            new_inputs.push(...new_input_tiles);
        }
        return new_inputs.length ? new_inputs : null;
    }

    public has_input_at(direction: Direction): boolean {
        return Object.keys(this.routes).includes(direction);
    }

    public has_output_at(direction: Direction): boolean {
        return Object.values(this.routes).reduce((acc, set) => [...acc, ...set], []).includes(direction);
    }

    public after_round() { }

    constructor(pos: Position, type: WireType) {
        super(pos);
        this.TYPE = type;

        this.set_image(determine_img_url(this.TYPE).url!);

        switch (type) {
            case WireType.WIRE_B_TO_T:
                this.routes = { "bottom": [Direction.T] };
                break;
            case WireType.WIRE_B_TO_L:
                this.routes = { "bottom": [Direction.L] };
                break;
            case WireType.WIRE_B_TO_R:
                this.routes = { "bottom": [Direction.R] };
                break;
            case WireType.WIRE_B_TO_LR:
                this.routes = { "bottom": [Direction.L, Direction.R] };
                break;
            case WireType.WIRE_B_TO_TL:
                this.routes = { "bottom": [Direction.T, Direction.L] };
                break;
            case WireType.WIRE_B_TO_TR:
                this.routes = { "bottom": [Direction.T, Direction.R] };
                break;
            case WireType.WIRE_B_TO_TLR:
                this.routes = { "bottom": [Direction.T, Direction.L, Direction.R] };
                break;
            case WireType.WIRE_L_TO_R:
                this.routes = { "left": [Direction.R] };
                break;
            case WireType.WIRE_L_TO_T:
                this.routes = { "left": [Direction.T] };
                break;
            case WireType.WIRE_L_TO_TR:
                this.routes = { "left": [Direction.T, Direction.R] };
                break;
            case WireType.WIRE_R_TO_L:
                this.routes = { "right": [Direction.L] };
                break;
            case WireType.WIRE_R_TO_T:
                this.routes = { "right": [Direction.T] };
                break;
            case WireType.WIRE_R_TO_TL:
                this.routes = { "right": [Direction.T, Direction.L] }
                break;
            case WireType.WIRE_DOUBLE_CROSS_TO_L:
                this.routes = {
                    "bottom": [Direction.T],
                    "right": [Direction.L],
                }
                break;
            case WireType.WIRE_DOUBLE_CROSS_TO_R:
                this.routes = {
                    "bottom": [Direction.T],
                    "left": [Direction.R],
                }
                break;
            case WireType.WIRE_DOUBLE_TO_TL:
                this.routes = {
                    "bottom": [Direction.L], 
                    "right": [Direction.T], 
                }
                break;
            case WireType.WIRE_DOUBLE_TO_TR:
                this.routes = {
                    "bottom": [Direction.R], 
                    "left": [Direction.T], 
                }
                break;
        }
    }
}
