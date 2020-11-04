document.addEventListener("DOMContentLoaded", () => {

    document.getElementById("search").addEventListener("keydown", (e) => {
        // on keydown of enter, i.e. ascii-code 13
        if (e.keyCode === 13) {
            document.getElementById("search_btn").click();
        }
    });

    document.getElementById("search_btn").addEventListener("click", () => {

        post({"search_text": document.getElementById("search").value},
            (data) => {
                var results_tag = document.getElementById("search-results")
                results_tag.innerHTML = null

                var results = data["item_list"];
                if (results.length === 0) {
                    results_tag.innerHTML += "<p>Keine Ergebnisse gefunden</p>"
                } else {
                    for (var i = 0; i < results.length; i++) {
                        results_tag.innerHTML +=
                            "<p><a href='" + results[i]["url"] + "'>" + results[i]["name"] + "</a></p>"
                    }
                }
            }
        )
    })
})
