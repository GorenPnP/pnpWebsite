/*
	VARIABLES
*/
var last_displayed_datetime = null
var message_container = null
var new_msg_input = null

var new_msg = null

/*
	HELPER FUNCTIONS
*/
function set_new_msg() {
	new_msg = new_msg_input.value.trim()
	new_msg_input.value = ""

	send_new_msg()
}


// send new_msg as long as it got saved successfully
function send_new_msg() {
	if (!new_msg) return;

	post(
		{ new_msg: new_msg },
		_ => new_msg = null,
		error => setTimeout(send_new_msg, 1000),
		false)
}


// construct new messages for spielleiter view
function construct_messages({ messages, own_name, spielleiter }) {

	if (spielleiter) {
		return messages.map(message => {
			let html_fragment = `<div class="message ${message.author == own_name ? 'message--own' : 'message--foreign'}">`
			if (message.author != own_name)
				html_fragment += `<span class="message__author">${message.author}</span>`

			html_fragment += `${message.text}</div>`

			return html_fragment
		}).join('')
	}

	return messages.map(message => `<div class="message">${message.text}</div>`).join('')
}


function scroll_down() {
	message_container.scrollTo(0, message_container.scrollHeight);
}


/*
	ON LOAD
*/
document.addEventListener("DOMContentLoaded", _ => {

	// init constants
	last_displayed_datetime = document.querySelector("#last_displayed_datetime")
	message_container = document.querySelector(".message-container")
	new_msg_input = document.querySelector('.footer__new-msg')


	// send message on enter in text input
	document.querySelector(".footer__new-msg").addEventListener("keydown", ({ keyCode }) => {

		// on enter
		if (keyCode === 13) set_new_msg()
	})


	// poll for new messages
	setInterval(__ => {
		post({ since: last_displayed_datetime.value },
			data => {

				const html = construct_messages(data)


				// append messages in DOM
				last_displayed_datetime.insertAdjacentHTML('beforebegin', html)

				if (data) {
					// update timestamp to most recent message
					last_displayed_datetime.value = data.messages.reverse()[0].created_at

					// scroll to latest message
					scroll_down()
				}
			},
			undefined,
			false)

	}, 1000);

	// initial scroll down
	scroll_down()
})
