let popup_opened = false;


function refresh_page(msg = 'Die nicht versendete Nachricht wird beim Refreshen gelöscht. Trotzdem Refreshen?') {
	if (popup_opened) { return; }
	
	popup_opened = true;
	if (!document.querySelector("#prompt").value || confirm(msg)) {
		location.reload(true);
	}
	popup_opened = false;
}

/** poll for new messages. Then refresh page if some exist. */
function poll_new_messages() {
	const url = `${location.href.replace(/\/$/, "")}/poll`;
	axios.get(url)
		.then(({data}) => data.unread_messages && refresh_page('Es gibt neue Nachrichten. Deine nicht versendete Nachricht wird beim Laden allerdings gelöscht. Trotzdem Laden?'));
}

/** scroll messages to the bottom */
function set_footer_height() {
	const prompt = document.querySelector("#prompt");
	document.documentElement.style.setProperty("--footer-height", prompt.style.height);

	// scroll messages down
	const msg_container =  document.querySelector("#message-container")
	msg_container.scrollTo(0, msg_container.scrollHeight);
}

/*
	ON LOAD
*/
document.addEventListener("DOMContentLoaded", _ => {
	const prompt = document.querySelector("#prompt");

	// send message on enter in text input
	prompt.addEventListener("keydown", function({ keyCode }) {
		
		// on enter
		if (keyCode === 13 && this.value?.length) this.form.submit();
	})

	// poll for new messages. Then refresh page
	const minute_in_miliseconds = 60 * 1000;
	setInterval(() => {
		if (popup_opened) { return; }
		poll_new_messages();
	}, 2 * minute_in_miliseconds);

	
	// initial scroll down
	set_footer_height()
	// scroll messages to the bottom on prompt height change
	new ResizeObserver(set_footer_height).observe(prompt);
})
