document.addEventListener("DOMContentLoaded", function () {

	/* header resize */
	const header = document.getElementsByTagName("header")[0]
	window.onresize = function() {

		// use breakpoint provided by someone else or default (400px)
		try {
			var small = window.innerWidth <= breakpoint
		} catch (ReferenceError) {
			var small = window.innerWidth <= 400
		}
		header.setAttribute("data-size", small ? "small" : "")
	}

	// trigger test for width in case noone else did (after setting breakpoint)
	// no guarantee for ordering though, if that happens after this bit
	window.dispatchEvent(new Event('resize'));

	/* toggle dropdown of small nav */
	document.getElementsByClassName("nav__more")[0].addEventListener("click", function() {
		var list = document.getElementsByClassName("dropdown-content")[0]
		list.style.display = list.style.display === "" || list.style.display === "none" ? "block" : "none";
	})
});
