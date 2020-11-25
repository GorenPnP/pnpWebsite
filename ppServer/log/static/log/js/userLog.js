var char_select_tag
var spieler_select_tag
var kategorie_select_tag

var table

/* helper functions */
function get_ids_from_select(select_tag, parseToInt=true) {

    var options = select_tag.getElementsByTagName("option");

    var all_selected = []
    Array.from(options).forEach(option => { if (option.selected && option.value != "all") all_selected.push( parseToInt ? parseInt(option.value) : option.value ) })

    return all_selected
}


/* event handlers */
document.addEventListener("DOMContentLoaded", () => {

    table = document.getElementsByClassName("grid-container")[0]

    char_select_tag = document.getElementById("char_dropdown")
    char_select_tag.addEventListener("change", handle_all_filters);

    spieler_select_tag = document.getElementById("spieler_dropdown")
    spieler_select_tag.addEventListener("change", handle_all_filters);

    kategorie_select_tag = document.getElementById("kategorie_dropdown")
    kategorie_select_tag.addEventListener("change", handle_all_filters);

    handle_all_filters()
});


function handle_all_filters() {
    var char = get_ids_from_select(char_select_tag)
    var spieler = get_ids_from_select(spieler_select_tag)
    var kategorie = get_ids_from_select(kategorie_select_tag, false)

    post({ char, spieler, kategorie }, data => {
        console.log(data.logs)

        table.innerHTML =
            `<div class="heading col1">Charakter</div>
                <div class="heading">Spieler</div>
                <div class="heading">Kategorie</div>
                <div class="heading">Notizen</div>
                <div class="heading">Kosten</div>
                <div class="heading heading--last">Timestamp</div>`

        data.logs.forEach(l => {
            table.innerHTML += `<div class="col1"> ${ l.charname }</div>
                <div>${ l.spielername }</div>
                <div>${ l.kategorie }</div>
                <div>${ l.notizen }</div>
                <div>${ l.kosten }</div>
                <div class="time">${ l.timestamp }</div>`
        })

        if (!data.logs.length)
            table.innerHTML += `<div class="col1" style="grid-column: 1 / -1; text-align: center; padding: 2em 1em;">Keine Ergebnisse</div>`
    })
}
