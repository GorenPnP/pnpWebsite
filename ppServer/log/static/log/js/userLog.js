$(document).ready(function () {
    $("#char_dropdown").change(handle_all_filters);
    $("#spieler_dropdown").change(handle_all_filters);
    $("#kategorie_dropdown").change(handle_all_filters);

    $("#char_dropdown").select2({
        placeholder: "Filter nach Charakter",
        tags: true,
        createTag: function (params) {return null},
        maximumInputLength: 50,
        width: "100%",
        language: "de"
    });
    $("#spieler_dropdown").select2({
        placeholder: "Filter nach Spieler",
        tags: true,
        createTag: function (params) {return null},
        maximumInputLength: 50,
        width: "100%",
        language: "de"
    });
    $("#kategorie_dropdown").select2({
        placeholder: "Filter nach Kategorie",
        tags: true,
        createTag: function (params) {return null},
        maximumInputLength: 50,
        width: "100%",
        language: "de"
    });
});

function handle_all_filters(e) {
    var all_selected = $(e["currentTarget"]).find("option:selected[value=all]");
    if (all_selected.length > 0) {
        var unselect = $(e["currentTarget"]).find("option:selected").not("[value=all]");
        for (var i = 0; i < unselect.length; i++) {
            unselect[i].selected = false;
            $("#note_all_selected").attr("style", "display:inherit");
            $("#note_all_selected").fadeOut(5000);
        }
    }


    var ids = get_ids_from_select($("#char_dropdown"));
    handle_hidden(ids, ".char", "c");

    ids = get_ids_from_select($("#spieler_dropdown"));
    handle_hidden(ids, ".spieler", "s");

    ids = get_ids_from_select($("#kategorie_dropdown"), false);
    handle_hidden(ids, ".kategorie", "k", false);
}

function get_ids_from_select(select_tag, int_bool=true) {
    var selected = $(select_tag).find("option:selected");
    var all = false;
    var ids = [];
    for (var i = 0; i < selected.length; i++) {
        var option_tag = $(selected[i]);
        if (option_tag.val() === "all") {
            all = true;
            break;
        }
        var val = option_tag.val();
        ids.push(int_bool? parseInt(val) : val);
    }
    if (all) {
        ids = [];
        var all_options = $(select_tag).find("option");
        for (var i = 0; i < all_options.length; i++) {
            if ($(all_options[i]).val() === "all") {continue;}
            var val = $(all_options[i]).val();
            ids.push(int_bool? parseInt(val) : val);
        }
    }
    return ids;
}

function handle_hidden(ids, selector, filter_char, int_bool=true) {
    var log_tr = $("tr").not(".sticky-top");
    for (var i = 0; i < log_tr.length; i++) {
        var char_td = $(log_tr[i]).find(selector);
        var char_tr = char_td.parent();
        var char_id = null;
        if (int_bool) {
            char_id = parseInt(/\d+/.exec(char_td.attr("class")));
        } else {
            var char_classes = char_td.attr("class").split(" ");
            for (var j = 0; j < char_classes.length; j++) {
                if (char_classes[j].length === 1) {
                    char_id = char_classes[j];
                    break;
                }
            }
        }
        var active_filters = char_tr.attr("data-active-filters");

        // found char_id in data-active-filters
        if ($.inArray(char_id, ids) !== -1) {
            if ($.inArray(filter_char, active_filters.split("")) === -1) {
                char_tr.attr("data-active-filters", active_filters+filter_char);
            }
        // did not find char_id
        } else {
            if ($.inArray(filter_char, active_filters.split("")) !== -1) {
                char_tr.attr("data-active-filters", active_filters.replace(filter_char, ""));
            }
        }
        char_tr.attr("hidden", char_td.parent().attr("data-active-filters").length !== 3);
    }
}