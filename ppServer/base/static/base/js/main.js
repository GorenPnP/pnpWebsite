let ready = false;

document.addEventListener("DOMContentLoaded", function () {
	window.onbeforeunload = function () {
		if (ready) { return; }

		document.getElementsByClassName("spinner-container")[0].style.display = 'flex'
		document.getElementsByClassName("spinner-container")[0].style.opacity = 1;
	};
})

document.onreadystatechange = function () {
    if (this.readyState === "interactive") {
		ready = true;
		document.getElementsByClassName("spinner-container")[0].style.display = 'none'
	}
}