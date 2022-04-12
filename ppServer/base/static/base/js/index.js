var carousel_tag
var arrow_left
var arrow_right

var current = 0
var max_index

// slide all slides to the left or right by 100vw, relative to their index and the next slide visible
function reposition() {
	console.log(current)
	// hide left- and rightmost arrows
	document.getElementsByClassName("arrow--left")[0].style.visibility = current <= 0 ? 'hidden' : 'visible'
	document.getElementsByClassName("arrow--right")[0].style.visibility = current >= max_index ? 'hidden' : 'visible'

	carousel_tag.getElementsByClassName("slider")[0].style.transform = "translateX(" + current * -100 + "vw)"
}

// on click handlers for left & right arrows
function moveLeft() {
	if (current <= 0) { return; }
	current--;
	reposition()
}
function moveRight() {
	if (current >= max_index) { return; }
	current++;
	reposition()
}

document.addEventListener("DOMContentLoaded", function () {

	//document.getElementsByClassName("hero")[0].style.transition = "transform 1s"
	carousel_tag = document.getElementsByClassName("hero-container")[0]
	max_index = carousel_tag.getElementsByClassName("hero").length - 1;

	if (max_index <= 0) {
		carousel_tag.classList.add("empty")
		return
	}

	// get arrows
	arrow_left = document.getElementsByClassName("arrow--left")[0]
	arrow_right = document.getElementsByClassName("arrow--right")[0]

	arrow_left.addEventListener('click', moveLeft)
	arrow_right.addEventListener('click', moveRight)

	// position initially and enable arrows (i.e. set onclick handlers)
	reposition()
})
