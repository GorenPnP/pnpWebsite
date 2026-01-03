const spieler_einheiten: {[spieler_pk: number | string]: number[]} = JSON.parse(document.querySelector("#spieler_einheiten")!.innerHTML);
document.querySelector<HTMLSelectElement>("#spieler-select")!.addEventListener("change", function() {
    
    // rm all checks
    [...document.querySelectorAll<HTMLInputElement>("#einheiten_list input[type='checkbox']")].forEach(checkbox => {
        checkbox.checked = false;
        // checkbox.disabled = false;
        // checkbox.closest(".list-group-item").classList.remove("disabled");
    });
    
    // check all accessable einheiten
    (spieler_einheiten[this.value] || [])
        .map((einheit_id: number) => document.querySelector<HTMLInputElement>(`#einheiten_list input[type='checkbox']#einheit-${einheit_id}`))
        .filter((checkbox: any) => checkbox)
        .forEach(checkbox => {
            checkbox!.checked = true;
            // checkbox.disabled = true;
            // checkbox.closest(".list-group-item").classList.add("disabled");
        })
});

document.querySelector<HTMLFormElement>("#form")!.addEventListener("submit", function() {
    this.einheiten.value = JSON.stringify(
        [...document.querySelectorAll(`#einheiten_list [type=checkbox]:checked`)].map(checkbox => parseInt(checkbox.id.split("-")[1]))
    );
});