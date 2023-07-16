function init_zauberslots() {
    const p = document.querySelector(".zauberplätze-input").closest("p");

    const label = p.querySelector("label");

    // label -> legend
    const legend = document.createElement("legend");
    legend.innerHTML = label.innerHTML;
    label.replaceWith(legend);

    // p -> fieldset
    const fieldset = document.createElement("fieldset");
    fieldset.innerHTML = p.innerHTML;
    p.replaceWith(fieldset);

    // add labels
    document.querySelectorAll(".zauberplätze-input").forEach(input => {
        const label = document.createElement("label");
        label.setAttribute("for", input.id);
        label.innerHTML = `Stufe ${parseInt(input.id.match(/\d+/))}:`;

        input.parentNode.insertBefore(label, input);
    });
}

document.addEventListener("DOMContentLoaded", function() {
    document.querySelector("#offcanvasExampleLabel").innerHTML = "aktuelle Werte";

    if (document.querySelector(".zauberplätze-input")) { init_zauberslots(); }
});