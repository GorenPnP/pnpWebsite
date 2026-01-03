abstract class Gate extends BlockTile {
    public readonly is_phenomenon: boolean = false;
    public readonly TYPE: GateType;

    constructor(pos: Position, type: GateType, connective_tags?: ConnectiveTag[]) {
        super(pos, connective_tags);
        this.TYPE = type;
        if (this.TYPE !== GateType.GATE_SWITCH) { this.set_image(determine_img_url(this.TYPE).url!); }
    }

    protected send_commands_to_all_outputs(commands: Command[]): TileInput[] | null {
        if (!commands?.length) { return null; }

        const new_inputs = commands.reduce((acc, command) => {
            const new_inputs = this.get_output_directions().map(dir => ({tile: this.get_neighbors([dir])[0]!, from_direction: reverse_direction([dir])[0]!, command}));
            return [...acc, ...new_inputs];
        }, [] as TileInput[]);

        return new_inputs.length ? new_inputs : null;
    }
}

class Mirror extends Gate {
    private blocked_command: Command | undefined;

    public incoming(...inputs: Input[]): TileInput[] | null {
        inputs = inputs.filter(input => this.has_input_at(input.from_direction))
        if (inputs.length !== 1) { return null; }

        this.blocked_command = inputs[0]!.command;
        return null;
    }
    public after_round() {
        if (this.blocked_command) {
            // block command for 3 turns
            logger.info(`BLOCK ${this.blocked_command} FOR 3 TURNS!!`);
            game_board.block_command(this.blocked_command, 3);

            this.destroy();
        }
    }
    
    constructor(pos: Position, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_MIRROR, connective_tags);
    }
}
class Inverter extends Gate {
    private static readonly conversion_map: {[command: string]: Command} = {
        "//drag": Command.DROP,
        "//drop": Command.DRAG,
        "//inject": Command.CRYSTALLIZE,
        "//crystallize": Command.INJECT,
        "//forward": Command.RETURN,
        "//return": Command.FORWARD, 
    }

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = inputs
            .filter(input => this.has_input_at(input.from_direction))
            .map(input => Inverter.conversion_map[input.command] || input.command);

        return this.send_commands_to_all_outputs(commands);
    }
    public after_round() { }

    constructor(pos: Position, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_INVERTER, connective_tags);
    }
}
class ButtonOn extends Gate implements Clickable {
    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = inputs
            .filter(input => this.has_input_at(input.from_direction))
            .map(input => input.command);

        return this.send_commands_to_all_outputs(commands);
    }
    public after_round() { }

    // toggle to "off" on click in user interface
    public click() {
        // this.destroy() is unnecessary here and only produces a flicker
        const button = game_board.createTile(GateType.GATE_BUTTON_OFF, this.pos) as ButtonOff;
        if (button) {
            button.is_blurred = this.is_blurred;
            button.draw();
        }
    }

    constructor(pos: Position, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_BUTTON_ON, connective_tags);
    }
}
class ButtonOff extends Gate implements Clickable {
    public incoming(..._: Input[]): TileInput[] | null {
        return null;
    }
    public after_round() { }

    // toggle to "on" on click in user interface
    public click() {
        // this.destroy() is unnecessary here and only produces a flicker
        const button = game_board.createTile(GateType.GATE_BUTTON_ON, this.pos) as ButtonOn;
        if (button) {
            button.is_blurred = this.is_blurred;
            button.draw();
        }
    }

    constructor(pos: Position, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_BUTTON_OFF, connective_tags);
    }
    
}
class Switch extends Gate implements Clickable {
    private active_direction!: Direction.T | Direction.L | Direction.R;

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = inputs
            .filter(input => this.has_input_at(input.from_direction))
            .map(input => input.command);

        const output_to = this.get_neighbors([this.active_direction])[0]!;
        const output_direction = reverse_direction([this.active_direction])[0]!;
        return commands.map(command => ({
            command,
            tile: output_to,
            from_direction: output_direction
        }));
    }
    public after_round() { }

    public click() {
        const outputs = this.get_output_directions();
        const index = outputs.indexOf(this.active_direction);
        this.set_active_direction(outputs[(index+1) % outputs.length]!);
    }

    constructor(pos: Position, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_SWITCH, connective_tags);

        if (!this.get_output_directions().length) {
            logger.error(`Switch an Position (${this.pos.x}, ${this.pos.y}) hat keinen Output! Der Switch muss in der Config unter seinen Outputs stehen.`);
        }

        this.set_active_direction(this.get_output_directions()[0]!);
    }

    private set_active_direction(direction: Direction.T | Direction.L | Direction.R) {
        this.active_direction = direction;

        switch (this.active_direction) {
            case Direction.T: this.set_image("/static/time_space/images/Switch oben.png"); break;
            case Direction.L: this.set_image("/static/time_space/images/Switch links.png"); break;
            case Direction.R: this.set_image("/static/time_space/images/Switch rechts.png"); break;
        }
        this.draw();
    }
}

