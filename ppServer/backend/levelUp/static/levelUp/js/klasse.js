document.querySelectorAll("[name='stufenplan_id']").forEach(radio_input => radio_input.addEventListener("change", function() {
    const learn_btn = document.querySelector("#choose-stufe");
    if (learn_btn) { learn_btn.disabled = !document.querySelectorAll("form input[name='stufenplan_id']:checked").length; }
}));