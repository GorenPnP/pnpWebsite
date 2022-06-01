const fert_pool_tag = document.querySelector('#fert_pool');
const wp_pool_tag = document.querySelector('#wp_pool');

let initial_fert_pool = parseInt(fert_pool_tag.textContent);
let initial_wp_pool = parseInt(wp_pool_tag.textContent);

let selected_ferts = [];

function calc_initial_pools(ferts) {
    // get/calc values
    const values = ferts
        .map(fert => fert.punkte)
        .filter(punkte => punkte !== null);

    const wp = values
        .reduce((sum, wp_points) => sum + wp_points, 0);

    const num_ferts = values.length;

    initial_fert_pool = parseInt(fert_pool_tag.textContent) + num_ferts;
    initial_wp_pool = parseInt(wp_pool_tag.textContent) + wp;
}

function calc() {

    // get/calc values
    const values = [...document.querySelectorAll('[type="number"]')]
        .map(tag => parseInt(tag.value))
        .filter(val => !isNaN(val));

    const wp = values
        .reduce((sum, wp_points) => sum + wp_points, 0);

    const ferts = values.length;

    // update stats
    fert_pool_tag.textContent = initial_fert_pool - ferts;
    wp_pool_tag.textContent = initial_wp_pool - wp;

    selected_ferts = [...document.querySelectorAll('[type="number"]')]
        .filter(tag => !isNaN(parseInt(tag.value)))
        .map(tag => ({
            kind_of_fert: tag.dataset.fert,
            pk: parseInt(tag.dataset.pk),
            wp: parseInt(tag.value)
        }));

    // update submit button
    document.querySelector("#submit").disabled = fert_pool_tag.textContent != 0 ||  wp_pool_tag.textContent != 0;
}

function create_table(headings, rows, div, max_wp_per_row) {
    // def columns
    const columnDefs = headings
        .map(def => ({...def, pinned: def.headerName === "Name" ? 'left' : ''})
    );

    // add interactive wp column
    columnDefs.push({
        headerName: "WP (verteile Punkte)",
        field: "punkte",
        sort: 'desc',

        // editable: true,

        cellRenderer: params => `<input type="number" placeholder="0" min="0" max="${max_wp_per_row || initial_wp_pool}" step="1" value='${params.data.punkte || ''}' data-fert="${params.data.kind_of_fert}"data-pk="${params.data.pk}" onfocusout="calc()">`
    })

    // let the grid know which columns and what data to use
    const gridOptions = {
        columnDefs,
        rowData: rows,

        // sideBar: true,
        rowDragManaged: true,
        localeText: AG_GRID_LOCALE_DE,

        pagination: true,
        paginationPageSize: 50,

        defaultColDef: {
            flex: 1,
            minWidth: 100,
            // some actions
            sortable: true,
            filter: true,
            // read all text
            autoHeight: true,
            wrapText: true,
            resizable: true,

            
            menuTabs: ['filterMenuTab', 'generalMenuTab']
        },
        // highlight chosen ferts
        getRowStyle: params => {
            if (params.data.punkte !== null) {
                return { background: 'red' };
            }
        },
        suppressClickEdit: true,
    };


    // setup the grid after the page has finished loading
    new agGrid.Grid(div, gridOptions);

    return gridOptions;
}

function submit() {
    post({selected: selected_ferts});
}



calc_initial_pools([...JSON.parse(document.querySelector("#spezialfertigkeiten").textContent), ...JSON.parse(document.querySelector("#wissensfertigkeiten").textContent)]);

const spF_gridOptions = create_table(
    JSON.parse(document.querySelector("#headings_spF").textContent),
    [...JSON.parse(document.querySelector("#spezialfertigkeiten").textContent)].map(f => ({...f, kind_of_fert: "spF"})),
    document.querySelector('#table_spF')
);
const wF_gridOptions = create_table(
    JSON.parse(document.querySelector("#headings_wF").textContent),
    [...JSON.parse(document.querySelector("#wissensfertigkeiten").textContent)].map(f => ({...f, kind_of_fert: "wF"})),
    document.querySelector('#table_wF'),
    6
);

