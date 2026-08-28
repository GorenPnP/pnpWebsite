// autosave notizen on items on change
document.querySelectorAll("form.item-notizen-form").forEach(form =>
    form.addEventListener("input", function() { axios.post(this.action, new FormData(this)); })
);
