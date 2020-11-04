var initial_zauber;
var zauber_pool_tag;
var submit_btn;

var zauber_ids = [];

var checked = "checked";

// get class of row
function getClass(tag, prefix = "row") {

    var classes = tag.classList
    for (var c = 0; c < classes.length; c++) {
        if (classes[c].startsWith(prefix)) return classes[c];
    }
    return null
}

document.addEventListener("DOMContentLoaded", function () {
    zauber_pool_tag = document.getElementById("zauber_pool")
    initial_zauber = parseInt(zauber_pool_tag.innerHTML)
    submit_btn = document.getElementById("submit")

    // handle btn
    submit_btn.disabled = initial_zauber !== 0

    // get all selected checkboxes
    checkboxes = document.getElementsByClassName("checkbox");
    selectedCboxes = Array.prototype.slice.call(checkboxes).filter(ch => ch.classList.contains(checked));
    initial_zauber += selectedCboxes.length

    // add them initially to form lists
    for (var i = 0; i < selectedCboxes.length; i++) {

        var zauber_class = getClass(selectedCboxes[i], "zauber-id-")
        var zauber = parseInt(/\d+/.exec(zauber_class))

        zauber_ids.push(zauber)
    }
})


// toggle of (un)checked prior to this handler
function onClick(e) {

    // toggle select on pseudo-checkbox
    e.currentTarget.classList.toggle(checked)

    // handle zauber_pool
    var zauber_pool = parseInt(zauber_pool_tag.innerHTML)
    zauber_pool += e.currentTarget.classList.contains(checked) ? -1 : 1;
    zauber_pool_tag.innerHTML = zauber_pool

    // handle btn
    submit_btn.disabled = zauber_pool !== 0

    // handle form list
    var zauber_class = getClass(e.currentTarget, "zauber-id-")
    var zauber = parseInt(/\d+/.exec(zauber_class))

    // work with input tags
    if (e.currentTarget.classList.contains(checked)) zauber_ids.push(zauber)
    else zauber_ids = zauber_ids.filter((j) => { return j !== zauber })
}

function submit() {
    post({id_list: zauber_ids})
}
