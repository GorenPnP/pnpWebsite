$(document).ready(function () {
    $("#spieler_dropdown").select2({
        placeholder: "Wähle hier einen Spieler",
        tags: true,
        createTag: function (params) {return null},
        maximumInputLength: 50,
        maximumSelectionLength: 1,
        width: "50%",
        language: "de"
    });

    $("#char_dropdown").select2({
        placeholder: "Wähle hier einen Charakter",
        tags: true,
        createTag: function (params) {return null},
        maximumInputLength: 50,
        maximumSelectionLength: 1,
        width: "50%",
        language: "de"
    });

    $("#spieler_dropdown").change(function () {
        $("#char_dropdown").empty();

        var chosen = $("#spieler_dropdown").select2("data");
        if (chosen.length === 0) {
            $("#char_div").hide();
            $(".apps").hide();
            return;
        }
        $("#char_div").show();
        $("#char_dropdown").addClass("select2-container--focus");
        $("#spieler_dropdown").removeClass("select2-container--focus");

        $.ajax({
            type: 'POST',
            data: {"spieler_id": chosen[0].id, "topic": "choose_spieler"},
            success: function (data) {
                // dropdown of all spieler's chars

                var dropdown = $("#char_dropdown");
                for (var i = 0; i < data["chars"].length; i++) {
                    var char = data["chars"][i];

                    dropdown.append($("<option></option>").text(char["name"]).addClass("spieler_id").prop("value", char["id"]));
                }
            },
            error: function (data) {
                alert("Fehler: " + data["responseJSON"]["message"]);
            }
        });
    });

    $("#char_dropdown").change(function () {
        var chosen = $("#char_dropdown").select2("data");
        if (chosen.length === 0) {
            $(".apps").hide();
        } else {
            $(".apps").show();
        }

    });

    $("#for_sp").find(".send").click(function() {
        var chosen_id = $("#char_dropdown").select2("data");
        if (chosen_id.length === 0) {
            return;
        }
        var num = parseInt($("#for_sp").find(".num").val());

        $.ajax({
            type: 'POST',
            data: {"char_id": chosen_id[0].id, "num": num, "topic": "for_sp"},
            success: function (data) {
                //location.href = data["url"];
                alert(data["response"]);
            },
            error: function (data) {
                alert("Fehler: " + data["responseJSON"]["message"]);
            }
        });
    });

    $("#char_div").hide();
    $(".apps").hide();
});

