abstract class TimeFissure extends BlockTile {
    public readonly is_phenomenon: boolean = true;
    public readonly TYPE: TimeFissureType;
    public stufe: number;

    // for liniendeletion-cover
    protected looks_like_liniendeletion: boolean = false;
    private readonly original_image_url: string;

    protected readonly messages: {
        wrong: string[],
        correct: string[],
        destroy: string[];
    };

    protected required_sequence: Command[];
    protected next_correct_command: number = 0;
    public round_state: PhenomenonRoundState = PhenomenonRoundState.NOT_HIT;

    constructor(
        pos: Position,
        type: TimeFissureType,
        required_sequence: Command[],
        messages: { wrong: string[], correct: string[], destroy: string[];},
        stufe: number = 1, connective_tags?: ConnectiveTag[]
    ) {
        super(pos, connective_tags);
        this.TYPE = type;
        this.required_sequence = required_sequence;
        this.messages = messages;
        this.stufe = stufe;

        this.original_image_url = determine_img_url(this.TYPE).url!;
        this.set_image(this.original_image_url)
    }

    public toggle_cover_as_liniendeletion() {
        game_board.remove_draw(this.pos);
        this.set_image(this.looks_like_liniendeletion ? this.original_image_url : "/src/images/Zeitriss schwarz.png");
        this.looks_like_liniendeletion = !this.looks_like_liniendeletion;
    }
    public get is_covered_as_liniendeletion() {
        return this.looks_like_liniendeletion;
    }


    /**
     * warning: resets this.round_state to PhenomenonRoundState.NOT_HIT
     */
    protected _log() {
        switch (this.round_state) {
            case PhenomenonRoundState.NOT_HIT: logger.register_round_answer(this); break;
            case PhenomenonRoundState.WRONG_COMMAND: this.stufe++; logger.register_round_answer(this, get_random_of(this.messages.wrong)); break;
            case PhenomenonRoundState.CORRECT_COMMAND: logger.register_round_answer(this, get_random_of(this.messages.correct)); break;
            case PhenomenonRoundState.DESTROYED: logger.register_round_answer(this, get_random_of(this.messages.destroy)); break;
        }

        this.round_state = PhenomenonRoundState.NOT_HIT;
    }

    /**
     * Collects all incoming Commands form correctly attached wires.
     * Checks for successful hits, increases this.next_correct_command-counter
     * and sets this.round_state to the appropriate PhenomenonRoundState (for
     * use in logging to game_board)
     * @param inputs (unfiltered, can be of incorrect origin)
     * @returns all FILTERED commands
     */
    protected _process_incoming_commands(inputs: Input[]): Command[] {
        const has_short = this.connective_tags
            .some(conn => conn.type === ConnectiveType.SHORT_TF && game_board.tiles_by_tag(conn).length >= 2);

        const commands = inputs
            .filter(input => this.has_input_at(input.from_direction))
            .map(input => input.command)
            .filter(conn => !has_short || this.required_sequence.includes(Command.NATURALIZE) || conn !== Command.NATURALIZE);

        if (commands.length === 0) {
            this.round_state = PhenomenonRoundState.NOT_HIT;
            return [];
        }
        this.round_state = PhenomenonRoundState.WRONG_COMMAND;

        while (
            this.required_sequence.length > this.next_correct_command &&            // not dead
            commands.includes(this.required_sequence[this.next_correct_command]!)   // correct command
        ) {
            this.next_correct_command++;
            this.round_state = PhenomenonRoundState.CORRECT_COMMAND;
        }
        if (this.round_state === PhenomenonRoundState.WRONG_COMMAND) {
            this.next_correct_command = 0;
        }

        if (this.required_sequence.length <= this.next_correct_command) {
            this.round_state = PhenomenonRoundState.DESTROYED;
        }

        return commands;
    }
}

class Liniendeletion extends TimeFissure {
    private will_cover: boolean = false;
    private covered_fissure: TimeFissure | null = null;

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = this._process_incoming_commands(inputs);

