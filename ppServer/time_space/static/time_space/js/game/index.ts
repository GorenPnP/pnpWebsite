// init canvas
GRID_WIDTH = parseInt(document.querySelector("#width")!.innerHTML);
GRID_HEIGHT = parseInt(document.querySelector("#height")!.innerHTML);
canvas.setAttribute("width", `${GRID_WIDTH * TILE_SIZE}px`);
canvas.setAttribute("height", `${GRID_HEIGHT * TILE_SIZE}px`);
ctx.lineWidth = LINE_WIDTH;

// init canvas container
const canvas_container: HTMLDivElement = document.querySelector(".canvas-container")!;
canvas_container.style.width = `${GRID_WIDTH * TILE_SIZE}px`;
canvas_container.style.height = `${GRID_HEIGHT * TILE_SIZE}px`;
canvas_container.style.setProperty("--tile-size", `${TILE_SIZE}px`);


// init logic stuff
const logger = new Logger();
const game_tiles: TileConfig[] = JSON.parse(document.querySelector("#game")!.innerHTML);
const game_board = new GameBoard();




/****** mouse callbacks *******/

// change cursor when hovering over clickable tile
canvas_container.onmousemove = function ({x, y}) {
    const {x: offsetX, y: offsetY} = canvas_container.getBoundingClientRect();
    x = Math.floor((x-offsetX) / TILE_SIZE);
    y = Math.floor((y-offsetY) / TILE_SIZE);
    const tile = game_board.get(x, y);

    canvas.style.cursor = tile && isClickable(tile) ? "pointer" : "auto";
};

// click clickable tiles
canvas_container.onclick = function ({x, y}) {
    const {x: offsetX, y: offsetY} = canvas_container.getBoundingClientRect();
    x = Math.floor((x-offsetX) / TILE_SIZE);
    y = Math.floor((y-offsetY) / TILE_SIZE);
    const tile = game_board.get(x, y);

    if (tile && isClickable(tile)) { tile.click(); }
};


// load game
let game_started: boolean = false;
let input_blocked: boolean = false;
function init() {
    if (game_started) { return; }
    game_started = true;

    game_board.draw_empty_grid();

    for (const tile of game_tiles) {
        game_board.createTile(tile.type, tile.pos, tile.stufe, tile.connective_tags, tile.converter_config);
    }
}



function run_round(event: KeyboardEvent, command: string) {
    if (event.key !== "Enter" || input_blocked) { return; }

    // execute command
    if (game_started && Object.values(Command).includes(command as any)) {
        logger.info(command);
        const comm = command as any as Command;
        
        if (game_board.is_command_blocked(comm)) {
            logger.error(`${comm} ist blockiert!`);
            logger.log("----");
            return;
        }
        
        input_blocked = true;
        execute_command(comm).then(_ => input_blocked = false);
        return;
    }

    // execute inquiry command
    if (Object.values(InquiryCommand).some(icomm => command.startsWith(icomm))) {

        const comm =
            Object.values(InquiryCommand).find(icomm => command === icomm) ||           // prefer equality
            Object.values(InquiryCommand)                                               // use .startswith as fallback & have string-details
                .filter(icomm => command.startsWith(icomm))
                .sort((a, b) => b.length - a.length)[0]!;
    
        const details = command.replace(comm, "").trim();

        if (comm === InquiryCommand.INIT) { return init(); }
        if (game_started || command.startsWith("/help")) {
            logger.info(comm, details || " ");

            input_blocked = true;
            return new InquiryLogger().run(comm, details.trim()).then(_ => {
                logger.log("----");
                input_blocked = false;    
            });
        }
    }

    // command not found
    logger.error("incorrect input");
    logger.log("----");
}


async function execute_command(command: Command) {

    // start logic
    if (command !== Command.SKIP) {
        _run_command(command);
    }

    // handle (some) connections
    handle_Short_TF_connections();
    handle_Traceback_Wurmloch_connections();
    handle_liniendeletion_linearriss();     // needs to be after Short - TF to be able to switch the connection in there

    // let every tile do their thing AFTER ROUND
    game_board.all().forEach(tile => tile.after_round());

    await game_board.after_round();

    // mark replaceable gates
    if (DEBUG) {

        // unmark all
        ctx.beginPath();
        ctx.fillStyle = BACKGROUND_COLOR;
        game_board.all().filter(tile => Object.values(WireType).includes(tile.TYPE as any))
            .forEach(({pos}) => ctx.fillRect(pos.x*TILE_SIZE, pos.y*TILE_SIZE, 5, 5))
        ctx.closePath();

        // mark all replaceables
        ctx.beginPath();
        ctx.fillStyle = "red";
        get_replaceable_wires().forEach(pos => ctx.fillRect(pos.x*TILE_SIZE, pos.y*TILE_SIZE, 5, 5))
        ctx.closePath();
    }
}

/**
 * let command pass through the game_board
 * @param command 
 */
function _run_command(command: Command) {
    let y = GRID_HEIGHT - 1;
    const phenomena = [];
    let input_to_tiles = game_board.all()
        .filter(tile => tile.pos.y === y)
        .map(tile => ({command, tile, from_direction: Direction.B})) as TileInput[];

    while (y >= 0 && input_to_tiles.length) {

        // get layer
        let next_layer: TileInput[] = [];

        // run layer
        while (input_to_tiles.length) {
            let temporary: TileInput[] = input_to_tiles
                .map(input => input.tile.incoming(input))
                .filter(new_inputs => new_inputs)
                .reduce((all, input) => [...all!, ...input!], [] as TileInput[]) as any;
        
            input_to_tiles = temporary.filter(tile_input => tile_input.tile.pos.y >= y && !tile_input.tile.is_phenomenon);
            next_layer.push(...temporary.filter(tile_input => tile_input.tile.pos.y < y && !tile_input.tile.is_phenomenon));
            phenomena.push(...temporary.filter(tile_input => tile_input.tile.is_phenomenon));
        }

        // prepare next layer
        input_to_tiles = next_layer;
        y--;
    }

    // do phenomena like fissures and such
    if (phenomena.length) {
        const key = (tile: Tile): number => tile.pos.x + tile.pos.y * GRID_WIDTH;
        const phenomena_inputs = Object.values(
            phenomena.reduce((all, tile_input) => {
                const k = key(tile_input.tile);
                const prev = all[k] || [];
                all[k] = [...prev, tile_input];
                return all;
            }, {} as {[key: number]: TileInput[]})
        );

        phenomena_inputs.forEach(pi => pi[0]!.tile.incoming(...pi));
    }
}


