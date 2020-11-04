var carousel_tag
var slides = []
var arrow_left
var arrow_right

var current = -1

// slide all slides to the left or right by 100vw, relative to their index and the next slide visible
function reposition(left) {
	current += left ? 1 : -1;
	slides.forEach((slide, nr) => slide.style.transform = "translateX(" + (current + nr) * 100 + "vw)")

	enableArrows()
}

// utilities for adding and removing on-click handlers of arrows
function enableArrows() {
	arrow_left.forEach(arrow => arrow.addEventListener('click', moveLeft))
	arrow_right.forEach(arrow => arrow.addEventListener('click', moveRight))
}
function disableArrows() {
	arrow_left.forEach(arrow => arrow.removeEventListener('click', moveLeft))
	arrow_right.forEach(arrow => arrow.removeEventListener('click', moveRight))
}

// on click handlers for left & right arrows
function moveLeft() {
	disableArrows()
	reposition(true)
}
function moveRight() {
	disableArrows()
	reposition(false)
}

document.addEventListener("DOMContentLoaded", function () {

	//document.getElementsByClassName("hero")[0].style.transition = "transform 1s"
	carousel_tag = document.getElementsByClassName("hero")[0]

	// gather all slides
	slides = [...document.getElementsByClassName('hero__container')]

	if (!slides.length) {
		carousel_tag.classList.add("empty")
		return
	}

	// hide left- and rightmost arrows
	slides[0].getElementsByClassName("hero__arrow--left")[0].style.visibility = 'hidden'
	slides[slides.length - 1].getElementsByClassName("hero__arrow--right")[0].style.visibility = 'hidden'

	// get arrows
	arrow_left = [...document.getElementsByClassName("hero__arrow--left")]
	arrow_right = [...document.getElementsByClassName("hero__arrow--right")]

	// position initially and enable arrows (i.e. set onclick handlers)
	reposition(true)
})