        this.will_cover = commands.length > 0 && Math.random() < 0.05;
        return null;
    }
    public after_round() {

        // setup
        const available_fissures: TimeFissure[] = game_board.all()
            .filter(fissure =>
                fissure instanceof TimeFissure &&
                ![TimeFissureType.TIME_LINIENDELETION, TimeFissureType.TIME_LINEARRISS].includes(fissure.TYPE)
            ) as TimeFissure[];

        // uncover if other fissure died or will cover new one
        if (this.covered_fissure && (this.will_cover || !available_fissures.includes(this.covered_fissure))) {
            this.covered_fissure?.toggle_cover_as_liniendeletion();
            this.covered_fissure = null;
            this.looks_like_liniendeletion = false;
        }

        if (this.will_cover) {
            this.will_cover = false;
            const fissures = available_fissures.filter(fissure => fissure !== this.covered_fissure);
            
            if (fissures.length) {

                // cover fissure as liniendeletion
                this.looks_like_liniendeletion = true;
                this.covered_fissure = get_random_of(fissures);
                this.covered_fissure.toggle_cover_as_liniendeletion();

                // switch places?
                if (Math.random() < 0.5) {
                    const pos = this.pos;
                    this.pos = this.covered_fissure.pos;
                    this.covered_fissure.pos = pos;

                    game_board.set(this.pos.x, this.pos.y, this);
                    game_board.set(this.covered_fissure.pos.x, this.covered_fissure.pos.y, this.covered_fissure);
                }
                    
                // draw
                game_board.remove_draw(this.pos);
                this.draw();
                game_board.remove_draw(this.covered_fissure.pos);
                this.covered_fissure.draw();
            }
        }

        // destroy
        if (this.round_state === PhenomenonRoundState.DESTROYED) {
            this.covered_fissure?.toggle_cover_as_liniendeletion();
            this.covered_fissure = null;
            this.destroy();
        }

        // log
        this._log();
    }

    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(
            pos, TimeFissureType.TIME_LINIENDELETION,
            [Command.ANALYZE, Command.DRAG, Command.DROP, Command.NATURALIZE],
            {
                wrong: [
                    "Target not found.", "No event existing.", "There is nothing.", "We are wasting energy.", "No.", "Time is a state of mind.",
                    "Reach out.", "Unidentified object found", "Restarting ...", "Program not ready.", "Initializing ...", "Please restart.",
                    "Converting splinter.", "What am I?"
                ],
                correct: [
                    "Target not found.", "No event existing.", "There is nothing.", "We are wasting energy.", "No.", "Time is a state of mind.",
                    "Reach out.", "Unidentified object found", "Restarting ...", "Program not ready.", "Initializing ...", "Please restart.",
                    "Converting splinter.", "What am I?"
                ],
                destroy: [
                    "Target not found.", "No event existing.", "There is nothing.", "We are wasting energy.", "No.", "Time is a state of mind.",
                    "Reach out.", "Unidentified object found", "Restarting ...", "Program not ready.", "Initializing ...", "Please restart.",
                    "Converting splinter.", "What am I?"
                ]
            },
            stufe, connective_tags
        );
    }
}
class Linearriss extends TimeFissure {
    private num_commands_seen = 0;
    private turns_to_splinter: boolean = false;
    public splits: number;

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = this._process_incoming_commands(inputs);

        // grows into splinter?
        this.num_commands_seen += commands.length;
        if (this.num_commands_seen >= 3) {
            this.num_commands_seen %= 3;
            this.stufe++;
            this.turns_to_splinter = Math.random() < 0.25;
        }

        return null;
    }
    public after_round() {

        // destroy
        if (this.round_state === PhenomenonRoundState.DESTROYED) {
            this.destroy();
        } else {
            
            // transform into splinter?
            if (this.turns_to_splinter) {
                logger.info(this, " grows into splinter!");
                
                this.destroy();
                const splinter = game_board.createTile(TimeFissureType.TIME_SPLINTER, this.pos, 1, this.connective_tags) as Splinter;
                splinter.linearriss = this;
            }
        }

        // log
        this._log();
        this.stufe--;
    }
    
    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[], splits: number = 0) {
        super(
            pos, TimeFissureType.TIME_LINEARRISS,
            [Command.RETURN, Command.CRYSTALLIZE, Command.NORMALIZE],
            {
                wrong: ["Growth accelerated. Manainput stabilized. Increasing size for further division."],
                correct: ["Growth accelerated. Manainput stabilized. Increasing size for further division."],
                destroy: ["Growth has been corrupted. Stabilization failed."],
            },
            stufe, connective_tags
        );
        this.splits = splits;
    }
}
class Splinter extends TimeFissure {
    private divide_now: boolean = false;
    public linearriss!: Linearriss | null;

