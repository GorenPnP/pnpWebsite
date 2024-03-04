// Loop through each nested sortable element
const sortables = [...(document.querySelectorAll(".sortable-list") as any)].map(list =>
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
        acc[sortable.el.dataset.einheit!] = sortable.toArray().map((id: string) => parseInt(id));
        return acc;
    }, {} as {[einheit_id: string]: number[]});
    (document.querySelector("#input-sortable")! as any).value = JSON.stringify(content);
}

set_order();