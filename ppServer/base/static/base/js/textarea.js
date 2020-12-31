// auto-grow textarea on typing
function autoGrow(oField) {
	oField.style.lineHeight = 1.2
	if (oField.scrollHeight != oField.clientHeight) {
		oField.style.height = `${oField.scrollHeight * 1.2}px`
	}
}

document.addEventListener("DOMContentLoaded", _ => {

	// resize textareas
	const textareas = [...document.getElementsByTagName("textarea")]
	textareas.forEach(area => {
		autoGrow(area)
		area.addEventListener("keyup", ({ currentTarget }) => autoGrow(currentTarget))
		area.addEventListener("input", ({ currentTarget }) => autoGrow(currentTarget))
	})
})
