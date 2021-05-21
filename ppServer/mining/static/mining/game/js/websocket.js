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

}

function receiveMsg(e) {
    const data = JSON.parse(e.data);
    const entity_id = data.message;

    switch (data.type) {
        case "break_entity_message":
            // delete entity from game
            entities = entities.filter(entity => entity.id !== entity_id);
            collidables = entities.filter(entity => entity.id !== entity_id);
            breakables = entities.filter(entity => entity.id !== entity_id);
            break;
        default:
            console.log(data);
    }
}

function ws_break(clicked_breakable) {
    webSocket.send(JSON.stringify({ type: "break_entity_message", message: clicked_breakable.id }));
}