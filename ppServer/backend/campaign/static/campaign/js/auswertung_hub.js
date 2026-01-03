const STORAGE_KEY = "auswertung_hub:selected_chars";
let selected_characters = [];


function set_display() {
    const list = document.querySelector("#selected-chars");

    if (selected_characters.length) {
        list.innerHTML = selected_characters.map(char => `<li><a href="${location.href.replace(/\/+$/, '')}/${char.id}/" class="text-light">${char.label}</a></li>`).join("");
    } else {
        list.innerHTML = "<small>keine Charaktere gewählt</small>";
    }
}

document.addEventListener("DOMContentLoaded", function() {
    document.querySelector("#offcanvasExampleLabel").innerHTML = "aktuelle Charaktere";

    // load selected chars from storage
    selected_characters = JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];

    const removed_chars = []
    selected_characters.forEach(selected_char => {
        const box = document.querySelector(`#char-${selected_char.id}`)
        if (box) box.checked = true;
        else removed_chars.push(selected_char)
    });
    selected_characters = selected_characters.filter(char => !removed_chars.includes(char));

    set_display();

    // listen for changes
    document.querySelectorAll("[type='checkbox']").forEach(input => input.addEventListener("change", function() {
        
        // select
        if (this.checked) {
            selected_characters.push({
                id: parseInt(this.name),
                label: document.querySelector(`label[for=char-${this.name}]`).innerHTML
            })
            selected_characters = selected_characters.sort((a, b) => a.label < b.label ? -1 : 1);
        }

        // unselect
        else { selected_characters = selected_characters.filter(char => char.id != this.name); }

        // save to storage
        localStorage.setItem(STORAGE_KEY, JSON.stringify(selected_characters));
        set_display();
    }));

    // filter chars
    document.querySelector("#char-filter").addEventListener("input", function() {
        const search = this.value.toLowerCase();
        console.log(search)

        document.querySelectorAll(".all-chars li").forEach(li => {
            const hidden = search && !li.querySelector("label b").innerHTML.toLowerCase().includes(search);
            if (hidden) li.classList.add("hidden");
            else li.classList.remove("hidden");
        });
    });
});