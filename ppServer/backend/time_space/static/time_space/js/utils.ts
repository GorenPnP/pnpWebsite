/** tile width and height in px */
const TILE_SIZE = 64;
let GRID_WIDTH: number;
let GRID_HEIGHT: number;

const LINE_WIDTH = 1.0;
const BACKGROUND_COLOR = "white";
const GRID_COLOR = "#ddd";

const SPEECH_ENABLED = true;
const DEBUG = false;

const canvas: HTMLCanvasElement = document.querySelector("#grid")!;
const ctx: CanvasRenderingContext2D = canvas.getContext("2d")!;

enum Direction {
    L = "left",
    R = "right",
    T = "top",
    B = "bottom",
}

enum InquiryCommand {
    INIT = "/init",
    STUFE = "/s",       // < 4 | = 2 | ...
    TYPE = "/type",     // RR | ZR | ZA
    RESPONSE = "/response", // #1 | #7 | ...
    SPLITS = "/splits",     // #1 | #7 | ...
    SPLITN = "/splitn",     // #1 | #7 | ...
    HELP = "/help",
    HELP1 = "/help1",
    HELP2 = "/help2",
}
enum Command {
    ANALYZE = "//analyze",
    CRYSTALLIZE = "//crystallize",
    DELETE = "//delete",
    DRAG = "//drag",
    DROP = "//drop",
    FORWARD = "//forward",
    INJECT = "//inject",
    NATURALIZE = "//naturalize",
    NORMALIZE = "//normalize",
    RETURN = "//return",
    SKIP = "//skip",

    BDV = "//bdv",
    MDV = "//mdv",
    MDBV = "//mdbv"
}

enum PhenomenonRoundState {
    NOT_HIT = "not hit",
    WRONG_COMMAND = "wrong command",
    CORRECT_COMMAND = "correct command",
    DESTROYED = "destroyed",
};

interface Input {
    from_direction: Direction,
    command: Command,
}
interface TileInput extends Input {
    tile: Tile,
}

interface Position {
    x: number,
    y: number
}


function get_random_of<T>(msgs: T[]): T {
    const index = Math.floor(Math.random() * msgs.length);
    return msgs[index]!;
};

function reverse_direction(dirs: Direction[]): Direction[] {
    return dirs.map(d => {
        switch(d) {
            case Direction.L: return Direction.R;
            case Direction.R: return Direction.L;
            case Direction.T: return Direction.B;
            case Direction.B: return Direction.T;
        }
    })
}

function get_wire(inputs: (Direction.B | Direction.L | Direction.R)[], outputs: ( Direction.T | Direction.L | Direction.R )[]): WireType | null {
    // remove duplicates
    inputs = [...new Set(inputs)];
    outputs = [...new Set(outputs)];

    if (inputs.length === 0 || outputs.length === 0) { return null; }
    
    if (inputs.length > 1) {
        if (inputs.includes(Direction.L)) { return WireType.WIRE_DOUBLE_TO_TR; }
        return WireType.WIRE_DOUBLE_TO_TL;
    }

    // From bottom to ...
    if (inputs[0] === Direction.B) {
        if (outputs.length === 1) {
            switch (outputs[0]) {
                case Direction.T: return WireType.WIRE_B_TO_T;
                case Direction.L: return WireType.WIRE_B_TO_L;
                case Direction.R: return WireType.WIRE_B_TO_R;
            }
        }
        if (outputs.length === 3) { return WireType.WIRE_B_TO_TLR; }
        if (!outputs.includes(Direction.T)) { return WireType.WIRE_B_TO_LR; }
        if (outputs.includes(Direction.L)) { return WireType.WIRE_B_TO_TL; }
        return WireType.WIRE_B_TO_TR;
    }

    // from left to ...
    if (inputs[0] === Direction.L) {
        if (outputs.length === 2) { return WireType.WIRE_L_TO_TR; }
        if (outputs[0] === Direction.T) { return WireType.WIRE_L_TO_T; }
        return WireType.WIRE_L_TO_R;
    }
    
    // from right to ...
    if (outputs.length === 2) { return WireType.WIRE_R_TO_TL; }
    if (outputs[0] === Direction.T) { return WireType.WIRE_R_TO_T; }
    return WireType.WIRE_R_TO_L;
}


function get_random_string(length: number = 32) {
    var s = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    return Array(length).join().split(',').map(function() { return s.charAt(Math.floor(Math.random() * s.length)); }).join('');
}

