function init_current_story() {
    const container = document.querySelector(".aside--story");

    // mana
    const mana_tag = container.querySelector("#id_mana");
    const max_mana = [...document.querySelectorAll("section#values tbody tr")].reduce((acc, tr) => {
        const [label, value] = tr.querySelectorAll("td");
        return label.innerText === "Manaoverflow" ? parseInt(value.innerText) : acc;
    }, null);

    mana_text = mana_tag.parentElement.querySelector(".input-group-text");
    mana_text.innerHTML = mana_text.innerHTML.replace("xxx", max_mana);
    if (isNaN(parseInt(mana_tag.value))) mana_tag.value = max_mana;
    
    // konz
    const konz_tag = container.querySelector("#id_konz");
    if (isNaN(parseInt(konz_tag.value))) konz_tag.value = parseInt(konz_tag.parentElement.querySelector(".input-group-text").innerHTML.replace(/\D/gi, ""));

    // gHP
    const [kHP_table, gHP_table] = document.querySelectorAll("section#hp tbody");

    const gHP_tag = container.querySelector("#id_gHP");
    const max_gHP = parseInt(gHP_table.querySelector("tr:last-of-type td:last-of-type").innerHTML.replace(/\D/gi, ""));
    gHP_text = gHP_tag.parentElement.querySelector(".input-group-text");
    gHP_text.innerHTML = gHP_text.innerHTML.replace("xxx", max_gHP);
    if (isNaN(parseInt(gHP_tag.value))) gHP_tag.value = max_gHP;

    // kHP
    const kHP_tag = container.querySelector("#id_kHP");
    const max_kHP = parseInt(kHP_table.querySelector("tr:last-of-type td:last-of-type").innerHTML.replace(/\D/gi, ""));
    kHP_text = kHP_tag.parentElement.querySelector(".input-group-text");
    kHP_text.innerHTML = kHP_text.innerHTML.replace("xxx", max_kHP);
    if (isNaN(parseInt(kHP_tag.value))) kHP_tag.value = max_kHP;
}

init_current_story();

// init MD-Editors
const element = document.querySelector(".aside--story .story-note-form textarea");

let initialValue = element.value?.trim() || "";
try {
    initialValue = JSON.parse(initialValue)["text"] || " ";
} catch {};

const notes_editor = new EasyMDE({
    ...MDEditorConfig,
    element,
    initialValue
});


// wait for events
document.querySelector(".aside--story .story-note-form").addEventListener("input", function() {
    axios.post(this.action, new FormData(this));
});
document.querySelector(".aside--story .story-note-form").addEventListener("reset", function(e) {
    e.preventDefault();

    notes_editor.value("");
    this.querySelectorAll("input:not([type=hidden])").forEach(tag => tag.value = null);
    
    init_current_story();
    axios.post(this.action, new FormData(this));
});