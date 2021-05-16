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
    console.log(data)
}