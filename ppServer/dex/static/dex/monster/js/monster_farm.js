document.querySelectorAll(".del-btn--monster").forEach(btn => btn.addEventListener("click", function() {
    document.querySelector("[name=monster_id]").value = parseInt(this.dataset.monster);
    document.querySelector("#monster_name").innerHTML = this.closest(".del-btn-container").querySelector(".monster__name").innerHTML;
}));