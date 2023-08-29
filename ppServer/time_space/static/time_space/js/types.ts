enum WireType {
    WIRE_B_TO_T = "b to t",
    WIRE_B_TO_L = "b to l",
    WIRE_B_TO_R = "b to r",
    WIRE_B_TO_LR = "b to lr",
    WIRE_B_TO_TL = "b to tl",
    WIRE_B_TO_TR = "b to tr",
    WIRE_B_TO_TLR = "b to tlr",

    WIRE_L_TO_R = "l to r",
    WIRE_L_TO_T = "l to t",
    WIRE_L_TO_TR = "l to tr",

    WIRE_R_TO_L = "r to l",
    WIRE_R_TO_T = "r to t",
    WIRE_R_TO_TL = "r to tl",

    WIRE_DOUBLE_CROSS_TO_L = "cross to l",
    WIRE_DOUBLE_CROSS_TO_R = "cross to r",
    WIRE_DOUBLE_TO_TL = "double to tl",
    WIRE_DOUBLE_TO_TR = "double to tr",
};

enum GateType {
    GATE_MIRROR = "mirror",
    GATE_INVERTER = "inverter",
    GATE_BUTTON_ON = "button on",
    GATE_BUTTON_OFF = "button off",
    GATE_SWITCH = "switch",
    GATE_CONVERTER = "converter",
    GATE_BARRIER = "barrier",
    GATE_NO_MANA = "no mana",
    GATE_MANA_BOMB = "mana bomb",
    GATE_SUPPORT = "support",
    GATE_SENSOR = "sensor",
    GATE_TRACING = "tracing",

    GATE_TELEPORT_IN = "teleport in",
    GATE_TELEPORT_OUT = "teleport out",
};

enum TimeFissureType {    
    TIME_LINIENDELETION = "liniendeletion",
    TIME_LINEARRISS = "linearriss",
    TIME_SPLINTER = "splinter",
    TIME_DUPLIKATOR = "duplikator",
    TIME_LOOPER = "looper",
    TIME_TIMELAGGER = "timelagger",
    TIME_TIMEDELAYER = "timedelayer",
    TIME_RUNNER = "runner",
};

enum AnomalyType {    
    ANOMALY_CONSUMER = "consumer",
    ANOMALY_ERASER = "eraser",
    ANOMALY_BLURR = "blurr",
    ANOMALY_SHORT = "short",
    ANOMALY_TRACEBACK = "traceback",
};

enum SpaceFissureType {    
    SPACE_RAUMFISSUR = "raumfissur",
    SPACE_WURMLOCH = "wurmloch",
    SPACE_RAUMLOCH = "raumloch",
    SPACE_KAPSELPHÄNOMEN = "kapselphänomen",
    SPACE_BIZARRGEBIET = "bizarrgebiet",
};

enum PlaceholderType {
    GENERAL = "general placeholder",
    TIME_FISSURE = "time fissure placeholder",
    SPACE_FISSURE = "space fissure placeholder",
    ANOMALY = "anomaly placeholder"
}

type TileType = WireType | GateType | TimeFissureType | SpaceFissureType | AnomalyType | PlaceholderType;