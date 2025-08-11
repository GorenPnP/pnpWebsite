function toDate(str) {
    const d = new Date(str);
    return new Date(d.getTime() + d.getTimezoneOffset()*60000);
}

let categories = [];

document.addEventListener("DOMContentLoaded", () => {
    categories = JSON.parse(document.querySelector("#categories").innerHTML);

    const first_available_date_tag = document.querySelector(".day");
    const last_available_date_tag = [...document.querySelectorAll(".day")].reverse()[0];

    categories.forEach(category => {

        category.intervals.forEach(({start, end}) => {
            const startdate = start.split("T")[0];
            const enddate = end.split("T")[0];

            // not displayable bc. out of bounds
            if (toDate(first_available_date_tag.dataset.date) > toDate(enddate) && toDate(last_available_date_tag.dataset.date) < toDate(startdate)) return;

            // get all days of interval
            [...document.querySelectorAll(".day")]
                .filter(tag => toDate(tag.dataset.date) >= toDate(startdate) && toDate(tag.dataset.date) <= toDate(enddate))
                .forEach(day => {
                    let backgroundContainer = day.querySelector(".category-container");
                    if (!backgroundContainer) {
                        backgroundContainer = document.createElement("DIV");
                        backgroundContainer.classList.add("category-container");
                        day.appendChild(backgroundContainer);
                    }

                    if (!backgroundContainer.querySelector(`[aria-description='${category.name}']`)) {
                        const categoryBackground = document.createElement("div");
                        categoryBackground.style.background = category.color;
                        categoryBackground.classList.add("category");
                        categoryBackground.ariaDescription = category.name;

                        backgroundContainer.appendChild(categoryBackground);
                    }
                });
        })
    })
});


function toggleTag() {
    const active_categories = [...document.querySelectorAll(".category-tag.active")].map(btn => btn.dataset.tag);
    const inactive_categories = [...document.querySelectorAll(".category-tag:not(.active)")].map(btn => btn.dataset.tag);

    if (active_categories.length) document.querySelectorAll(active_categories.map(cat  => `.category-container .category[aria-description='${cat}']`).join(", ")).forEach(cat_tag => cat_tag.style.display = "block");
    if (inactive_categories.length) document.querySelectorAll(inactive_categories.map(cat  => `.category-container .category[aria-description='${cat}']`).join(", ")).forEach(cat_tag => cat_tag.style.display = "none");
}

function date_clicked(day_tag, date) {
    const categorynames = [...day_tag.querySelectorAll(".category")].map(tag => tag.ariaDescription);

    const appointments = [];
    for (const cat of categories.filter(c => categorynames.includes(c.name))) {
        const intervals = cat.intervals
            .map(({id, start, end}) => ({ id, start, end, startdate: toDate(start.split("T")[0]), enddate: toDate(end.split("T")[0]) }))
            .filter(({startdate, enddate}) => startdate <= toDate(date) && toDate(date) <= enddate)
            .map(({id, start, end}) => {
                const day_begin = toDate(date);
                const day_end = new Date(day_begin.getTime() + 23*60000*60 + 59*60000);

                return {
                    id,
                    // starts before this day?
                    start: toDate(start) <= day_begin ? null : start,
                    // ends after this day?
                    end: toDate(end) >= day_end ? null : end,
                };
            });
        appointments.push(...intervals.map(i => ({...i, category: cat})));
    }

    document.querySelector("#dayModalLabel").innerText = toDate(date).toLocaleDateString('de-DE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    document.querySelector("#dayModal .modal-body").innerHTML = appointments
        .sort((a, b) =>
            toDate(a.start).getTime() - toDate(b.start).getTime() ||
            toDate(a.end).getTime() - toDate(b.end).getTime() ||
            (a.category.name <= b.category.name ? -1 : 1)
        )
        .map(({id, start, end, category}) => `
            <div class="appointment" style="background: ${category.color}; color: ${category.textColor}">
                <span class="appointment__name">${category.name}</span>
                <small class="appointment__time">
                    ${start !== null ? toDate(start).toLocaleTimeString('de-DE', { hour: "2-digit", minute: "2-digit" }) : '00:00'} -
                    ${end !== null ? toDate(end).toLocaleTimeString('de-DE', { hour: "2-digit", minute: "2-digit" }) : '23:59'} Uhr
                </small>
                <a type="button" aria-label="delete" class="del-btn btn btn-sm btn-danger ms-2 m-auto" href="/todo/delete_interval/${id}/${date}">
					<svg style="width:1em; margin: auto; display: block;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
						<!--! Font Awesome Pro 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. -->
						<path fill="#ffffff" d="M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z"/>
					</svg>
				</a>
            </div>`
        ).join("") || "Keine Termine";
    document.querySelector('[data-bs-toggle="modal"][data-bs-target="#dayModal"]').click();

}