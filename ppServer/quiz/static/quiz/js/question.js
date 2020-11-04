function toggleCheckbox(id) {
    // toggle clicked checkbox
    document.getElementById(id).classList.toggle('checked')

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
