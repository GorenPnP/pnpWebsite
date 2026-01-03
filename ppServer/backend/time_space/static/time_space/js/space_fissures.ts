abstract class SpaceFissure extends BlockTile {
    public readonly is_phenomenon: boolean = true;
    public readonly TYPE: SpaceFissureType;
    public stufe: number;

    public round_state: PhenomenonRoundState = PhenomenonRoundState.NOT_HIT;

    constructor(pos: Position, type: SpaceFissureType, stufe: number = 1, connective_tags?: ConnectiveTag[]) {
        super(pos, connective_tags);
        this.TYPE = type;
        this.stufe = stufe;
        this.set_image(determine_img_url(this.TYPE).url!);
    }

    protected _log() {
        switch (this.round_state) {
            case PhenomenonRoundState.NOT_HIT: logger.register_round_answer(this, "0"); break;
            case PhenomenonRoundState.WRONG_COMMAND: this.stufe++; logger.register_round_answer(this, "1"); break;
            case PhenomenonRoundState.CORRECT_COMMAND: logger.register_round_answer(this, "2"); break;
            case PhenomenonRoundState.DESTROYED: logger.register_round_answer(this, "3"); break;
        }
        this.round_state = PhenomenonRoundState.NOT_HIT;
    }

    /**
     * Collects all incoming Commands form correctly attached wires.
     * @param inputs (unfiltered, can be of incorrect origin)
     * @returns all FILTERED commands
     */
    protected _process_incoming_commands(inputs: Input[]): Command[] {
        return inputs
            .filter(input => this.has_input_at(input.from_direction))
            .map(input => input.command);
    }

    public after_round() {
        if (this.round_state === PhenomenonRoundState.DESTROYED) {
            this.destroy();
        }

        this._log();
    }
}

class Raumfissur extends SpaceFissure {
    public incoming(...inputs: Input[]): TileInput[] | null {

        const commands = this._process_incoming_commands(inputs);

        if (commands.length) { this.round_state = PhenomenonRoundState.WRONG_COMMAND; }
        if (commands.includes(Command.MDV)) { this.round_state = PhenomenonRoundState.DESTROYED; }

        return null;
    }

    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, SpaceFissureType.SPACE_RAUMFISSUR, stufe, connective_tags);
    }
}
class Wurmloch extends SpaceFissure {

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = this._process_incoming_commands(inputs);
        if (!commands.length) {
            this.round_state = PhenomenonRoundState.NOT_HIT;
            return null;
        }

        const correct_commands = commands.filter(comm => comm === Command.BDV).length;
        this.stufe = Math.min(1, this.stufe - correct_commands);
        this.round_state = correct_commands > 0 ? PhenomenonRoundState.CORRECT_COMMAND : PhenomenonRoundState.WRONG_COMMAND;

        if (commands.includes(Command.CRYSTALLIZE)) {
            this.round_state = PhenomenonRoundState.DESTROYED;
        }
        if (this.round_state === PhenomenonRoundState.WRONG_COMMAND) {
            this.stufe++;
        }

        return null;
    }

    private hazard_stufe1() {
        // setup
        let all_gates = game_board.all().filter(tile => Object.values(GateType).includes(tile.TYPE as any)) as Gate[];
                
        // move random gate?
        if (Math.random() < 0.2 && all_gates.length) {
            const gate = get_random_of(all_gates);

            const wire_pos = get_replaceable_wires();
            if (wire_pos.length) {
                gate.destroy();
                gate.pos = get_random_of(wire_pos);
                game_board.set(gate.pos.x, gate.pos.y, gate);
                gate.draw;
            } else {
                logger.error("Wurmloch cannot move a Support Gate, no space left");
            }
        }

        // switch random gates?
        if (Math.random() < 0.2 && all_gates.length >= 2) {
            // get gates
            const gate1 = get_random_of(all_gates);
            all_gates = all_gates.splice(all_gates.indexOf(gate1), 1)
            const gate2 = get_random_of(all_gates);

            // switch positions
            const pos = gate1.pos;
            gate1.pos = gate2.pos;
            gate2.pos = pos;

            game_board.set(gate1.pos.x, gate1.pos.y, gate1);
            game_board.set(gate2.pos.x, gate2.pos.y, gate2);
            
            // draw
            game_board.remove_draw(gate1.pos);
            game_board.remove_draw(gate2.pos);
            gate1.draw();
            gate2.draw();
        } else {
            logger.error("Wurmloch cannot switch positions of random Gates, <2 Gates exist");
        }
    }
    private hazard_stufe2() {
        if (Math.random() < 0.05) {
            const wire_pos = get_replaceable_wires();
            if (!wire_pos.length) {
                logger.error("Wurmloch cannot spawn a Support Gate, no space left");
                return;
            }
            logger.info("Wurmloch  spawns a Support Gate");

            game_board.createTile(GateType.GATE_SUPPORT, get_random_of(wire_pos));
        }
    }
    private hazard_stufe3() {
        // setup
        const num_tracing_gates = game_board.all().filter(tile => tile.TYPE === GateType.GATE_TRACING).length;
            
        const kapselphenomena = game_board.all().filter(tile => tile.TYPE === SpaceFissureType.SPACE_KAPSELPHÄNOMEN) as Kapselphänomen[];

        // replace Kapselphänomen with Raumloch?
        if (Math.random() < (0.01 * num_tracing_gates) && kapselphenomena.length) {
            logger.info("Wurmloch replaces Kapselphänomen with Raumloch");

            const phenomenon = get_random_of(kapselphenomena);
            game_board.createTile(SpaceFissureType.SPACE_RAUMLOCH, phenomenon.pos);
        }
    }

    public after_round(): void {

        // destroy
        if (this.round_state === PhenomenonRoundState.DESTROYED) {
            this.destroy();
        } else {

            // do hazardous stuff
            this.stufe >= 1 && this.hazard_stufe1();
            this.stufe >= 2 && this.hazard_stufe2();
            this.stufe >= 3 && this.hazard_stufe3();
        }

        // log
        this._log();
        this.stufe = Math.min(3, this.stufe);
    }

    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, SpaceFissureType.SPACE_WURMLOCH, stufe, connective_tags);
    }
}
class Raumloch extends SpaceFissure {
    public incoming(...inputs: Input[]): TileInput[] | null {
        if (this._process_incoming_commands(inputs).length) {
            this.round_state = PhenomenonRoundState.WRONG_COMMAND;
        }

        return null;
    }
    public after_round(): void {
        super.after_round();

        this.stufe = 1;
    }

    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, SpaceFissureType.SPACE_RAUMLOCH, stufe, connective_tags);
    }
}
class Kapselphänomen extends SpaceFissure {
    private static resistance_map = [0.5, 0.4, 0.3, 0.2, 0.1];
    private round_counter: number = 0;

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = this._process_incoming_commands(inputs);
        
