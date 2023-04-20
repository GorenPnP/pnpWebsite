let initial_ip = 0;


function ip_spent() {
    const spent = [...document.querySelectorAll("#vorteil-table .anzahl-input")]
        .map(anz_input => ({anz_input, ip_tag: document.querySelector(`#vorteil-table .ip[data-id="${anz_input.dataset.id}"]`)}))
        .map(({anz_input, ip_tag}) => (parseInt(anz_input.value) || 0) * (parseInt(ip_tag.innerHTML) || 0))
        .reduce((sum, ip) => sum + ip, 0);

    const gained = [...document.querySelectorAll("#nachteil-table .anzahl-input")]
        .map(anz_input => ({anz_input, ip_tag: document.querySelector(`#nachteil-table .ip[data-id="${anz_input.dataset.id}"]`)}))
        .map(({anz_input, ip_tag}) => (parseInt(anz_input.value) || 0) * (parseInt(ip_tag.innerHTML) || 0))
        .reduce((sum, ip) => sum + ip, 0);

    return spent - gained;
}

function calc_ip_pool() {
    const ip = initial_ip - ip_spent();
    document.querySelector("#ip_pool").innerHTML = ip;

    document.querySelector('[type="submit"]').disabled = ip < 0;
}

function highlight_rows() {
    const highlight_class = "highlight";

    [...document.querySelectorAll(".main-container tbody tr")].forEach(tr_tag => {
        const is_selected = parseInt(tr_tag.querySelector(".anzahl-input").value);
        is_selected ? tr_tag.classList.add(highlight_class) : tr_tag.classList.remove(highlight_class);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    // init
    initial_ip = parseInt(document.querySelector("#ip_pool").innerHTML) + ip_spent();
    highlight_rows();

    // listen for changes
    document.querySelectorAll(".anzahl-input").forEach(anz_input => anz_input.addEventListener("input", function() {
        calc_ip_pool();
        highlight_rows();
    }));
});