    public incoming(...inputs: Input[]): TileInput[] | null {
        if (this._process_incoming_commands(inputs).length) {
            // Divide into multiple?
            this.divide_now = Math.random() < 0.33;
        }

        return null;
    }

    protected _log() {
        if (this.round_state === PhenomenonRoundState.NOT_HIT) { return logger.register_round_answer(this); }

        // increment stufe on command
        this.stufe++;

        // log
        const text_length = 3+ Math.floor(Math.random() * 48);
        logger.register_round_answer(this, get_random_string(text_length));

        this.round_state = PhenomenonRoundState.NOT_HIT;
    }

    public after_round() {

        // Divide into multiple?
        if (this.divide_now) {
            this.destroy();

            // set to linearriss
            const stufe = this.linearriss ? this.linearriss.stufe : 1;
            const linearriss: Linearriss = game_board.createTile(TimeFissureType.TIME_LINEARRISS, this.pos, stufe, this.connective_tags) as any;
            linearriss.splits = (this.linearriss?.splits || 0) + 1;

            // add other Fissures

            // get number of new ones
            const number_limits = [0.45, 0.25, 0.15, 0.1, 0.05];    // possibilities for 1 - 5 additional fissures
            let amount: number = 0;
            let rand = Math.random();
            do { rand -= number_limits[amount++]!; }
            while (rand >= 0);

            // spawn other <amount> Zeitrisse but not splinter, liniendeletion or linearriss
            const possible_fissures: TimeFissureType[] = [
                TimeFissureType.TIME_DUPLIKATOR,
                TimeFissureType.TIME_LOOPER,
                TimeFissureType.TIME_TIMELAGGER,
                TimeFissureType.TIME_TIMEDELAYER,
                TimeFissureType.TIME_RUNNER
            ];
            Array.from({length: amount})
                .map(() => get_random_of(possible_fissures))
                .forEach(type => game_board.spawn_phenomenon(PlaceholderType.TIME_FISSURE, type));

            logger.info(`Splinter divides into Linearriss + ${amount} other/s!`);
        }

        this._log();
    }
    
    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, TimeFissureType.TIME_SPLINTER, [], { wrong: [], correct: [], destroy: []}, stufe, connective_tags);
    }
}
class Duplikator extends TimeFissure {

    public incoming(...inputs: Input[]): TileInput[] | null {
        this._process_incoming_commands(inputs);
        return null;
    }

    protected _log() {
        switch (this.round_state) {
            case PhenomenonRoundState.NOT_HIT: logger.register_round_answer(this); break;
            case PhenomenonRoundState.WRONG_COMMAND: this.stufe++; logger.register_round_answer(this, get_random_of(this.messages.wrong), get_random_of(this.messages.wrong)); break;
            case PhenomenonRoundState.CORRECT_COMMAND: logger.register_round_answer(this, get_random_of(this.messages.correct), get_random_of(this.messages.correct)); break;
            case PhenomenonRoundState.DESTROYED: logger.register_round_answer(this, get_random_of(this.messages.destroy), get_random_of(this.messages.destroy)); break;
        }

        this.round_state = PhenomenonRoundState.NOT_HIT;
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
        super(
            pos, TimeFissureType.TIME_DUPLIKATOR,
            [Command.CRYSTALLIZE, Command.NORMALIZE, Command.RETURN],
            {
                wrong: ["Mana has been detected", "More mana is needed", "Gathering more mana"],
                correct: ["Input has been blocked", "Currently no power input", "A critical error occurred"],
                destroy: ["Maintaining manaflow failed", "Stabilization failed", "Dew point too high"],
            },
            stufe, connective_tags
        );
    }
}
class Looper extends TimeFissure {
    private logged_messages: string[] = [];

    public incoming(...inputs: Input[]): TileInput[] | null {
        this._process_incoming_commands(inputs);

        return null;
    }

