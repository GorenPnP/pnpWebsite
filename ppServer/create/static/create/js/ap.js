var attrs = {};
initial_ap = 0;
init = true

// get class of row
function getClass(tag, prefix = "row") {

    var classes = tag.classList
    for (var c = 0; c < classes.length; c++) {
        if (classes[c].startsWith(prefix)) return classes[c];
    }
    return null
}

function calc_ap_pool() {

    var sum = 0;

    var tag_list = document.getElementsByClassName("aktuell");
    for (var i = 0; i < tag_list.length; i++) {
        // get class of row to find other entries in that row
        var tag = tag_list[i]
        var row_class = getClass(tag, "row")

        // max starting

        // neuberechnung max
        var max_base = parseInt(document.getElementsByClassName("max_base " + row_class)[0].innerHTML)
        var max_ap_tag = document.getElementsByClassName("max " + row_class)[0].firstChild
        var max_sum_tag = document.getElementsByClassName("max_sum " + row_class)[0]

        var max_ap = parseInt(max_ap_tag.value)
        sum += (2 * max_ap);

        // bonus
        var max_bonus_tags = document.getElementsByClassName("max_bonus " + row_class)
        var max_bonus_val = max_bonus_tags.length ? parseInt(max_bonus_tags[0].innerHTML) : 0

        // neuberechnung aktuell_sum
        var max_sum = max_ap + max_base + max_bonus_val;

        // check with limit
        var limit = max_sum_tag.dataset.limit;
        limit = limit === "" ? Number.MAX_VALUE : parseInt(limit);

        if (limit < max_sum) {
            max_sum -= 1;
            max_sum_tag.innerHTML = max_sum;
            max_ap_tag.value = max_ap - 1;
            sum -= 2;
        }
        max_sum_tag.innerHTML = max_sum;

        // aktuell starting

        // neuberechnung aktuell
        var aktuell_base = parseInt(document.getElementsByClassName("aktuell_base " + row_class)[0].innerHTML)
        var aktuell_ap_tag = document.getElementsByClassName("aktuell " + row_class)[0].firstChild
        var aktuell_sum_tag = document.getElementsByClassName("aktuell_sum " + row_class)[0]

        var aktuell_ap = parseInt(aktuell_ap_tag.value)
        sum += aktuell_ap;

        // neuberechnung aktuell_sum
        var aktuell_sum = aktuell_ap + aktuell_base;

        // check with limit
        var limit = aktuell_sum_tag.dataset.limit;
        if (limit === "") { limit = Number.MAX_VALUE; } else { limit = parseInt(limit) }

        if (limit < aktuell_sum || aktuell_sum > max_sum) {
            aktuell_sum -= 1;
            aktuell_sum_tag.innerHTML = aktuell_sum - 1;
            aktuell_ap_tag.value = aktuell_ap - 1;
            sum -= 1;
        }

        // bonus
        var aktuell_bonus_tags = document.getElementsByClassName("aktuell_bonus " + row_class)
        var aktuell_bonus_val = aktuell_bonus_tags.length ? parseInt(aktuell_bonus_tags[0].innerHTML) : 0

        aktuell_sum_tag.innerHTML = aktuell_sum + aktuell_bonus_val;

        // setup data for form
        var entry = { "aktuell": aktuell_ap, "max": max_ap }

        var attr_tag = document.getElementsByClassName("attr " + row_class)[0]
        var attr_class = getClass(attr_tag, "attr-id-")
        var attr = /\d+/.exec(attr_class)

        attrs[attr] = entry;
    }

    if (!init) {
        var curr_ap = initial_ap - sum;
        ap_pool_tag.innerHTML = curr_ap;
    } else {
        initial_ap += sum
    }
    // handle submit button
    document.getElementById("submit").disabled = curr_ap !== 0
}


function submit() {
    post(attrs)
}

document.addEventListener("DOMContentLoaded", function () {
    ap_pool_tag = document.getElementById("ap_pool");
    initial_ap = parseInt(ap_pool_tag.innerHTML)

    calc_ap_pool()

    // gathering data for initial_ap is done
    init = false
});
