/************ handle form-incompatibilities with LARP *******************/

document.querySelector("#larp").addEventListener("input", function() {
    const stufe = document.querySelector("#stufe");
    stufe.disabled = this.checked;
    stufe.closest(".form-field").style.display = this.checked ? "none" : "block";
    document.querySelector("#fieldset-klassen").style.display = this.checked ? "none" : "block";
    if (this.checked) { stufe.value = 1; }

    update_stufen();
});

document.querySelector("#stufe").addEventListener("input", function() {
    const value = parseInt(this.value || 0);
    const larp = document.querySelector("#larp");
    larp.disabled = value !== 1;
    if (value) { larp.checked = false; }

    update_stufen();
});

/************ handle klassen *******************/

function update_stufen() {
    const char_stufe = parseInt(document.querySelector("#stufe").value);
    const klasse_stufe_sum = [...document.querySelectorAll(".stufe-input")].reduce((sum, input) => sum + parseInt(input.value), 0);

    let text = "";
    const is_larp = !!document.querySelector("#larp:checked");
    if (!is_larp && char_stufe < klasse_stufe_sum) text = `${klasse_stufe_sum - char_stufe} Stufe${Math.abs(char_stufe - klasse_stufe_sum) !== 1 ? 'n': ''} zu viel in Klassen verteilt`;
    if (!is_larp && char_stufe > klasse_stufe_sum) text = `${char_stufe - klasse_stufe_sum} Stufe${Math.abs(char_stufe - klasse_stufe_sum) !== 1 ? 'n': ''} zu wenig in Klassen verteilt`;
    document.querySelector("#stufen-errortext").innerText = text;
    document.querySelectorAll("#create-char-form, #submit-char-btn").forEach(tag => tag.disabled = !!text);
}

// select new klasse
document.querySelector("#choose-klasse-btn").addEventListener("click", function() {
    // gather data
    const select = document.querySelector("#new-klasse-select");
    const klasse = {
        id: select.value,
        titel: select.options[select.selectedIndex].text,
    };
    if (!klasse.id) { return; }

    // update select
    select.options[select.selectedIndex].disabled = true;;
    select.options[0].selected = true;

    // add entry for Klassenstufe
    const target_container = document.createElement("div");
    target_container.innerHTML = 
    `<div class="input-group flex-nowrap klasse-stufe-field">
        <a class="input-group-text klasse-titel" href="/wiki/klassen/${klasse.id}" data-id="${klasse.id}">${klasse.titel}</a>
        <span class="input-group-text">Stufe</span>
        <input type="number" class="form-control stufe-input" name="klasse-${klasse.id}" min="1" max="30" value="1">
        <button class="btn btn-danger klasse-delete-btn" type="button" aria-label="löschen">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3" viewBox="0 0 16 16">
                <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5M11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47M8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5"/>
            </svg>
        </button>
    </div>`;

    document.querySelector("#klassen-container").appendChild(target_container.firstChild);
    target_container.remove();
    update_stufen();
});

// delete klasse
document.querySelector("#klassen-container").addEventListener("click", function(e) {
    // check if delete button pressed
    const delete_btn = e.target.classList.contains("klasse-delete-btn") ? e.target : e.target.closest("button.klasse-delete-btn");
    if (!delete_btn) { return; }
    const field = delete_btn.closest(".klasse-stufe-field");


    // update select of new Klasse
    const klasse_id = field.querySelector(".klasse-titel").dataset.id;
    document.querySelector(`#new-klasse-select option[value='${klasse_id}']`).disabled = false;

    // delete field / update stufen
    field.remove();
    update_stufen();
});

// change stufe
document.querySelector("#klassen-container").addEventListener("input", function(e) {
    // check if stufe input changed
    const input = e.target;
    if (!input.classList.contains("stufe-input")) { return; }

    update_stufen();
});


update_stufen();