namespace Converter {
    export interface ConverterConfig {
        from: Command,
        to: Command,
        bidirectional: boolean,
    }
}
class Converter extends Gate {
    private readonly conversion: {from: Command, to: Command}[];

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = inputs
            .filter(input => this.has_input_at(input.from_direction))
            .map(input => this.conversion.find(conv => conv.from === input.command)?.to || input.command);

        return this.send_commands_to_all_outputs(commands);
    }
    public after_round() { }

    constructor(pos: Position, converter_config?: Converter.ConverterConfig, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_CONVERTER, connective_tags);

        // if no converter_config set, randomize one
        if (!converter_config) {
            converter_config = {
                from: Command[get_random_of(Object.keys(Command)) as keyof typeof Command],
                to: Command[get_random_of(Object.keys(Command)) as keyof typeof Command],
                bidirectional: Math.random() < 0.5
            };
        }
        
        // set conversion
        this.conversion = [converter_config];
        if (converter_config.bidirectional) {
            this.conversion.push({from: converter_config.to, to: converter_config.from});
        }
    }
}
class Barrier extends Gate {
    private hits: number;

    public incoming(...inputs: Input[]): TileInput[] | null {
        if (inputs.some(input => this.get_input_directions().includes(input.from_direction as any))) {
            this.hits--;
        }
        return null;
    }
    public after_round() {
        if (this.hits <= 0) {
            this.destroy();
        }
    }

    constructor(pos: Position, hits?: number, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_BARRIER, connective_tags);

        this.hits = hits || Math.floor(Math.random() * 5) +1;   // if not set, randomize [1, 5]
    }
}
class NoMana extends Gate {
    private destroyed: boolean = false;

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = inputs
            .filter(input => this.get_input_directions().includes(input.from_direction as any))
            .map(input => input.command);

        if (commands.includes(Command.INJECT)) {
            this.destroyed = true;
        }
        return this.send_commands_to_all_outputs(commands.filter(comm => comm !== Command.INJECT))
    }
    public after_round() {
        if (this.destroyed) {
            this.destroy();
        }
    }

    constructor(pos: Position, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_NO_MANA, connective_tags);
    }
}
class ManaBomb extends Gate {
    private will_destroy: boolean = false;

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = inputs
            .filter(input => this.has_input_at(input.from_direction))
            .map(input => input.command);
        
        this.will_destroy = !!commands.length;

        return this.send_commands_to_all_outputs(commands);
    }
    public after_round() {
        if (this.will_destroy) {

            // destroy gate and related anomalies
            this.destroy();
            this.connective_tags
                .filter(conn => conn.type === ConnectiveType.MANABOMBE_A)
                .map(conn => game_board.tiles_by_tag(conn).find(tile => tile !== this))
                .forEach(anomaly => (anomaly as Anomaly).destroy());

            // get a random time fissure
            const time_fissures = game_board.all().filter(tile =>
                Object.values(TimeFissureType).includes(tile.TYPE as any) &&
                tile.TYPE !== TimeFissureType.TIME_SPLINTER
            ) as TimeFissure[];
        
            if (!time_fissures.length) {
                logger.error("Manabomb can't find a time fissure to promote to a Splinter");
                return;
            }

            // convert to splinter
            const time_fissure = get_random_of(time_fissures);
            game_board.remove_draw(time_fissure.pos);
            game_board.createTile(TimeFissureType.TIME_SPLINTER, time_fissure.pos, 1, time_fissure.connective_tags);
        }
    }

    constructor(pos: Position, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_MANA_BOMB, connective_tags);
    }
}
class Support extends Gate {
    private destroyed: boolean = false;

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = inputs
            .filter(input => this.get_input_directions().includes(input.from_direction as any))
            .map(input => input.command);

