var show_nav_tag;

// also don't play an animation in the beginning (without either class), because that's annoying. Just be closed.
// use 2 classes (expand, shrink) in css to toggle between two different animations, because one animation of same name won't run twice
function toggleMenu() {
	if (show_nav_tag.classList.contains("expand") || show_nav_tag.classList.contains("shrink"))
		show_nav_tag.classList.toggle("shrink")

	show_nav_tag.classList.toggle("expand")
}

// callback for nav-links (see html)
function changeSection({ currentTarget }) {

	// need to send request to server, or is it the current page?
	var load = true;

	// remove class 'current'
	Array.from(document.getElementsByClassName("show-nav__item current")).forEach(tag => {
		if (currentTarget !== tag) tag.classList.remove("current")
		else load = false
	})
	if (load) {

		// add it to the selected tag
		currentTarget.classList.add("current")

		post({section: currentTarget.innerHTML}, (data) => {

			if (Object.keys(data).indexOf("html") !== -1)

				// set response-html as container content
				document.getElementsByClassName("container")[0].innerHTML = data["html"]

			else
				document.location.href = "/accounts/login/?next=" + document.location.pathname

			toggleMenu()
			},
			(data) => {
				reaction(data)
				toggleMenu()
			}
		)

		// close menu anyways
	} else toggleMenu()
}


document.addEventListener("DOMContentLoaded", () => {
	show_nav_tag = document.getElementsByClassName("show-nav")[0]

	// close menu on click to X
	document.getElementsByClassName("mobile-nav")[0].addEventListener("click", () => {
		toggleMenu()
	})
})
