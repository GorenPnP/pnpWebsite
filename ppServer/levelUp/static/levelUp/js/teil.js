const accordion = document.querySelector(".accordion");
const is_vorteil = JSON.parse(document.querySelector("#is_vorteil").innerHTML);
    
accordion.addEventListener("click", (e) => {

    const addCheck = e.target.closest(".add-checkbox");
    if (addCheck) { return toggleAdd(addCheck); }

    const delBtn = e.target.closest(".del-btn");
    if (delBtn) { return toggleDelete(delBtn); }

    // don't toggle accordion on click in expanded content (only on .head)
    const content = e.target.closest(".accordion-content");
    if (content) { return; }

    const activePanel = e.target.closest(".accordion-panel");
    if (activePanel) return toggleAccordion(activePanel);
    
});


/************* ACCORDION ANIMATION **************/

function toggleAccordion(panelToActivate) {
    const activeButton = panelToActivate.querySelector("button");
    const activePanelIsOpened = activeButton.getAttribute("aria-expanded");

    if (activePanelIsOpened === "true") {
        panelToActivate
            .querySelector("button")
            .setAttribute("aria-expanded", false);
    
        panelToActivate
            .querySelector(".accordion-content")
            .setAttribute("aria-hidden", true);
    } else {
        panelToActivate.querySelector("button").setAttribute("aria-expanded", true);
    
        panelToActivate
            .querySelector(".accordion-content")
            .setAttribute("aria-hidden", false);
    }
}




/************ LOGIC *************/

function toggleAdd(addCheck) {
    
    // update teil highlight
    update_highlight(addCheck);
    
    // update card
    const add_card = addCheck.closest(".card");
    add_card.querySelectorAll("[data-required=true]").forEach(input => input.required = addCheck.checked);

    // update general IP
    update_ip(get_ip(addCheck) * (addCheck.checked ? -1 : 1));
}

function toggleDelete(deleteBtn) {
    const card = deleteBtn.closest(".card");
    card.classList.toggle("deleted");
    
    const checkbox = card.querySelector(`[name=${deleteBtn.dataset.delete}]`);
    const was_deleted = JSON.parse(checkbox.value || "false");
    checkbox.value = was_deleted ? null : 'true';

    update_highlight(deleteBtn);
    update_ip(get_ip(deleteBtn) * (was_deleted ? -1 : 1));
}


// update display of field validity
document.querySelector("form").onclick = function() {
    const form = document.querySelector("form");

    // reset invalidity
    form.querySelectorAll(".invalid").forEach(tag => tag.classList.remove("invalid"));

    if (!form.checkValidity()) {
        const invalid_inputs = [...form.querySelectorAll(":invalid")];
        invalid_inputs.map(i => form.querySelector(`[for=${i.id}]`).classList.add("invalid"))

        // invalid cards
        new Set(invalid_inputs.map(tag => tag.closest(".card")))
            .forEach(card => card.classList.add("invalid"));

        // invalid teils
        new Set(invalid_inputs.map(tag => tag.closest(".accordion-panel")))
            .forEach(teil => teil.classList.add("invalid"));
            
        // open accordion
        form.querySelectorAll(".accordion-panel.invalid .accordion-trigger[aria-expanded=false]")
            .forEach(trigger => !trigger.ariaExpanded && trigger.click());

    }
}



/************ LOGIC HELPERS *************/

function get_ip(element_in_card) {
    const card = element_in_card.closest(".card");
    const card_container = element_in_card.closest(".accordion-panel");

    return parseInt(card.querySelector(".input-field .ip")?.value) ||
           parseInt(card_container.querySelector(".head .ip")?.innerHTML) || 0;
}

function update_ip(diff) {
    const ip_pool = document.querySelector("#ip_pool");

    if (!is_vorteil) { diff *= -1; }
    ip_pool.innerHTML = parseInt(ip_pool.innerHTML) + diff;
}


function update_highlight(element_in_teil) {
    const card_container = element_in_teil.closest(".accordion-panel");
    const has_existing_teil = card_container.querySelectorAll(".card:not(.card--add):not(.deleted)").length;
    const has_new_teil = card_container.querySelector(".add-checkbox")?.checked;
    
    card_container.classList.remove("text-bg-primary", "text-bg-dark")
    const style_class = has_existing_teil || has_new_teil ? "text-bg-primary" : "text-bg-dark";
    card_container.classList.add(style_class);
}
