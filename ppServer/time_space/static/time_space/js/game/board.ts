enum OrderPrio {
    RUNNER = 0,
    LINEARRISS = 1,
    OTHER = 2,
    TIMELAGGER = 3,
};
enum NumberPrio {
    LINEARRISS = 0,
    OTHER = 2,
};


class GameBoard {

    public get(x: number, y: number): Tile | null {
        if (this.tiles.length <= y) { return null; }
        if (this.tiles[y]!.length <= x) { return null; }
        return this.tiles[y]![x]!;
    }

    public set(x: number, y: number, tile: Tile | null): void {
        if (this.tiles.length <= y) { return; }
        if (this.tiles[y]!.length <= x) { return; }
        this.tiles[y]![x] = tile;
    }

    public all(): Tile[] {
        return this.tiles.reduce((tiles, row) => [...tiles, ...row.filter(tile => tile)], [] as any[]);
    }

    public get_placeholders(): Placeholder[] {
        return this.placeholders;
    }

    private tiles: (Tile | null)[][] = [[]];
    private placeholders: Placeholder[] = [];
    private rounds = 0;
    /** zehnerstelle sum(stufe) of all */
    private gate_breakpoint: number = 0;

    private blocked_commands: {[command: string]: number} = {};


    constructor() {
        this.tiles = Array.from({length: GRID_HEIGHT}).map(() => Array.from({length: GRID_WIDTH}).map(() => null));
    }

