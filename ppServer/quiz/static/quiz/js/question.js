function toggleCheckbox(id) {
    // toggle clicked checkbox
    const checkbox = document.getElementById(id)
    checkbox.classList.toggle('checked')

    if (checkbox.classList.contains('checkbox--correction'))
        checkbox.classList.toggle('wrong-answer')

    var list_tag = document.getElementById("ids")
    var list = JSON.parse(list_tag.value)

    // toggle its id in list
    if (list.indexOf(id) !== -1) list = list.filter(e => {return e !== id})
    else list.push(id)

    // write list back
    list_tag.value = JSON.stringify(list)
}

// auto-grow textarea on typeing
function autoGrow(oField) {
    oField.style.lineHeight = 1.2
    if (oField.scrollHeight != oField.clientHeight) {
        oField.style.height = `${oField.scrollHeight * 1.2}px`
    }
}

function back(e) {
    e.preventDefault()
    window.history.back()
}

function back_to_previous(e) {
    e.preventDefault()

    const form = document.getElementsByTagName("form")[0]
    form.querySelector("input.previous").checked = true
    form.querySelector("input.points__input").required = false
    form.submit()
}


function updateChecked() {

    // for /quiz/sp/correction/.. only
    const checkboxes = [...document.getElementsByClassName("checkbox checkbox--correction wrong-answer")]
    checkboxes.forEach(checkbox => checkbox.classList.toggle('checked'))

    // for /quiz/question/.. only
    if (checkboxes.length == 0) {
        const checked = JSON.parse(document.getElementById("ids").value)
        checked.forEach(id => document.getElementById(`${id}`).addEventListener("change"));
    }
}

document.addEventListener("DOMContentLoaded", _ => {

    // resize textareas
    const textareas = [...document.getElementsByTagName("textarea")]
    textareas.forEach(area => autoGrow(area))

    // handle checkboxes (on file upload)
    const inputs = [...document.querySelectorAll("input[type=file]")]
    inputs.forEach(input => {
        input.addEventListener("change", __ => updateChecked)
        input.addEventListener("click", __ => updateChecked)
    })

    updateChecked()
})
