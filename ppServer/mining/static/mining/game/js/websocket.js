var webSocket;

function initWsSocket() {
    const ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    const region_id = JSON.parse(document.querySelector('#region-id').innerHTML);

    const wsUrl = `${ws_scheme}://${window.location.host}/ws/mining/game/${region_id}/`;
    webSocket = new WebSocket(wsUrl);

    webSocket.onmessage = receiveMsg;
    webSocket.onclose = leave;
}

function leave() {
    console.log("Your Web socket connection is terminated");
}

function receiveMsg(e) {
    const data = JSON.parse(e.data);
    
    switch (data.type) {
        case "break_entity_message":
            const {entity_id} = data.message;

            // delete entity from game
            entities = entities.filter(entity => entity.id !== entity_id);
            collidables = entities.filter(entity => entity.id !== entity_id);
            breakables = entities.filter(entity => entity.id !== entity_id);

            if (data.username = player.username) {
                // data.message = {
                //     amount: number,
                //     total_amount: number,
                //     entity_id: number,
                //     bg_color: string,   // rgb-hex
                //     crafting_item: { id, name, icon_url },
                //     height: number,
                //     id: number,
                //     max_amount: number,
                //     width: number
                // }
                const {id, height, width, bg_color, crafting_item} = data.message.item;
                const item = {
                    id,
                    h: height,
                    w: width,
                    amount: data.message.total_amount,
                    bg_color,
                    image_href: crafting_item.icon_url
                }
                Inventory.setItem(item);
            }
            break;
        case "player_position_message":
            const username = data.username;
            const {position, speed} = data.message;
            if (username === player.username) { return; }
            
            let other_player = other_players.find(p => p.username === username);
            if (!other_player) {
                other_player = new Player(position, username);
            } else {
                other_players = other_players.filter(p => p !== other_player);
                other_player.speed = {
                    x: position.x - other_player.pos.x,
                    y: position.y - other_player.pos.y
                };
                other_player.pos = position;
            }
            other_player.speed = speed;
            other_players.push(other_player);
            break;
        default:
            console.log(data);
    }
}

function ws_break(clicked_breakable) {
    const timer_handle = setInterval(() => {
        if (webSocket.readyState === 1) {
            webSocket.send(JSON.stringify({ type: "break_entity_message", message: clicked_breakable.id }));
            clearInterval(timer_handle);
        }
    }, 100);
}

function ws_player_pos({position, speed}) {
    const timer_handle = setInterval(() => {
        if (webSocket.readyState === 1) {
            webSocket.send(JSON.stringify({ type: "player_position_message", message: {position, speed} }));
            clearInterval(timer_handle);
        }
    }, 100);
}

function ws_save_player_position(position) {
    const timer_handle = setInterval(() => {
        if (webSocket.readyState === 1) {
            webSocket.send(JSON.stringify({ type: "save_player_position_message", message: position }));
            clearInterval(timer_handle);
        }
    }, 100);
}