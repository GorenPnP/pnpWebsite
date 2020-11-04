// init ap_pool at beginning
init = true
var initial_fp = 0
var initial_fg = 0
var fp_dict = {}
var fg_dict = {}

// get class of row
function getClass(tag, prefix="row") {

    var classes = tag.classList
    for (var c = 0; c < classes.length; c++) {
        if (classes[c].startsWith(prefix)) return classes[c];
    }
    return null
}

document.addEventListener("DOMContentLoaded", function () {
    fp_pool_tag = document.getElementById("fp_pool")
    fg_pool_tag = document.getElementById("fg_pool")
    submit_btn = document.getElementById("submit")

    initial_fp = parseInt(fp_pool_tag.innerHTML);
    initial_fg = parseInt(fg_pool_tag.innerHTML);

    calc_fp_pool();
    calc_fg_pool();

    // gathering data for initial_ap is done
    init = false
});

function calc_fp_pool() {

    var sum = 0;

    // go through all ENTRIES in table
    var tag_list = document.getElementsByClassName("fp");
    for (var i = 0; i < tag_list.length; i++) {

        // get class of row
        var row_class = getClass(tag_list[i], "row")

        // neuberechnung fp_pool

        // get fp
        var fp_tag = document.getElementsByClassName("fp " + row_class)[0];
        var fp_val = parseInt(fp_tag.value);
        var max = parseInt(fp_tag.max);
        if ( fp_val > max ) {
            fp_tag.value = max;
            fp_val = max;
        }
        sum += fp_val;


        // get attr_val of attrs
        var attrs = document.getElementsByClassName("attr__val " + row_class);

        var attr_val = 0;
        for (var j = 0; j < attrs.length; j++) {
            attr_val += parseInt(attrs[j].innerHTML);
        }

        // get fp bonus
        var bonus_tags = document.getElementsByClassName("bonus " + row_class)
        var fp_bonus_val = bonus_tags.length ? parseInt(bonus_tags[0].innerHTML) : 0

        // get fg
        var fg_val = 0;
        if (attrs.length === 1) {
            var attr_id = fp_tag.dataset.attr
            var fg_tag = document.getElementsByClassName("fg attr" + attr_id)[0]
            fg_val = parseInt(fg_tag.value);
        }

        // fg_bonus
        var fg_bonus_tags = document.getElementsByClassName("fg_bonus attr" + attr_id)
        var fg_bonus_val = fg_bonus_tags.length ? parseInt(fg_bonus_tags[0].innerHTML) : 0

        // update fert-pool
        document.getElementsByClassName("pool " + row_class)[0].innerHTML = attr_val + fp_val + fg_val + fp_bonus_val + fg_bonus_val;

        // setup data for form
        var fert_tag = document.getElementsByClassName("fert " + row_class)[0]
        var fert_class = getClass(fert_tag, "fert-id-")
        var fert = /\d+/.exec(fert_class)

        fp_dict[fert] = fp_val;
    }

    var curr_fp = initial_fp - sum;
    if (!init) {
        fp_pool_tag.innerHTML = curr_fp;
    } else {
        initial_fp += sum;
    }

    // handle submit button
    submit_btn.disabled = curr_fp !== 0 || parseInt(fg_pool_tag.innerHTML) !== 0
}


function calc_fg_pool() {

     var sum = 0;

    // go through all ENTRIES in table
    var tag_list = document.getElementsByClassName("fg");
    for (var i = 0; i < tag_list.length; i++) {
        var row_class = getClass(tag_list[i], "row")

        // fg_pool
        var fg_val = parseInt(tag_list[i].value)
        sum += fg_val;

        // fg_bonus
        var attr_class = getClass(tag_list[i], "attr")
        var attr = /\d+/.exec(attr_class)

        var fg_bonus_tag = document.getElementsByClassName("fg_bonus attr" + attr)
        var fg_bonus_val  = fg_bonus_tag.length ? parseInt(fg_bonus_tag[0].innerHTML) : 0

        // neuberechnung attr_val
        var attr_tag = document.getElementsByClassName("attr " + row_class)[0]
        var attr_val = parseInt(document.getElementsByClassName("attr__val " + row_class)[0].innerHTML)


        // find all with same fg_pool
        var attr_class = getClass(attr_tag, "attribute")
        var same_attr = document.getElementsByClassName(attr_class);

        for (var j = 0; j < same_attr.length; j++) {
            var row_class = getClass(same_attr[j], "row")

            // get fp_val
            var fp_val = parseInt(document.getElementsByClassName("fp " + row_class)[0].value);

            // get fp bonus
            var bonus_tags = document.getElementsByClassName("bonus " + row_class)
            var fp_bonus_val = bonus_tags.length ? parseInt(bonus_tags[0].innerHTML) : 0

            // assign pool without fg, comes right after
            document.getElementsByClassName("pool " + row_class)[0].innerHTML = attr_val + fg_val + fp_val + fp_bonus_val + fg_bonus_val;
        }

        // setup data for form
        fg_dict[attr] = fg_val;

    }

    if (!init) {
        var curr_fg = initial_fg - sum;
        fg_pool_tag.innerHTML = curr_fg;
    } else {
        initial_fg += sum;
    }

    // handle submit button
    submit_btn.disabled = curr_fg !== 0 || parseInt(fp_pool_tag.innerHTML) !== 0
}

function submit() {
    post({fp_dict, fg_dict})
}
