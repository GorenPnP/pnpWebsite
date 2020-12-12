player = -1
state = -1
modul = -1

module_states = {}		// initial states
dirty_states = {}
dirty_optionals = []

// transfer via html via AJAX into page
function attachEntries(data) {
	reaction(data)

	module_list = document.getElementsByClassName("module-list")[0]
	module_list.innerHTML = ""
	module_list.insertAdjacentHTML("beforeend", data["html"])

	reapplyDirty()
}

// dirty-marker is potentially deleted on filter change, reapply afterwards
function reapplyDirty() {

	var enableBtn = false

	// go over all dirty ones
	Object.keys(dirty_states).forEach(id => {
		tag = document.getElementById(id)
		if (!tag) return

		// add dirty class
		enableBtn = true
		tag.parentNode.classList.add("dirty")

		// get previously selected option back
		for (var i = 0; i < tag.options.length; i++) {
			if (tag.options[i].value == dirty_states[id]) {
				tag.selectedIndex = i
				break
			}
		}
	})

	// handle submit-btn
	if (!enableBtn) document.getElementsByClassName("submit")[0].classList.remove("active")
	else document.getElementsByClassName("submit")[0].classList.add("active")
}


// event handlers
// changed player filter
function refreshPlayer({ currentTarget }) {
	player = parseInt(currentTarget.options[currentTarget.selectedIndex].value)
	post({ player, state, modul }, attachEntries)
}

// changed state filter
function refreshState({ currentTarget }) {
	state = parseInt(currentTarget.options[currentTarget.selectedIndex].value)
	post({player, state, modul }, attachEntries)
}

// changed module filter
function refreshModule({ currentTarget }) {
	modul = parseInt(currentTarget.options[currentTarget.selectedIndex].value)
	post({ player, state, modul }, attachEntries)
}



// changed state of one Module
function changeState({ currentTarget }) {
	var new_state = parseInt(currentTarget.getElementsByClassName("option" + currentTarget.selectedIndex)[0].value)
	var id = parseInt(currentTarget.id)

	// set class dirty and add to dirty_states if state is not initial state. If so, reverse
	if (new_state != module_states[id]) {
		currentTarget.parentNode.parentNode.classList.add("dirty")
		dirty_states[id] = new_state
	} else {
		currentTarget.parentNode.parentNode.classList.remove("dirty")
		delete dirty_states[id]
	}

	// adapt submit-btn
	if (document.getElementsByClassName("dirty").length)
		document.getElementsByClassName("submit")[0].classList.add("active")
	else
		document.getElementsByClassName("submit")[0].classList.remove("active")
}


function changeOptional(checkbox) {
	checkbox.classList.toggle("checked")
	var id = parseInt(/\d+/.exec(checkbox.id))
	console.log(id)

	// set class dirty and add to dirty_states if state is not initial state. If so, reverse
	if (!dirty_optionals.includes(id)) {
		checkbox.parentNode.parentNode.classList.add("dirty")
		dirty_optionals.push(id)
	} else {
		checkbox.parentNode.parentNode.classList.remove("dirty")
		dirty_optionals = dirty_optionals.filter(o_id => o_id !== id)
	}

	// adapt submit-btn
	if (document.getElementsByClassName("dirty").length)
		document.getElementsByClassName("submit")[0].classList.add("active")
	else
		document.getElementsByClassName("submit")[0].classList.remove("active")
}


// save changed states of modules
function submit() {

	// no change, btn should be inactive anyway
	if (!Object.keys(dirty_states).length && !dirty_optionals.length) return

	post({"state_changes": dirty_states, "optional_changes": dirty_optionals}, () => {

		// remove all 'dirty'-classes
		Object.keys(dirty_states).forEach(id => {
			document.getElementById(id).parentNode.classList.remove("dirty")
			module_states[id] = dirty_states[id]
		})

		dirty_optionals.forEach(id => {
			document.getElementById(id).parentNode.classList.remove("dirty")
		})

		// clear dirty_modules and disable submit-btn
		dirty_states = {}
		dirty_optionals = []
		document.getElementsByClassName("submit")[0].classList.remove("active")
	})
}


// collect initial states
document.addEventListener("DOMContentLoaded", () => {
	Array.from(document.getElementsByClassName("stateChange")).forEach(tag => {
		module_states[parseInt(tag.id)] = parseInt(tag.getElementsByClassName("option" + tag.selectedIndex)[0].value)
	})
})