function handle_liniendeletion_linearriss() {
    const has_linearriss: boolean = game_board.all().filter(tile => tile.TYPE === TimeFissureType.TIME_LINEARRISS).length > 0;
    if (!has_linearriss) { return; }

    // set DESTROYED -> CORRECT
    (game_board.all().filter(tile => tile.TYPE === TimeFissureType.TIME_LINIENDELETION) as Liniendeletion[])
        .filter(deletion => deletion.round_state === PhenomenonRoundState.DESTROYED)
        .forEach(deletion => deletion.round_state = PhenomenonRoundState.CORRECT_COMMAND);    
}

function handle_Short_TF_connections() {
    const all_shorts = game_board.all().filter(tile => tile.TYPE === AnomalyType.ANOMALY_SHORT) as Short[];
    for (const short of all_shorts) {
        const connection = short.connective_tags.find(conn => conn.type === ConnectiveType.SHORT_TF);

        // Short has no connection?
        if (!connection) {
            short.round_state = PhenomenonRoundState.DESTROYED;
            continue;
        }
        const tf = game_board.tiles_by_tag(connection).find(tile => tile.TYPE !== AnomalyType.ANOMALY_SHORT) as TimeFissure;
        
        // connection has no TF?
        if (!tf) {
            short.round_state = PhenomenonRoundState.DESTROYED;
            continue;
        }

        // should at least one be destroyed?
        if (tf.round_state === PhenomenonRoundState.DESTROYED || short.round_state === PhenomenonRoundState.DESTROYED) {
            const all_linearriss = game_board.all().filter(tile => tile.TYPE === TimeFissureType.TIME_LINEARRISS) as Linearriss[];
            
            // time fissure is destroyable => destroy both
            if (tf.TYPE !== TimeFissureType.TIME_LINIENDELETION || all_linearriss.length === 0) {
                short.round_state = PhenomenonRoundState.DESTROYED;
                tf.round_state = PhenomenonRoundState.DESTROYED;
                continue;
            }

            // Short will be destroyed, but connected to a Liniendeletion while Linearriss still exists!
            // => Short stays, Liniendeletion dies and connection switches to a random linearriss
            
            // switch connection
            const linearriss = get_random_of(all_linearriss)!;
            linearriss.connective_tags = [...(linearriss.connective_tags || []), connection];

            // keep Short & destroy Liniendeletion
            if (short.round_state === PhenomenonRoundState.DESTROYED) { short.round_state = PhenomenonRoundState.CORRECT_COMMAND; }
            tf.destroy();
        }
    }
}

function handle_Traceback_Wurmloch_connections() {
    const tracebacks = game_board.all().filter(tile => tile.TYPE === AnomalyType.ANOMALY_TRACEBACK) as Traceback[];
    const wurms = game_board.all().filter(tile => tile.TYPE === SpaceFissureType.SPACE_WURMLOCH) as Wurmloch[];

    // eliminate disconnected Tracebacks
    const connected_tracebacks: Traceback[] = [];
    for (const traceback of tracebacks) {
        const connection = traceback.connective_tags.find(conn => conn.type === ConnectiveType.TRACE_WURM);
        const has_connection = connection && game_board.tiles_by_tag(connection).length > 1;
        
        if (has_connection) {
            connected_tracebacks.push(traceback);
        } else {
            traceback.round_state = PhenomenonRoundState.DESTROYED;
        }
    }

    // eliminate disconnected Wurmlöcher
    const connected_wurms: Wurmloch[] = [];
    for (const wurm of wurms) {
        const connection = wurm.connective_tags.find(conn => conn.type === ConnectiveType.TRACE_WURM);
        const has_connection = connection && game_board.tiles_by_tag(connection).length > 1;

        if (has_connection) {
            connected_wurms.push(wurm);
        } else {
            wurm.round_state = PhenomenonRoundState.DESTROYED;
        }
    }

    console.assert(connected_tracebacks.length === connected_wurms.length);

    for (const traceback of connected_tracebacks) {
        const connection = traceback.connective_tags.find(conn => conn.type === ConnectiveType.TRACE_WURM);
        const wurm = game_board.tiles_by_tag(connection!).find(tile => tile.TYPE === SpaceFissureType.SPACE_WURMLOCH) as Wurmloch;
    
        // both have to be destroyed at the same time!
        if (
            (traceback.round_state === PhenomenonRoundState.DESTROYED && wurm.round_state !== PhenomenonRoundState.DESTROYED) ||
            (traceback.round_state !== PhenomenonRoundState.DESTROYED && wurm.round_state === PhenomenonRoundState.DESTROYED)
        ) {
            if (traceback.round_state === PhenomenonRoundState.DESTROYED) { traceback.round_state = PhenomenonRoundState.CORRECT_COMMAND; }
            if (wurm.round_state === PhenomenonRoundState.DESTROYED) { wurm.round_state = PhenomenonRoundState.CORRECT_COMMAND; }
        }
    }
}