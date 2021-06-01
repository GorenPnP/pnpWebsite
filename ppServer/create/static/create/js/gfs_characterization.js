var gfs_characterizations = [];

var active_filters = {};    // {fieldname: "some value", ...}

document.addEventListener("DOMContentLoaded", () => {
    const gfs_characterizations_list = JSON.parse(document.querySelector("#gfs_characterizations").innerHTML);
    gfs_characterizations = gfs_characterizations_list.reduce((acc, g_c) => {
        acc[g_c.gfs_id] = g_c;
        return acc;
    }, {});

    currently_displayed_gfs = Object.keys(gfs_characterizations);
});

function filterChange(select_tag) {
    const fieldname = select_tag.id;
    const selected_value = [...select_tag.querySelectorAll("option")].find(option => option.selected).value;
    if (selected_value) {
        active_filters[fieldname] = selected_value;
    } else {
        delete active_filters[fieldname];
    }

    updateDisplayed();
}

function updateDisplayed() {
    const allGfsTags = [...document.querySelectorAll(".gfs-container .gfs")];
    const no_gfs_displayed = allGfsTags.map(gfs_tag => {
        const characterization = gfs_characterizations[gfs_tag.dataset.gfs_id];

        const is_displayed = Object.entries(active_filters)
            .map(([fieldname, value]) => characterization[fieldname] == value)
            .every(t => t);

        gfs_tag.style.display = is_displayed ? "flex" : "none";
        return is_displayed;
    }).every(is_displayed => !is_displayed);

    document.querySelector(".gfs-container").style.display = no_gfs_displayed ? "none" : "grid";
    document.querySelector(".none-found").style.display = !no_gfs_displayed ? "none" : "block";
}