        if (!commands.length) { return null; }


        // spawn new Consumers?
        const new_consumers = commands.filter(comm => [Command.INJECT, Command.DROP].includes(comm)).length;
        if (new_consumers) {
            logger.info(`SPAWN ${new_consumers} NEW CONSUMER/S!`);

            Array.from({length: new_consumers}).forEach(_ =>
                game_board.spawn_phenomenon(PlaceholderType.ANOMALY, AnomalyType.ANOMALY_CONSUMER)
            );
        }

        this.destroyed = commands.some(comm => comm === Command.DRAG);
        return this.send_commands_to_all_outputs(commands.filter(comm => ![Command.INJECT, Command.DROP].includes(comm)));
    }
    public after_round() {
        if (this.destroyed) {
            this.destroy();
        }
    }

    constructor(pos: Position, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_SUPPORT, connective_tags);
    }
}
class Sensor extends Gate {
    private destroyed: boolean = false;

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = inputs
            .filter(input => this.get_input_directions().includes(input.from_direction as any))
            .map(input => input.command);

        if (!commands.length) { return null; }

        if (commands.includes(Command.DELETE)) {
            this.destroyed = true;
        }
        return this.send_commands_to_all_outputs(commands.filter(comm => comm !== Command.DELETE));
    }
    public after_round() {
        if (this.destroyed) {
            this.destroy();
        }
    }

    constructor(pos: Position, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_SENSOR, connective_tags);
    }
}
class Tracing extends Gate {
    private command_counter: number = 0;

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = inputs
            .filter(input => this.get_input_directions().includes(input.from_direction as any))
            .map(input => input.command);

        this.command_counter += commands.length;
        if (this.command_counter >= 5) {
            this.command_counter %= 5;
            logger.info("SPAWN KAPSELPHENOMEN!");

            game_board.spawn_phenomenon(PlaceholderType.SPACE_FISSURE, SpaceFissureType.SPACE_KAPSELPHÄNOMEN);
        }

        return this.send_commands_to_all_outputs(commands);
    }
    public after_round() { }

    constructor(pos: Position, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_TRACING, connective_tags);
    }
}

class TeleportIn extends Gate {
    private move_partner: TeleportOut | null = null;

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = inputs
            .filter(input => this.get_input_directions().includes(input.from_direction as any))
            .map(input => input.command);

        const teleport_connection = this.connective_tags.find(conn => conn.type = ConnectiveType.TELEPORT);
        if (!teleport_connection) {
            logger.error("teleport connection missing for TeleportIn");
            return null;
        }

        this.move_partner = game_board.tiles_by_tag(teleport_connection).find(tile => tile.TYPE === GateType.GATE_TELEPORT_OUT) as TeleportOut;

        return commands.map(command => ({
                command,
                tile: this.move_partner!,
                from_direction: null as any
            })
        );
    }
    public after_round() {
        if (this.move_partner) {
            const wire_pos = get_replaceable_wires();

            if (!wire_pos.length) {
                logger.error("No free space to relocate TeleportIn");
            } else {

                // move to a free spot
                this.destroy();
                const new_pos = get_random_of(wire_pos);
                game_board.remove_draw(new_pos);
                game_board.createTile(GateType.GATE_TELEPORT_IN, new_pos, undefined, this.connective_tags);
            }
        }
    }

    constructor(pos: Position, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_TELEPORT_IN, connective_tags);
    }
}
class TeleportOut extends Gate {
    private move: boolean = false;

    public incoming(...inputs: Input[]): TileInput[] | null {
        const commands = inputs
            .filter(input => input.from_direction === null)     // coming from a teleportIn
            .map(input => input.command);

        this.move = !!commands.length;
        return this.send_commands_to_all_outputs(commands);
    }
    public after_round() {
        if (this.move) {
            const wire_pos = get_replaceable_wires();

            if (!wire_pos.length) {
                logger.error("No free space to relocate TeleportOut");
            } else {

                // move to a free spot
                this.destroy();
                const new_pos = get_random_of(wire_pos);
                game_board.remove_draw(new_pos);
                game_board.createTile(GateType.GATE_TELEPORT_OUT, new_pos, undefined, this.connective_tags);
            }
        }
    }

    constructor(pos: Position, connective_tags?: ConnectiveTag[]) {
        super(pos, GateType.GATE_TELEPORT_OUT, connective_tags);
    }
}