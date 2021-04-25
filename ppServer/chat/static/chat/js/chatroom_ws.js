var text_input;
var name_input;
var chatSocket;
var username;

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
    const ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    const wsUrl = `${ws_scheme}://${window.location.host}/ws/chat/${document.querySelector('#room_name').textContent}/`;
    chatSocket = new WebSocket(wsUrl);

    chatSocket.onmessage = receive_msg;
    chatSocket.onclose = leave_chat;
}


// close this chat on logout
function leave_chat() {
    document.querySelector('.message-container').innerHTML += `<div class="info">Leaving this chat...</div>`;
    setTimeout(() => location.href = `/chat`, 5000);
}

function set_new_msg() {
    const charactername = name_input.value || '';
    const message = text_input.value;
    if (!message) return;
    
    chatSocket.send(JSON.stringify({ message, charactername }));
    text_input.value = "";
}

function receive_msg(e) {
    
    const data = JSON.parse(e.data);
    username = username || data.username;
    switch(data.type) {

        case 'message':
            display_message(data); break;
        
        case 'info':
            display_info(data); break;

        default:
            console.log('type not applicable');
    }
}

function display_message(data) {
    let message = `<div class="message ${data.username === username ? "message--own" : "message--foreign"}">`;
        if (data.username !== username) message += `<span class="message__author">${data.charactername || 'anonymous'} (${data.username})</span>`;
        message += `${data.message}</div>`

    document.querySelector('.message-container').innerHTML += message;
}

function display_info(data) {
    const message = `<div class="info">${data.username === username ? "You" : data.username} ${data.message}</div>`

    document.querySelector('.message-container').innerHTML += message;
}