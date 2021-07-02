// May use callbacks on dragstart and dragend:
//
// drag_start_callback(of_element)
// drag_end_callback(of_element)
//
// Basic structure:
//
// <div class="reorder-container">
//		<div class="reorder-container__element" draggable="true"></div>
//		...
// </div>


/*
	VARIABLES
*/
var offsetTouchX = null;
var offsetTouchY = null;

var container;

/*
	HELPER FUNCTIONS
*/

// returns element of container below position of cursor
function getDragAfterElement(container, y) {
	const draggableElements = [...container.querySelectorAll('.reorder-container__element:not(.dragging)')]

	return draggableElements.reduce((closest, child) => {

		// y-offset cursor from center of element, if negative cursor above element
		const box = child.getBoundingClientRect()
		const offset = y - box.top - box.height / 2

		// if offset negative and closer to 0, take that. Else: keep old one
		return offset < 0 && offset > closest.offset ? { offset: offset, element: child } : closest

		// initial value of closest, simulates element infinitely further down; (.element: just return element without the offset)
	}, { offset: Number.NEGATIVE_INFINITY }).element
}


/*
	event handlers for dragging elements
*/
function init_draggable_reorder() {

	// handle dragging
	container = document.getElementsByClassName("reorder-container")[0]
	const draggables = [...container.getElementsByClassName('reorder-container__element')]

	// fires constantly if dragging over container (.reorder-container)
	container.addEventListener('dragover', e => {

		// allow dropping into container
		e.preventDefault()

		// get moving element and the one below its position
		const afterElement = getDragAfterElement(container, e.clientY)
		const draggable = document.getElementsByClassName('dragging')[0]

		// set moving element before the element or at the absolute bottom if null
		afterElement == null ? container.appendChild(draggable) : container.insertBefore(draggable, afterElement)

		offsetTouchX = e.layerX
		offsetTouchY = e.layerY
	});

	// set class dragging on drag of element
	draggables.forEach(draggable => add_draggable(draggable))
}


function add_draggable(draggable) {
	draggable.addEventListener('dragstart', () => {
		draggable.classList.add('dragging')
		
		drag_start_callback(draggable)
	})
	draggable.addEventListener('dragend', () => {
		draggable.classList.remove('dragging')

		// callback
		drag_end_callback(draggable)
	})




	/*
		... for mobile
	*/
	draggable.addEventListener("touchstart", e => {
		e.preventDefault();
		draggable.classList.add('dragging')
		draggable.classList.add('dragging--mobile')

		const touch = e.targetTouches[0]
		offsetTouchY = draggable.getBoundingClientRect().height * .5

		draggable.dispatchEvent(new TouchEvent("touchmove", { targetTouches: [touch] }))

		// callback
		drag_start_callback(draggable)
	})

	draggable.addEventListener("touchmove", e => {

		const touch = e.targetTouches[0]

		// container position relative to whole document
		var containerTop = window.scrollY + container.offsetTop
		draggable.style.top = `${touch.pageY - containerTop - offsetTouchY}px`
		draggable.style.left = `${container.style.paddingLeft}px`

		// work on elements
		// get moving element and the one below its position
		const afterElement = getDragAfterElement(container, e.targetTouches[0].clientY)

		var copy = container.getElementsByClassName("copy")
		if (!(copy?.length)) {

			// (mark as) copy
			copy = draggable.cloneNode(true);
			copy.classList.add("copy")

			// unset fields of original
			copy.id = "";
			copy.style.position = "unset";
			copy.style.left = "unset"
			copy.style.top = "unset";
		}
		// get existing copy of dragged element
		else copy = copy[0]

		// set moving element before the element or at the absolute bottom if null
		afterElement == null ? container.appendChild(copy) : container.insertBefore(copy, afterElement)
	})

	draggable.addEventListener("touchend", e => {
		e.preventDefault();
		draggable.classList.remove('dragging')
		draggable.classList.remove('dragging--mobile')

		var copies = [...container.getElementsByClassName("copy")]
		copies.forEach(c => c.remove())

		// get moving element and the one below its position
		const afterElement = getDragAfterElement(container, e.changedTouches[0].clientY)

		// set moving element before the element or at the absolute bottom if null
		afterElement == null ? container.appendChild(draggable) : container.insertBefore(draggable, afterElement)

		// callback
		drag_end_callback(draggable)
	})
}