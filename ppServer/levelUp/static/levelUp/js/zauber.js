const max_tier = parseInt(document.querySelector("#max_tier").innerHTML);
const slots_available = parseInt(document.querySelector("#slots_available").innerHTML);
const sp_available = parseInt(document.querySelector("#sp_available").innerHTML);
const ap_available = parseInt(document.querySelector("#ap_available").innerHTML);
const sp_cost_for_tier = JSON.parse(document.querySelector("#sp_cost_for_tier").innerHTML);
const cards = document.querySelectorAll("#update-form .card");


function set_tier(tier, card) {
    const min_tier = card.querySelectorAll(".tier-bought").length;
    tier = Math.min(max_tier, Math.max(min_tier, tier));
    card.querySelector(".tier-input").value = tier;
}

function update_display(card) {
    const min_tier = card.querySelectorAll(".tier-bought").length;
    const tier = parseInt(card.querySelector(".tier-input").value);

    // update buttons
    card.querySelector(".btn--decrease").disabled = tier === min_tier;
    card.querySelector(".btn--increase").disabled = tier === max_tier;

    card.querySelectorAll(".tier").forEach((t, i) => {
        if (i+1 <= min_tier || i+1 > tier) { t.classList.remove("tier-filled"); }
        else { t.classList.add("tier-filled"); }

    })
}

function update_general() {
    // update create zauber button
    const learn_btn = document.querySelector("#learn-zauber");
    if (learn_btn) { learn_btn.disabled = !!document.querySelectorAll(".tier-filled").length; }

    // update number display in resources & disabled of #learn-tier btn
    document.querySelectorAll(".pay-tier").forEach(tag => tag.innerHTML = "");
    
    const amount_tiers_chosen = document.querySelectorAll(".tier-filled").length;
    let submittable = false;
    switch (document.querySelector("#payment-method").value) {
        case "sp": 
            let sp = 0
            cards.forEach(card => {
                const bought = card.querySelectorAll(".tier-bought").length;
                let will_buy = card.querySelectorAll(".tier-filled").length;
                while (will_buy > 0) {
                    sp += sp_cost_for_tier[bought+will_buy--];
                }
            });
            document.querySelector("#pay-tier-with-sp").innerHTML = sp ? ` (-${sp})` : '';
            submittable = sp <= sp_available;
            break;
        case "slot":
            document.querySelector("#pay-tier-with-slots").innerHTML = amount_tiers_chosen ? ` (-${amount_tiers_chosen})` : '';
            submittable = amount_tiers_chosen <= slots_available;
            break;
        case "ap":
            document.querySelector("#pay-tier-with-ap").innerHTML = amount_tiers_chosen ? ` (-${amount_tiers_chosen})` : '';
            submittable = amount_tiers_chosen <= ap_available;
            break;
    }
    document.querySelector("#learn-tier").disabled = !submittable;
}



document.querySelectorAll(".btn--decrease").forEach(btn => btn.addEventListener("click", function() {
    const card = this.closest(".card");
    const tier = parseInt(card.querySelector(".tier-input").value) -1;
    set_tier(tier, card);
    update_display(card);
    update_general();
}));
document.querySelectorAll(".btn--increase").forEach(btn => btn.addEventListener("click", function() {
    const card = this.closest(".card");
    const tier = parseInt(card.querySelector(".tier-input").value) +1;
    set_tier(tier, card);
    update_display(card);
    update_general();
}));
document.querySelector("#payment-method")?.addEventListener("change", function() {
    update_general();
});

document.querySelector("[name='zauber_id']")?.addEventListener("change", function() {
    const price = this.selectedIndex ? parseInt(this.options[this.selectedIndex].dataset.money) : 0;
    const formatted_price = price.toLocaleString("de-DE")

    if (document.querySelector("#pay-money")) {
        document.querySelector("#pay-money").innerHTML = price ? ` (-${formatted_price})` : "";
    }
});