    protected _log() {
        if (this.round_state === PhenomenonRoundState.NOT_HIT) { return logger.register_round_answer(this); }
        
        switch (this.round_state) {
            case PhenomenonRoundState.WRONG_COMMAND: this.stufe++; this.logged_messages.push(get_random_of(this.messages.wrong)); break;
            case PhenomenonRoundState.CORRECT_COMMAND: this.logged_messages.push(get_random_of(this.messages.correct)); break;
            case PhenomenonRoundState.DESTROYED: this.logged_messages.push(get_random_of(this.messages.destroy)); break;
        }
        logger.register_round_answer(this, ...this.logged_messages);

        this.round_state = PhenomenonRoundState.NOT_HIT;
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
        super(pos, TimeFissureType.TIME_LOOPER, [
                Command.ANALYZE,
                Command.DRAG,
                Command.DELETE,
                Command.NATURALIZE,
            ],
            {
                wrong: ["Mana in a spiral", "Circulating more energy", "Power ramped up"],
                correct: ["Dizzyness", "Eastward it goes", "Getting down"],
                destroy: ["Mana falling down", "Leaving the circle", "Outer space"],
            },
            stufe, connective_tags
        );
    }
}
class Timelagger extends TimeFissure {
    public incoming(...inputs: Input[]): TileInput[] | null {
        this._process_incoming_commands(inputs);

        return null;
    }
    public after_round() {

        if (this.round_state === PhenomenonRoundState.DESTROYED) {
            return this.destroy();  // no answer on destruction
        }

        this._log();
    }

    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, TimeFissureType.TIME_TIMELAGGER, [
                Command.ANALYZE,
                Command.DRAG,
                Command.DROP,
                Command.NORMALIZE
            ], {
                wrong: [""],
                correct: ["it says", "I guess", "maybe", "it shouldn't be", "I assume"],
                destroy: [],
            },
            stufe, connective_tags
        );
    }
}
class Timedelayer extends TimeFissure {
    private prev_message: string = "";
    private destroy_next_round: boolean = false;

    public incoming(...inputs: Input[]): TileInput[] | null {
        // is practically dead?
        if (this.destroy_next_round) { return null; }

        this._process_incoming_commands(inputs);
        return null;
    }

    protected _log() {
        if (this.round_state === PhenomenonRoundState.NOT_HIT) { return; }
        
        this.prev_message ? logger.register_round_answer(this, this.prev_message) : logger.register_round_answer(this);
        switch (this.round_state) {
            case PhenomenonRoundState.WRONG_COMMAND: this.stufe++; this.prev_message = get_random_of(this.messages.wrong); break;
            case PhenomenonRoundState.CORRECT_COMMAND: this.prev_message = get_random_of(this.messages.correct); break;
            case PhenomenonRoundState.DESTROYED: this.prev_message = get_random_of(this.messages.destroy); break;
        }

        this.round_state = PhenomenonRoundState.NOT_HIT;
    }
    public after_round() {

        // do destroy
        if (this.destroy_next_round) { this.destroy(); }
            
        // destroy next round
        if (this.round_state === PhenomenonRoundState.DESTROYED) {
            this.destroy_next_round = true;
        }

        // log
        this._log();
    }

    constructor(pos: Position, stufe?: number, connective_tags?: ConnectiveTag[]) {
        super(
            pos, TimeFissureType.TIME_TIMEDELAYER,
            [Command.FORWARD, Command.INJECT, Command.NORMALIZE],
            {
                wrong: ["No", "Wrong", "Incorrect", "Yesn't", "Don't", "Is not"],
                correct: ["Yes", "Right", "Hurt", "Wow", "Betrayal", "Unfair"],
                destroy: ["Murderer", "Killer", "No time for that", "Out of existance"],
            },
            stufe, connective_tags
        );
    }
}
class Runner extends TimeFissure {

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
        super(
            pos, TimeFissureType.TIME_RUNNER,
            [Command.CRYSTALLIZE, Command.RETURN, Command.NORMALIZE],
            {
                wrong: ["Yes", "More power", "POW", "Module established", "More mana is needed"],
                correct: ["Mana has been blocked", "A critical error occurred", "Target not found", "Run"],
                destroy: ["Stormy", "Awaiting input", "Stopped running", "I stopped working"],
            },
            stufe, connective_tags
        )
    }
}