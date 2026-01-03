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

function back(e) {
    e.preventDefault()
    window.history.back()
}

function submit_and_redirect(button) {

    // setup redirect url
    const redirect = document.querySelector('#redirect') // add redirect to POST data
    redirect.name = 'redirect'
    redirect.value = button.dataset.redirect

    // points are optional
    const points = document.querySelector(".points__input")
    points.required = false

    // send
    document.querySelector('form').submit()
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

    // handle checkboxes (on file upload)
    const inputs = [...document.querySelectorAll("input[type=file]")]
    inputs.forEach(input => {
        input.addEventListener("change", __ => updateChecked)
        input.addEventListener("click", __ => updateChecked)
    })

    updateChecked()
})
