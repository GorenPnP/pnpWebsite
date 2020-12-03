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
    if (oField.scrollHeight > oField.clientHeight) {
        oField.style.height = oField.scrollHeight + "px"
    }
}

function back(e) {
    e.preventDefault()
    window.history.back()
}


// for /quiz/sp/correction/.. only
document.addEventListener("DOMContentLoaded", _ => {
    const checkboxes = [...document.getElementsByClassName("checkbox checkbox--correction wrong-answer")]
    checkboxes.forEach(checkbox => checkbox.classList.toggle('checked'))
})
