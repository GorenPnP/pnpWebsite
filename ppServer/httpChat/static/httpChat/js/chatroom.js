/** poll for new messages. Then refresh page if some exist. */
function poll_new_messages() {
	const url = `${location.href.replace(/\/$/, "")}/poll`;
	axios.get(url)
		.then(({data}) => data.new_messages && location.reload());
}

/*
	ON LOAD
*/
document.addEventListener("DOMContentLoaded", _ => {

	// send message on enter in text input
	document.querySelector("#prompt").addEventListener("keydown", function({ keyCode }) {
		
		// on enter
		console.log(this)
		if (keyCode === 13 && this.value?.length) this.form.submit();
	})

	// initial scroll down
	const msg_container =  document.querySelector("#message-container")
	msg_container.scrollTo(0, msg_container.scrollHeight);

	// poll for new messages. Then refresh page
	const minute_in_miliseconds = 60 * 1000;
	setInterval(() => {
		console.log("Polling...")
		poll_new_messages();
	}, 2 * minute_in_miliseconds);
})
