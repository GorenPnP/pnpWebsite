let ready = false;

document.addEventListener("DOMContentLoaded", function () {
	const spinner_container = document.getElementsByClassName("spinner-container")?.[0];

	window.onbeforeunload = function () {
		if (ready || !spinner_container) { return; }

		spinner_container.style.display = 'flex'
		spinner_container.style.opacity = 1;
	};
})

document.onreadystatechange = function () {
	const spinner_container = document.getElementsByClassName("spinner-container")?.[0]
    if (this.readyState === "interactive") {
		ready = true;
		if (spinner_container) spinner_container.style.display = 'none'
	}
}