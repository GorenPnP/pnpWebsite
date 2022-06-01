function focus_row() {
    var hash = window.location.hash;
    var id = hash.substring(1);

    if (hash) {
        const marked_row = gridOptions.api.getRowNode(id);
        if (marked_row) {
            marked_row.setSelected(true, true);
            gridOptions.rowData.find(row => row.pk == id).row_pinned = "top";
        }
    }
}

// def columns
const columnDefs = JSON.parse(document.querySelector("#headings").textContent)
    .map((def, index) => {
        if (index === 0) { def = {...def, rowDrag: true}; }

        switch(def.type) {
            case "image":
                return {...def, maxWidth: 85, sortable: false, menuTabs: ['generalMenuTab'], cellRenderer: params => `<img src="${params.value}" class="icon">` };
            case "number":
                return {...def, flex: 0.5, filter: "agNumberColumnFilter", cellRenderer: params => params.value ? new Intl.NumberFormat("de").format(params.value) : '-'};
            case "price":
                return {...def, filter: "agNumberColumnFilter", cellRenderer: params => params.value ? `${new Intl.NumberFormat("de").format(params.value)} Dr.`: '-'};
            case "boolean":
                return {...def, flex: 0.5, cellRenderer: params => params.value ? "ja" : "-"};
            case "text":
                    return {...def, cellRenderer: params => params.value || "-"};
            case "text--long":
                    return {...def, minWidth: 250, flex: 2, cellRenderer: params => params.value || "-"};
            default: return def;
        }
    });

const buyable = JSON.parse(document.querySelector("#buyable").textContent)
if (buyable) {
    columnDefs.push({headerName: "", field: "buy", cellRenderer: params => params.data.url ? `<button onclick='window.location.href = "${params.data.url}"'>Kaufen</button>` : ''});
}
columnDefs
    .filter(col => ["Name"].includes(col.headerName))
    .forEach(col => { col.pinned = 'left'; col.maxWidth = 120});


// collect data
const rowData = JSON.parse(document.querySelector("#rows").textContent);

if (buyable) {
    rowData.forEach(row => row.buy = row.url);
}

// let the grid know which columns and what data to use
gridOptions = {
    columnDefs,
    rowData,

    // sideBar: true,
    rowDragManaged: true,
    localeText: AG_GRID_LOCALE_DE,

    getRowId: params => params.data.pk,

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
};


// setup the grid after the page has finished loading
var gridDiv = document.querySelector('#table');
grid = new agGrid.Grid(gridDiv, gridOptions);



window.addEventListener('hashchange', focus_row);
focus_row();