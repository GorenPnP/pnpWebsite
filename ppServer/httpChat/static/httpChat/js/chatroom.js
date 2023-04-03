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
})
