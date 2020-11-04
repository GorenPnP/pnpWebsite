var marked_row = ""

// get class of row
function getClass(tag, prefix = "row") {

    var classes = tag.classList
    for (var c = 0; c < classes.length; c++) {
        if (classes[c].startsWith(prefix)) return classes[c];
    }
    return null
}

document.addEventListener("DOMContentLoaded", function () {

    window.addEventListener('hashchange', scroll);
    scroll();
})


function scroll() {
    var viewport_height = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0)
    var hash = window.location.hash
    var id = hash.substring(1)

    if (hash) {
        window.scrollBy(0, -.5 * viewport_height)

        if (marked_row !== "") {
            var tags = document.getElementsByClassName(marked_row)
            for (var i = 0; i < tags.length; i++) tags[i].classList.remove("selected")
        }

        marked_row = getClass(document.getElementsByName(id)[0], "row")
        if (marked_row !== "") {
            var tags = document.getElementsByClassName(marked_row)
            for (var i = 0; i < tags.length; i++) tags[i].classList.add("selected")
        }
    }
}
