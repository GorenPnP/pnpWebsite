module_states = {}		// initial states
dirty_states = {}
dirty_optionals = []


// changed state of one Module
function changeState({ currentTarget }) {
	const new_state = parseInt(currentTarget.value)
	const id = parseInt(currentTarget.id)

	// set class dirty and add to dirty_states if state is not initial state. If so, reverse
	if (new_state != module_states[id]) {
		currentTarget.classList.add("dirty")
		currentTarget.parentNode.parentNode.parentNode.classList.add("dirty--state")
		dirty_states[id] = new_state
	} else {
		currentTarget.classList.remove("dirty")
		currentTarget.parentNode.parentNode.parentNode.classList.remove("dirty--state")
		delete dirty_states[id]
	}

	adapt_submit_btn();
}


function changeOptional(checkbox) {
	var id = parseInt(/\d+/.exec(checkbox.id))

	// set class dirty and add to dirty_states if state is not initial state. If so, reverse
	if (!dirty_optionals.includes(id)) {
		checkbox.classList.add("dirty")
		checkbox.parentNode.parentNode.parentNode.classList.add("dirty--optional")
		dirty_optionals.push(id)
	} else {
		checkbox.classList.remove("dirty")
		checkbox.parentNode.parentNode.parentNode.classList.remove("dirty--optional")
		dirty_optionals = dirty_optionals.filter(o_id => o_id !== id)
	}

	adapt_submit_btn();
}

function adapt_submit_btn() {
	if (dirty_optionals.length || Object.keys(dirty_states).length)
		document.querySelector("#save-changes-btn").removeAttribute("disabled")
	else
		document.querySelector("#save-changes-btn").setAttribute("disabled", true)
}


// collect initial states
document.addEventListener("DOMContentLoaded", () => {
	Array.from(document.querySelectorAll(".stateChange")).forEach(tag => {
		module_states[parseInt(tag.id)] = parseInt(tag.value)
	})
})
