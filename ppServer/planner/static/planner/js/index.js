const non_bookable_states = ["full", "blocked", "cancelled", "takes-place"];

function format_time(iso_time) {
    return iso_time.slice(0, -3)
}

function is_bookable(iso_date, username, days_by_iso) {
    day = days_by_iso[iso_date];
    if (!day) { return true; }

    return !non_bookable_states.includes(day.status) && !day.proposals.includes(username);
}

function update_appointment(iso_date, days_by_iso) {
    const day = days_by_iso[iso_date];

    if (!day?.appointment) {
        return document.querySelector("#appointment-section").style.display = "none";
    }
    document.querySelector("#appointment-section").innerHTML = `<h2>${day.appointment.title}</h2><p>${day.appointment.tags} startet um ${format_time(day.appointment.start)}</p>`;
    document.querySelector("#appointment-section").style.display = "block";
    
}

function update_proposals(iso_date, days_by_iso) {
    const proposals = (days_by_iso[iso_date]?.proposals || [])
    document.querySelector("#participants").innerHTML = proposals.map(player => `<li>${player}</li>`).join("");
    document.querySelector("#participant-section").style.display = proposals.length ? "block": "none";
}

function update_form(iso_date) {
    document.querySelector("#id_date").value = iso_date;
    document.querySelector(".long_date").innerHTML = new Date(iso_date).toLocaleDateString();
}

function update_blocked(iso_date, days_by_iso) {
    const blocked = days_by_iso[iso_date]?.blocked_time;
    document.querySelector("#blocked-section").style.display = blocked ? "block" : "none";
    document.querySelector("#blocked-section").innerHTML = blocked ? `<p>Termin ist von <b>${format_time(blocked.start)} bis ${format_time(blocked.end)} blockiert</b>.</p>` : "";
}



document.addEventListener("DOMContentLoaded", function () {

    // prepare vals
    const username = JSON.parse(document.querySelector("#username").innerHTML);
    const days = JSON.parse(document.querySelector("#days").innerHTML) || [];
    const days_by_iso = days.reduce((acc, day) => {
        acc[day.date] = day;
        return acc;
    }, {});

    const day_tags = [...document.querySelectorAll(".day")];

    // add classes of states
    days.forEach(day => document.querySelector(`[data-date="${day.date}"]`).classList.add(day.status));

    const unbookable_days = day_tags.filter(day_tag => !is_bookable(day_tag.dataset.date, username, days_by_iso));
    const bookable_days = day_tags.filter(day_tag => is_bookable(day_tag.dataset.date, username, days_by_iso));

    // toggle visibilities
    bookable_days.forEach(date => date.addEventListener("click", () => update_form(date.dataset.date)))

    unbookable_days.forEach(day => day.addEventListener("click", () => document.querySelector("#participate-form").style.display = "none"))
    bookable_days.forEach(day => day.addEventListener("click", () => document.querySelector("#participate-form").style.display = "block"))

    // update participant list
    day_tags.forEach(day => day.addEventListener("click", () => {
        update_proposals(day.dataset.date, days_by_iso);
        update_appointment(day.dataset.date, days_by_iso);
        update_blocked(day.dataset.date, days_by_iso);
        document.querySelector(".popover").style.display = "block";
    }))


    // select first bookable day
    bookable_days[0].click();
});