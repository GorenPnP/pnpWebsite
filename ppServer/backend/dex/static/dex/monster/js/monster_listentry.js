// prevent navigation on opening of fullscreen-image modal
document.querySelectorAll(".monster").forEach(mon => mon.addEventListener("click", function(e) {
    if (e.target.tagName === "IMG" || e.target.classList.contains("open-modal-btn")) {
        e.preventDefault();
    }
}));