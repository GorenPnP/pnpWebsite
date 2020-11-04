document.addEventListener("DOMContentLoaded", function () {
	//setTimeout(() => document.getElementsByClassName("spinner-container")[0].style.display = 'none', 500)

	window.onbeforeunload = function () {
		document.getElementsByClassName("spinner-container")[0].style.display = 'flex'
		document.getElementsByClassName("spinner-container")[0].style.opacity = 1;
	};
})
