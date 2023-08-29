abstract class Anomaly extends BlockTile {
    public readonly is_phenomenon: boolean = true;
    public readonly TYPE: AnomalyType;
    public stufe: number;

    protected required_command: Command;
    public round_state: PhenomenonRoundState = PhenomenonRoundState.NOT_HIT;

    constructor(pos: Position, type: AnomalyType, required_command: Command, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, connective_tags);
        this.TYPE = type;
        this.required_command = required_command;
        this.stufe = stufe || 1;
        this.set_image(determine_img_url(this.TYPE).url!);
    }

    /**
     * warning: resets this.round_state to PhenomenonRoundState.NOT_HIT
     */
    protected _log() {
        switch (this.round_state) {
            case PhenomenonRoundState.NOT_HIT: logger.register_round_answer(this); break;
            case PhenomenonRoundState.WRONG_COMMAND: logger.register_round_answer(this, "Health restored!"); break;
            case PhenomenonRoundState.CORRECT_COMMAND: logger.register_round_answer(this, "Accepted!"); break;
            case PhenomenonRoundState.DESTROYED: logger.register_round_answer(this, "Done!"); break;
        }

        this.round_state = PhenomenonRoundState.NOT_HIT;
    }
    
    /**
     * Collects all incoming Commands form correctly attached wires.
     * Checks for successful hits, decreases this.stufe
     * and sets this.round_state to the appropriate PhenomenonRoundState (for
     * use in logging to game_board)
     * @param inputs (unfiltered, can be of incorrect origin)
     * @returns all FILTERED commands
     */
    protected _process_incoming_commands(inputs: Input[]): Command[] {
        const commands = inputs
            .filter(input => this.has_input_at(input.from_direction))
            .map(input => input.command);

        if (commands.length === 0) {
            this.round_state = PhenomenonRoundState.NOT_HIT;
            return [];
        }

        const correct_commands = commands.filter(comm => comm === this.required_command).length;
        this.stufe -= correct_commands;
        this.round_state = correct_commands ? PhenomenonRoundState.CORRECT_COMMAND : PhenomenonRoundState.WRONG_COMMAND;

        if (this.stufe <= 0) {
            this.round_state = PhenomenonRoundState.DESTROYED;
        }

        return commands;
    }
}


class Consumer extends Anomaly {

    public incoming(...inputs: Input[]): TileInput[] | null {
        this._process_incoming_commands(inputs);

        return null;
    }
    public after_round() {
        // grow?
        if (this.round_state !== PhenomenonRoundState.NOT_HIT && Math.random() < 0.33) {
            this.stufe!++;
            logger.info(this, "growing to stufe", this.stufe);

            if (this.stufe! > 0 && this.round_state === PhenomenonRoundState.DESTROYED) {
                this.round_state = PhenomenonRoundState.CORRECT_COMMAND;
            }
        }

        // destroy
        if (this.round_state === PhenomenonRoundState.DESTROYED) { this.destroy(); }

        // collapse into linearriss
        if (this.stufe! >= 5) {
            logger.info(this, "Consumer collapses into Linearriss");

            this.destroy();
            game_board.createTile(TimeFissureType.TIME_LINEARRISS, this.pos);
            return;
        }

        // log
        this._log();
    }

    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, AnomalyType.ANOMALY_CONSUMER, Command.INJECT, stufe, connective_tags);
    }
}
class Eraser extends Anomaly {

    public incoming(...inputs: Input[]): TileInput[] | null {
        this._process_incoming_commands(inputs);

        return null;
    }
    public after_round() {
        if (this.round_state === PhenomenonRoundState.DESTROYED) { this.destroy(); }

        this._log();
    }

    constructor(pos:Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, AnomalyType.ANOMALY_ERASER, Command.CRYSTALLIZE, stufe, connective_tags);
    }
}
class Blurr extends Anomaly {

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = this._process_incoming_commands(inputs);
        this.stufe! += commands.filter(comm => [Command.INJECT, Command.DROP, Command.CRYSTALLIZE].includes(comm)).length;

        if (this.round_state === PhenomenonRoundState.DESTROYED && this.stufe! > 0) {
            this.round_state = PhenomenonRoundState.CORRECT_COMMAND;
        }

        return null;
    }
    public after_round() {
        if (this.round_state === PhenomenonRoundState.DESTROYED) { this.destroy(); }

        this._log();

        for (let times = 0; times < this.stufe!; times++) {
            if (Math.random() >= 0.01) { continue; }

            // blur 1 random BlockTile
            logger.info("BLUR RANDOM BLOCK-TILE");
            const block_tiles = game_board.all().filter(tile => !Object.values(WireType).includes(tile.TYPE as any) && !blockTile.is_blurred) as BlockTile[];

            if (!block_tiles.length) {
                logger.error("Nothing to blurr");
                return;
            }

            const blockTile = get_random_of(block_tiles);
            blockTile.is_blurred = true;
            blockTile.draw();
        }
    }

    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, AnomalyType.ANOMALY_BLURR, Command.DRAG, stufe, connective_tags);
    }
}
class Short extends Anomaly {

    public incoming(...inputs: Input[]): TileInput[] | null {
        this._process_incoming_commands(inputs);

        return null;
    }
    public after_round() {

        if (this.round_state === PhenomenonRoundState.DESTROYED) { this.destroy(); }

        else {

            // steal stufe?
            if (Math.random() < 0.05) {
                const other_phenomena = game_board.all().filter(tile => tile.is_phenomenon && tile.stufe && tile.stufe > 1 && tile !== this);
                const phenomenon = get_random_of(other_phenomena);
                if (phenomenon) {
                    logger.info(`Short steals 1 Stufe of ${phenomenon.TYPE} at (${phenomenon.pos.x}, ${phenomenon.pos.y})`)

                    this.stufe++;
                    phenomenon.stufe!--;
                }
            }

            // collapse?
            if (this.stufe! >= 10) {
                this.destroy();
    
                logger.info(this, "collapses into Splinter and Raumfissur");
    
                game_board.createTile(TimeFissureType.TIME_SPLINTER, this.pos);
                game_board.spawn_phenomenon(PlaceholderType.SPACE_FISSURE, SpaceFissureType.SPACE_RAUMFISSUR);
            }
        }


        this._log();
    }

    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, AnomalyType.ANOMALY_SHORT, Command.NATURALIZE, stufe, connective_tags);
    }
}
class Traceback extends Anomaly {

    public incoming(...inputs: Input[]): TileInput[] | null {
        this._process_incoming_commands(inputs);

        return null;
    }
    public after_round() {

        // destroy
        if (this.round_state === PhenomenonRoundState.DESTROYED) {
            this.destroy();
        }

        // log
        this._log();
    }

    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, AnomalyType.ANOMALY_TRACEBACK, Command.CRYSTALLIZE, stufe, connective_tags);
    }
}
