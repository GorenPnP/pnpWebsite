function initWsSocket() {
    const ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    const wsUrl = `${ws_scheme}://${window.location.host}/ws/mining/game/${document.querySelector('#region-id').textContent}/`;
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