    public createTile(type: TileType, pos: Position, stufe?: number, connective_tags?: ConnectiveTag[], converter_config?: Converter.ConverterConfig): Tile | null {
        if (pos.y >= GRID_HEIGHT || pos.x >= GRID_WIDTH || pos.y < 0 || pos.x < 0) {
            logger.error(`Out of game bounds (${pos.x}, ${pos.y})`);
            return null;
        }
        
        let tile: Tile | null = null;
        switch (type) {

            // Wires
            case WireType.WIRE_B_TO_T:
            case WireType.WIRE_B_TO_L:
            case WireType.WIRE_B_TO_R:
            case WireType.WIRE_B_TO_LR:
            case WireType.WIRE_B_TO_TL:
            case WireType.WIRE_B_TO_TR:
            case WireType.WIRE_B_TO_TLR:
            case WireType.WIRE_L_TO_R:
            case WireType.WIRE_L_TO_T:
            case WireType.WIRE_L_TO_TR:
            case WireType.WIRE_R_TO_L:
            case WireType.WIRE_R_TO_T:
            case WireType.WIRE_R_TO_TL:
            case WireType.WIRE_DOUBLE_CROSS_TO_L:
            case WireType.WIRE_DOUBLE_CROSS_TO_R:
            case WireType.WIRE_DOUBLE_TO_TL:
            case WireType.WIRE_DOUBLE_TO_TR:
                tile = new Wire(pos, type); break;

            // Gates
            case GateType.GATE_MIRROR: tile = new Mirror(pos, connective_tags); break;
            case GateType.GATE_INVERTER: tile = new Inverter(pos, connective_tags); break;
            case GateType.GATE_BUTTON_ON: tile = new ButtonOn(pos, connective_tags); break;
            case GateType.GATE_BUTTON_OFF: tile = new ButtonOff(pos, connective_tags); break;
            case GateType.GATE_SWITCH: tile = new Switch(pos, connective_tags); break;
            case GateType.GATE_CONVERTER: tile = new Converter(pos, converter_config, connective_tags); break;
            case GateType.GATE_BARRIER: tile = new Barrier(pos, stufe, connective_tags); break;
            case GateType.GATE_NO_MANA: tile = new NoMana(pos, connective_tags); break;
            case GateType.GATE_MANA_BOMB: tile = new ManaBomb(pos, connective_tags); break;
            case GateType.GATE_SUPPORT: tile = new Support(pos, connective_tags); break;
            case GateType.GATE_SENSOR: tile = new Sensor(pos, connective_tags); break;
            case GateType.GATE_TRACING: tile = new Tracing(pos, connective_tags); break;
            case GateType.GATE_TELEPORT_IN: tile = new TeleportIn(pos, connective_tags); break;
            case GateType.GATE_TELEPORT_OUT: tile = new TeleportOut(pos, connective_tags); break;

            // TimeFissures
            case TimeFissureType.TIME_LINIENDELETION: tile = new Liniendeletion(pos, stufe, connective_tags); break;
            case TimeFissureType.TIME_LINEARRISS: tile = new Linearriss(pos, stufe, connective_tags); break;
            case TimeFissureType.TIME_SPLINTER: tile = new Splinter(pos, stufe, connective_tags); break;
            case TimeFissureType.TIME_DUPLIKATOR: tile = new Duplikator(pos, stufe, connective_tags); break;
            case TimeFissureType.TIME_LOOPER: tile = new Looper(pos, stufe, connective_tags); break;
            case TimeFissureType.TIME_TIMELAGGER: tile = new Timelagger(pos, stufe, connective_tags); break;
            case TimeFissureType.TIME_TIMEDELAYER: tile = new Timedelayer(pos, stufe, connective_tags); break;
            case TimeFissureType.TIME_RUNNER: tile = new Runner(pos, stufe, connective_tags); break;

            // SpaceFissures
            case SpaceFissureType.SPACE_RAUMFISSUR: tile = new Raumfissur(pos, stufe, connective_tags); break;
            case SpaceFissureType.SPACE_WURMLOCH: tile = new Wurmloch(pos, stufe, connective_tags); break;
            case SpaceFissureType.SPACE_RAUMLOCH: tile = new Raumloch(pos, stufe, connective_tags); break;
            case SpaceFissureType.SPACE_KAPSELPHÄNOMEN: tile = new Kapselphänomen(pos, stufe, connective_tags); break;
            case SpaceFissureType.SPACE_BIZARRGEBIET: tile = new Bizarrgebiet(pos, stufe, connective_tags); break;

            // Anomalies
            case AnomalyType.ANOMALY_CONSUMER: tile = new Consumer(pos, stufe, connective_tags); break;
            case AnomalyType.ANOMALY_ERASER: tile = new Eraser(pos, stufe, connective_tags); break;
            case AnomalyType.ANOMALY_BLURR: tile = new Blurr(pos, stufe, connective_tags); break;
            case AnomalyType.ANOMALY_SHORT: tile = new Short(pos, stufe, connective_tags); break;
            case AnomalyType.ANOMALY_TRACEBACK: tile = new Traceback(pos, stufe, connective_tags); break;


            // Placeholders
            case PlaceholderType.GENERAL:
            case PlaceholderType.TIME_FISSURE:
            case PlaceholderType.SPACE_FISSURE:
            case PlaceholderType.ANOMALY:
                this.placeholders.push(new Placeholder(pos, type)); break;
        }

        // remember phenomenon spot for spawning a new one if this got destroyed
        this.set(pos.x, pos.y, tile);
        if (tile?.is_phenomenon && !this.placeholders.some(p => p.pos.x === tile?.pos.x && p.pos.y === tile?.pos.y)) {
            this.placeholders.push(new Placeholder(tile.pos, PlaceholderType.GENERAL));
        }
        return tile;
    }

    public tiles_by_tag(connective_tag: ConnectiveTag): Tile[] {
        return this.all().filter(tile => 
            tile.connective_tags.some(tag => tag.type === connective_tag.type && tag.id === connective_tag.id)
        );
    }

    public spawn_phenomenon(placeholder: PlaceholderType, type: TileType, stufe?: number, connective_tags?: ConnectiveTag[]) {
        if (type in WireType || type in GateType || type in PlaceholderType) { return; }
        if (
            type === AnomalyType.ANOMALY_SHORT ||
            type === AnomalyType.ANOMALY_TRACEBACK ||
            type === SpaceFissureType.SPACE_WURMLOCH
        ) {
            logger.error(`${type} is not allowed to auto-spawn because it needs to be connected`);
            return;
        }

        const specific_placeholders = this.placeholders.filter(p => p.TYPE === placeholder && !this.get(p.pos.x, p.pos.y));
        const placeholders = specific_placeholders.length ? specific_placeholders : this.placeholders.filter(p => p.TYPE === PlaceholderType.GENERAL && !this.get(p.pos.x, p.pos.y));
        const pos = placeholders.map(p => p.pos);

        // RAUMLOCH: spawn on gates & wires alongside the usual placeholders
        if (type === SpaceFissureType.SPACE_RAUMLOCH) {
            pos.push(...get_replaceable_wires());
            pos.push(...game_board.all().filter(tile => Object.values(GateType).includes(tile.TYPE as any)).map(tile => tile.pos));
        }

        // no space?
        if (!placeholders.length && type !== SpaceFissureType.SPACE_RAUMLOCH) {
            logger.warn(`No room for a new ${type}`);
            return;
        }
        
        const final_pos = get_random_of(pos);
        game_board.remove_draw(final_pos);
        this.createTile(type, final_pos, stufe, connective_tags);
    }

