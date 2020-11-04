var begin_checked = "begin";
var new_checked = "selected";

var init = true
var initial_ip = 0
var ip_pool_tag
var vorteil_data = {}
var nachteil_data = {}

// get class of row
function getClass(tag, prefix = "row") {

    var classes = tag.classList
    for (var c = 0; c < classes.length; c++) {
        if (classes[c].startsWith(prefix)) return classes[c];
    }
    return null
}

document.addEventListener("DOMContentLoaded", function () {

    ip_pool_tag = document.getElementById("ip_pool")
    initial_ip = parseInt(ip_pool_tag.innerHTML)

    onChange()
    init = false
});

function onChange() {

    var sum = 0
    var anz_tags = document.getElementsByClassName("anz")
    for (var i = 0; i < anz_tags.length; i++) {

        // prepare for form data manipulation
        var val = parseInt(anz_tags[i].value)
        var id = parseInt(/\d+/.exec(getClass(anz_tags[i], "teilid-")))

        var vorteil = getClass(anz_tags[i], "teil") === "teil-vor"
        var data = vorteil ? vorteil_data : nachteil_data

        var row_class = getClass(anz_tags[i], "row")
        if (val) {
            // pretty print
            if (init) {
                //document.getElementsByClassName(row_class).forEach(function(e) {e.classList.add(begin_checked)})
                Array.prototype.forEach.call(document.getElementsByClassName(row_class), (e) => e.classList.add(begin_checked))
            } else {
                Array.prototype.forEach.call(document.getElementsByClassName(row_class), (e) => e.classList.add(new_checked))
            }

            // sum ip difference (vorteil -> -, nachteil -> +)
            var ip = parseInt(document.getElementsByClassName("ip " + row_class)[0].innerHTML)
            sum += vorteil ? ip * val * -1 : ip * val

            // set anz of teil in form data
            var notizen = document.getElementsByClassName("notizen " + row_class)[0].value
            data[id] = {"anz": val, "notizen": notizen}


        // val === 0 -> delete entry of teil in form data
        } else {
            delete data[id]

            // pretty print
            if (!init) {
                Array.prototype.forEach.call(document.getElementsByClassName(row_class), (e) => {
                    e.classList.remove(new_checked)
                    e.classList.remove(begin_checked)
                })
            }
        }
    }

    if (init) initial_ip -= sum
    else ip_pool_tag.innerHTML = initial_ip + sum
}

function updateNotizen(e) {

    var id = /\d+/.exec(getClass(e.currentTarget, "teilid-"))[0]

    var vorteil = getClass(e.currentTarget, "teil") === "teil-vor"
    var data = vorteil ? vorteil_data : nachteil_data

    // mirror changed notizen to form data
    if (Object.keys(data).indexOf(id) >= 0) {
        data[id]["notizen"] = e.currentTarget.value
    }
}

function submit() {
    post({vorteile: vorteil_data, nachteile: nachteil_data})
}
