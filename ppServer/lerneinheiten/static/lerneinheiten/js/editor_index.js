// Loop through each nested sortable element
const sortables = [...document.querySelectorAll(".sortable-list")].map(list =>
    new Sortable(list, {
        handle: '.handle', // handle's class
        group: { name: "einheit", pull: false, put: false },
        animation: 150,
        fallbackOnBody: true,
        swapThreshold: 0.65,

        onSort: set_order,
    })
);

function set_order() {
    const content = sortables.reduce((acc, sortable) => {
        acc[sortable.el.dataset.einheit] = sortable.toArray().map(id => parseInt(id));
        return acc;
    }, {});
    document.querySelector("#input-sortable").value = JSON.stringify(content);
}

set_order();