function determine_img_url(type: TileType): {url: string | null, color: string} {
    switch(type) {

        // wires
        case WireType.WIRE_B_TO_T: return {url: "/static/time_space/images/Tile 2.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_B_TO_L: return {url: "/static/time_space/images/Tile 4.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_B_TO_R: return {url: "/static/time_space/images/Tile 3.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_B_TO_LR: return {url: "/static/time_space/images/Tile 5.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_B_TO_TL: return {url: "/static/time_space/images/Tile 6.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_B_TO_TR: return {url: "/static/time_space/images/Tile 7.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_B_TO_TLR: return {url: "/static/time_space/images/Tile 1.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_L_TO_R: return {url: "/static/time_space/images/Tile 9.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_L_TO_T: return {url: "/static/time_space/images/Tile 11.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_L_TO_TR: return {url: "/static/time_space/images/Tile 12.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_R_TO_L: return {url: "/static/time_space/images/Tile 8.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_R_TO_T: return {url: "/static/time_space/images/Tile 10.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_R_TO_TL: return {url: "/static/time_space/images/Tile 13.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_DOUBLE_CROSS_TO_L: return {url: "/static/time_space/images/Tile 15.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_DOUBLE_CROSS_TO_R: return {url: "/static/time_space/images/Tile 14.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_DOUBLE_TO_TL: return {url: "/static/time_space/images/Tile 17.png", color: BACKGROUND_COLOR};
        case WireType.WIRE_DOUBLE_TO_TR: return {url: "/static/time_space/images/Tile 16.png", color: BACKGROUND_COLOR};

        // gates
        case GateType.GATE_MIRROR: return {url: "/static/time_space/images/Mirror.png", color: BACKGROUND_COLOR};
        case GateType.GATE_INVERTER: return {url: "/static/time_space/images/Inverter.png", color: BACKGROUND_COLOR};
        case GateType.GATE_BUTTON_ON: return {url: "/static/time_space/images/Aktivator.png", color: BACKGROUND_COLOR};
        case GateType.GATE_BUTTON_OFF: return {url: "/static/time_space/images/Desaktivator.png", color: BACKGROUND_COLOR};
        case GateType.GATE_SWITCH: return {url: "/static/time_space/images/Switch oben.png", color: BACKGROUND_COLOR};
        case GateType.GATE_CONVERTER: return {url: "/static/time_space/images/Konverter.png", color: BACKGROUND_COLOR};
        case GateType.GATE_BARRIER: return {url: "/static/time_space/images/Barriere.png", color: BACKGROUND_COLOR};
        case GateType.GATE_NO_MANA: return {url: "/static/time_space/images/Manadegenerator.png", color: BACKGROUND_COLOR};
        case GateType.GATE_MANA_BOMB: return {url: "/static/time_space/images/Manabombe.png", color: BACKGROUND_COLOR};
        case GateType.GATE_SUPPORT: return {url: "/static/time_space/images/Support.png", color: BACKGROUND_COLOR};
        case GateType.GATE_SENSOR: return {url: "/static/time_space/images/Sensor.png", color: BACKGROUND_COLOR};
        case GateType.GATE_TRACING: return {url: "/static/time_space/images/Tracing.png", color: BACKGROUND_COLOR};
        case GateType.GATE_TELEPORT_IN: return {url: "/static/time_space/images/Teleport Input.png", color: BACKGROUND_COLOR};
        case GateType.GATE_TELEPORT_OUT: return {url: "/static/time_space/images/Teleport Output.png", color: BACKGROUND_COLOR};

        // time fissure
        case TimeFissureType.TIME_LINIENDELETION: return {url: "/static/time_space/images/Zeitriss schwarz.png", color: BACKGROUND_COLOR};
        case TimeFissureType.TIME_SPLINTER: return {url: "/static/time_space/images/Zeitriss rot.png", color: BACKGROUND_COLOR};
        case TimeFissureType.TIME_TIMELAGGER: return {url: "/static/time_space/images/Zeitriss farblos.png", color: BACKGROUND_COLOR};
        case TimeFissureType.TIME_LINEARRISS:
        case TimeFissureType.TIME_DUPLIKATOR:
        case TimeFissureType.TIME_LOOPER:
        case TimeFissureType.TIME_TIMEDELAYER:
        case TimeFissureType.TIME_RUNNER:
            return {url: "/static/time_space/images/Zeitriss blau.png", color: BACKGROUND_COLOR};

        // anomalies
        case AnomalyType.ANOMALY_CONSUMER:
        case AnomalyType.ANOMALY_ERASER:
        case AnomalyType.ANOMALY_BLURR:
        case AnomalyType.ANOMALY_SHORT:
        case AnomalyType.ANOMALY_TRACEBACK:
            return {url: "/static/time_space/images/Zeitanomalie.png", color: BACKGROUND_COLOR};

        // space fissure
        case SpaceFissureType.SPACE_RAUMFISSUR:
        case SpaceFissureType.SPACE_WURMLOCH:
        case SpaceFissureType.SPACE_RAUMLOCH:
        case SpaceFissureType.SPACE_KAPSELPHÄNOMEN:
        case SpaceFissureType.SPACE_BIZARRGEBIET:
            return {url: "/static/time_space/images/Raumriss.png", color: BACKGROUND_COLOR};

        // placeholders
        case PlaceholderType.GENERAL: return {url: null, color: "grey"};
        case PlaceholderType.TIME_FISSURE: return {url: null, color: "blue"};
        case PlaceholderType.SPACE_FISSURE: return {url: null, color: "yellow"};
        case PlaceholderType.ANOMALY: return {url: null, color: "violet"};
    }
}