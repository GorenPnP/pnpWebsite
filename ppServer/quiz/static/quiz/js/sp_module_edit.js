document.addEventListener("DOMContentLoaded", () => {
	// TODO use or delete?

	// const question_select = document.getElementById("id_questions")

	// const container = document.createElement("div")
	// container.id = "questions"
	// container.classList.add("reorder-container")

	// question_select.parentNode.append(container)
	// question_select.parentNode.querySelector("label").htmlFor = "question"

	// question_select.querySelectorAll("option").forEach(option => {
	// 	let element = document.createElement("div")

	// 	element.id = option.value
	// 	element.classList.add("reorder-container__element")
	// 	element.innerHTML = option.innerHTML

	// 	container.append(element)
	// })
	// question_select.remove()

	init_draggable_reorder()
})
