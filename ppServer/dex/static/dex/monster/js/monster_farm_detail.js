const max_trained_amount = parseInt(JSON.parse(document.querySelector("#max_trained_amount").innerHTML));
let trained_amount;

const text_stop = "Monster nicht mehr auf diesen Stat trainieren";
const text_start = "Monster auf diesen Stat trainieren";

function draw() {
    document.querySelectorAll(".stats-container .booble-container").forEach(btn => {
        btn.setAttribute("aria-description", btn.classList.contains("trained") ? text_stop : text_start);
        btn.setAttribute("title", btn.classList.contains("trained") ? text_stop : text_start);
    });

    // set rang increase btn
    trained_amount = document.querySelectorAll(".stats-container .booble-container.trained").length;
    document.querySelector("#training_save_btn").disabled = max_trained_amount != trained_amount;
    document.querySelector("#open_training").innerHTML = max_trained_amount - trained_amount + "x"
    
    // set input
    document.querySelector("#stat_input").value = [...document.querySelectorAll(".stats-container .booble-container.trained")].map(tag => tag.dataset.stat).join(" ");
    
}


// toggle trained
document.querySelectorAll(".stats-container .booble-container").forEach(btn => btn.addEventListener("click", function(e) {
    this.classList.toggle("trained");
    draw();
}));

draw();
document.querySelector("#rang_increase_btn").disabled = max_trained_amount != trained_amount;
document.querySelector("#rang_increase_btn").setAttribute("aria-description", max_trained_amount == trained_amount ? "Rang um 1 erhöhen" : "Du musst erst trainieren, bevor dein Monster den Rang erhöhen kann!");
document.querySelector("#rang_increase_btn").parentElement.title = max_trained_amount == trained_amount ? "Rang um 1 erhöhen" : "Du musst erst trainieren, bevor dein Monster den Rang erhöhen kann!";