        // not hit
        if (!commands.length) {
            this.round_state = PhenomenonRoundState.NOT_HIT;
            return null;
        }
        
        // immune or wrong command
        if (this.round_counter % 5 !== 0 || !commands.includes(Command.BDV)) {
            this.round_state = PhenomenonRoundState.WRONG_COMMAND;
            return null;
        }

        // will die from correct command?
        if (Math.random() < Kapselphänomen.resistance_map[this.stufe-1]!) {
            this.round_state = PhenomenonRoundState.DESTROYED;
            return null;
        }

        // destruction unsuccessful
        this.round_state = PhenomenonRoundState.CORRECT_COMMAND;
        this.stufe = Math.max(0, Math.min(Kapselphänomen.resistance_map.length, this.stufe+1));

        logger.log("SPAWN RAUMLOCH");
        game_board.spawn_phenomenon(PlaceholderType.SPACE_FISSURE, SpaceFissureType.SPACE_RAUMLOCH);

        return null;
    }
    public after_round() {
        super.after_round();

        // correct stufe set by super.after_round()
        if (this.round_counter % 5 !!= 0) {
            this.stufe--;
        }
        this.round_counter++;

    }

    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, SpaceFissureType.SPACE_KAPSELPHÄNOMEN, stufe, connective_tags);
    }
}
class Bizarrgebiet extends SpaceFissure {
    private is_half_destroyed: boolean = false;

    private will_remove_gates: Gate[] = [];
    private will_spawn_gates: Gate[] = [];

    public incoming(...inputs: Input[]): TileInput[] | null {

        const commands = this._process_incoming_commands(inputs);

        // not hit
        if (commands.length === 0) {
            this.round_state = PhenomenonRoundState.NOT_HIT;
            return null;
        }

        // destroyed?
        const mono = commands.filter(comm => comm === Command.MDV).length;
        if (
            commands.includes(Command.MDBV) ||
            mono >= 2 ||
            (this.is_half_destroyed && mono)
        ) {
            this.round_state = PhenomenonRoundState.DESTROYED;
            return null;
        }

        this.is_half_destroyed = !!mono;
        this.round_state = mono ? PhenomenonRoundState.CORRECT_COMMAND : PhenomenonRoundState.WRONG_COMMAND;
        return null;
    }
    public after_round(): void {
        for (const gate of this.will_spawn_gates) {
            game_board.createTile(gate.TYPE, gate.pos, gate.stufe || undefined, gate.connective_tags, ); // TODO converter config
        }
        this.will_spawn_gates = [];

        for (const gate of this.will_remove_gates) {
            gate.destroy();
        }
        this.will_remove_gates = [];

        if (this.round_state !== PhenomenonRoundState.DESTROYED) {
            // block random command for 1 round
            if (Math.random() < 0.5) {
                
                const key = get_random_of(Object.keys(Command));
                const comm = Command[key as keyof typeof Command];
                logger.info(`Bizarrgebiet blocks ${comm} for 1 round`);
                
                game_board.block_command(comm, 1);
            } else {
                
                if (Math.random() < 0.5) {
                    // spawn 1 gate for 1 round
                    
                    const gate = game_board.spawn_gate();
                    if (!gate) {
                        logger.error("Bizarrgebiet could not spawn a gate");
                    } else {
                        logger.info(`Bizarrgebiet spawns ${gate.TYPE} for 1 round`);
                        this.will_remove_gates.push(gate);
                    }
                    
                } else {
                    // hide 1 gate for 1 round
                    const all_gates = game_board.all().filter(tile => Object.values(GateType).includes(tile.TYPE as any)) as Gate[];
                    
                    if (!all_gates.length) {
                        logger.error("Bizarrgebiet could not remove a gate");
                    } else {
                        const gate = get_random_of(all_gates);
                        gate.destroy();
                        this.will_spawn_gates.push(gate);

                        logger.info(`Bizarrgebiet removes ${gate.TYPE} for 1 round`);
                    }
                }
            }
            
        }
            
        super.after_round();
    }

    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, SpaceFissureType.SPACE_BIZARRGEBIET, stufe, connective_tags);
    }
}