    public spawn_gate(): Gate | null {
        const wire_pos = get_replaceable_wires();
        if (!wire_pos.length) {
            logger.error("Cannot spawn gate, no space left");
            return null;
        }

        // get all gate types
        const phenomena = this.all().filter(tile => tile.is_phenomenon).map(phenomenon => phenomenon!.TYPE);

        const gate_type = [
            GateType.GATE_MIRROR,
            GateType.GATE_INVERTER,
            GateType.GATE_BUTTON_ON,
            GateType.GATE_BUTTON_OFF,
            GateType.GATE_SWITCH,
            GateType.GATE_CONVERTER,
            GateType.GATE_BARRIER,
        ];

        if (phenomena.includes(AnomalyType.ANOMALY_ERASER)) {
            gate_type.push(GateType.GATE_SUPPORT);
        }
        if (phenomena.includes(AnomalyType.ANOMALY_TRACEBACK)) {
            gate_type.push(GateType.GATE_TELEPORT_IN);
            gate_type.push(GateType.GATE_TELEPORT_OUT);
        }
        if (phenomena.includes(SpaceFissureType.SPACE_RAUMFISSUR)) {
            gate_type.push(GateType.GATE_SENSOR);
        }
        if (phenomena.includes(SpaceFissureType.SPACE_WURMLOCH)) {
            gate_type.push(GateType.GATE_TRACING);
        }
        if (phenomena.some(p => p in AnomalyType)) {
            gate_type.push(GateType.GATE_NO_MANA);
            gate_type.push(GateType.GATE_MANA_BOMB);
        }

        // get gate
        const gate = get_random_of(gate_type);

        // handle connections of new gate
        let connective_tags: ConnectiveTag[] | undefined;
        if (gate === GateType.GATE_TELEPORT_IN) {
            connective_tags = [{
                type: ConnectiveType.TELEPORT,
                id: get_random_string()
            }];
            this.createTile(GateType.GATE_TELEPORT_OUT, get_random_of(wire_pos), undefined, connective_tags);
        }
        if (gate === GateType.GATE_TELEPORT_OUT) {
            connective_tags = [{
                type: ConnectiveType.TELEPORT,
                id: get_random_string()
            }];
            this.createTile(GateType.GATE_TELEPORT_IN, get_random_of(wire_pos), undefined, connective_tags);
        }
        if (gate === GateType.GATE_MANA_BOMB) {
            const all_anomalies = this.all().filter(tile => Object.values(AnomalyType).includes(tile.TYPE as any)) as Anomaly[];
            if (all_anomalies.length) {
                connective_tags = [{
                    type: ConnectiveType.MANABOMBE_A,
                    id: get_random_string()
                }];
                const anomaly = get_random_of(all_anomalies)!;
                anomaly.connective_tags = [...(anomaly.connective_tags || []), ...connective_tags];
            }
        }

        // create gate
        return this.createTile(gate, get_random_of(wire_pos), undefined, connective_tags) as Gate | null;
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

    public remove_draw(pos: Position): void {
        ctx.beginPath();
        ctx.fillStyle = GRID_COLOR;
        ctx.fillRect(pos.x * TILE_SIZE, pos.y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
        ctx.closePath();

        ctx.beginPath();
        ctx.fillStyle = BACKGROUND_COLOR;
        const grid_offset = Math.ceil(LINE_WIDTH / 2)
        ctx.fillRect(pos.x * TILE_SIZE + grid_offset, pos.y * TILE_SIZE + grid_offset, TILE_SIZE - 2*grid_offset, TILE_SIZE - 2*grid_offset);
        ctx.closePath();
    }

    public block_command(command: Command, rounds: number) {
        if (rounds <= 0) { return; }
        this.blocked_commands[command] = (this.blocked_commands[command] || 0) + rounds+1;
    }
    public is_command_blocked(command: Command): boolean {
        return Object.keys(this.blocked_commands).includes(command);
    }


    public async after_round() {

        // round counter
        document.querySelector("#rounds")!.innerHTML = (++this.rounds).toString();

        // de-lock commands
        for (const command of Object.keys(this.blocked_commands)) {
            if (--this.blocked_commands[command] <= 0) {
                delete this.blocked_commands[command];
            }
        }

        // display blocked commands
        document.querySelector("#blocked-commands")!.innerHTML = Object.entries(this.blocked_commands)
            .map(([command, rounds]) => `<li>${command} für weitere ${rounds} Runden</li>`)
            .join('');


        // won?
        const is_won = this.tiles
            .reduce((acc, row) => [...acc, ...row.filter(tile => tile?.is_phenomenon)], [])
            .filter(phenomenon =>
                phenomenon!.TYPE !== SpaceFissureType.SPACE_KAPSELPHÄNOMEN &&
                phenomenon!.TYPE !== SpaceFissureType.SPACE_RAUMLOCH
            )
            .length === 0;

        if (is_won) {
            logger.log("You won");
        } else {
            await logger.log_round_answers();
        }


        // spawn/remove gates?
        const sum_stufe = this.all()
            .filter(tile => tile.is_phenomenon).map(p => p!.stufe!)
            .reduce((sum, stufe) => sum + stufe, 0);
        const new_breakpoint = Math.floor(sum_stufe / 10);
        logger.info("Stufensumme:", sum_stufe);

        if (this.gate_breakpoint < new_breakpoint) {
            Array.from({length: new_breakpoint - this.gate_breakpoint}).forEach(() => game_board.spawn_gate());
        }
        if (this.gate_breakpoint > new_breakpoint) {
            Array.from({length: this.gate_breakpoint - new_breakpoint}).forEach(() => {
                const all_gates = game_board.all().filter(tile => Object.values(GateType).includes(tile.TYPE as any)) as Gate[];
                if (!all_gates.length) {
                    logger.error("Cannot remove a gate since none are available");
                    return;
                }
                
                // destroy gate. Also destroy other half of teleport gate, if it has been a teleport gate
                const gate = get_random_of(all_gates);
                gate.destroy();
                const teleport_conn = gate.connective_tags.find(conn => conn.type === ConnectiveType.TELEPORT);
                if (teleport_conn) {
                    (this.tiles_by_tag(teleport_conn).find(tile => tile !== gate) as Gate).destroy();
                }
            });

        }
        this.gate_breakpoint = new_breakpoint;

        logger.info("round complete");
        logger.log("-----");
    }
}


function get_replaceable_wires(): Position[] {
    const get_neighbor_placeholders = (tile: Wire): Placeholder[] => {
        const coords: Position[] = [];
        if (tile.has_output_at(Direction.B)) { coords.push({x: tile.pos.x, y: tile.pos.y+1 }); }
        if (tile.has_output_at(Direction.T)) { coords.push({x: tile.pos.x, y: tile.pos.y-1 }); }
        if (tile.has_output_at(Direction.L)) { coords.push({x: tile.pos.x-1, y: tile.pos.y }); }
        if (tile.has_output_at(Direction.R)) { coords.push({x: tile.pos.x+1, y: tile.pos.y }); }

        return game_board.get_placeholders().filter(p => coords.some(({x, y}) => p.pos.x === x && p.pos.y === y));
    };

    const attached_neighbors = (tile: Wire): Tile[] => {
        return [Direction.B, Direction.T, Direction.L, Direction.R].reduce((neighbors, direction) => {
            if (!tile.has_input_at(direction) && !tile.has_output_at(direction)) { return neighbors; }

            const n = tile.get_neighbors([direction])[0];
            return n ? [...neighbors, n] : neighbors;
        }, [] as Tile[]);
    }

    return game_board.all().filter(tile =>
            (tile.pos.y !== GRID_HEIGHT-1 || !tile.has_input_at(Direction.B)) &&
            tile instanceof Wire &&
            attached_neighbors(tile).every(n => n === null || n instanceof Wire) &&
            !get_neighbor_placeholders(tile).length
        )
        .map(tile => tile.pos);
}