var text_input;
var name_input;
var chatSocket;

document.addEventListener('DOMContentLoaded', () => {

    text_input = document.querySelector(".input-message");
    name_input = document.querySelector(".input-name");
    initWsSocket();

    // send message on enter in text input
	document.querySelectorAll(".footer__new-msg").forEach(tag =>
        tag.addEventListener("keydown", ({ keyCode }) => {

            // on enter
            if (keyCode === 13) set_new_msg()
        })
    )
})

function initWsSocket() {
    const wsUrl = `ws://${window.location.host}/ws/chat/${document.querySelector('#room_name').textContent}/`;
    chatSocket = new WebSocket(wsUrl);

    // test
    chatSocket.onmessage = e => {
        const data = JSON.parse(e.data);
        document.querySelector('.message-container').innerHTML += `<p>${data.username || 'anonymous'}: ${data.message}</p>`;
    }
}


function set_new_msg() {
    const message = text_input.value;
    const name = name_input.value || 'anonymous';

    if (!message) return;

    chatSocket.send(JSON.stringify({ message, name }));

    text_input.value = "";
}