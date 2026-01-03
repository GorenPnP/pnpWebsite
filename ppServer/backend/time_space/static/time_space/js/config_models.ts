interface GameConfig {
    id?: number,
    name: string,
    width: number,
    height: number,
    tiles: TileConfig[],
};

interface TileConfig {
    pos: Position,
    type: TileType,
    connective_tags?: ConnectiveTag[],
    stufe?: number,
    converter_config?: Converter.ConverterConfig,
};

interface ConnectiveTag {
    type: ConnectiveType,
    id: string,
};

enum ConnectiveType {
    SHORT_TF="Short TF",
    MANABOMBE_A="Manabombe A",
    TELEPORT="Teleport",
    TRACE_WURM="Traceback Wurmloch",
};