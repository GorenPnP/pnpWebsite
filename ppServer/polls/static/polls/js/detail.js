var initial_votes;

function toggle(el) {

    el.classList.toggle("checked")

    var num_checked = document.getElementsByClassName("checkbox checked").length
    var remaning = initial_votes - num_checked
    document.getElementById("votes").innerHTML = remaning
    document.getElementById("plural").style.display = Math.abs(remaning) === 1 ? 'none' : 'inline'

    document.getElementById("submit").disabled = num_checked !== initial_votes
}


document.addEventListener("DOMContentLoaded", () => {
    initial_votes = parseInt(document.getElementById("votes").innerHTML)
    var submit_btn = document.getElementById("submit")

    submit_btn.addEventListener("click", () => {
        if (document.getElementsByClassName("checkbox checked").length === parseInt(document.getElementById("votes").innerHTML)) {
            alert("Nicht die richtige Anzahl ausgewählt");
            return;
        }

        var checked = document.getElementsByClassName("checkbox checked")
        var ids = [...checked].map(tag => { return parseInt(tag.id) });
        post({ ids })
    });
});
