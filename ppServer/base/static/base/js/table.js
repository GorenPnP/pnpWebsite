// PAGINATION_PAGE_SIZE = 50;
TABLE_TAG = document.querySelector('#table');

let headings, row_data;


function focus_row() {
    var hash = window.location.hash;
    var id = hash.substring(1);

    if (hash) {
        const marked_row = TABLE_TAG.querySelector(`tr[data-id="${id}"]`);
        if (marked_row) {
            marked_row.classList.add("marked");
            marked_row.scrollIntoView({ behavior: "smooth", block: "end"});
        }
    }
}

function get_headings(buyable) {
    const sortable = JSON.parse(document.querySelector("#sortable").textContent) === "true";

    // def columns
    const headings = JSON.parse(document.querySelector("#headings").textContent)
        .map(def => {
            switch(def.type) {
                case "image":
                    return {...def, filter: false, sortable: false, cellRenderer: params => `<img src="${params.value}" class="icon">` };
                case "date":
                    return {...def, filter: false, sortable, cellRenderer: params => params.value ? params.value.split("-").reverse().join(".") : '-'};
                case "datetime":
                    return {...def, filter: false, sortable, cellRenderer: params => { date = new Date(params.value); return `${date.toLocaleDateString("de-DE")} ${date.toLocaleTimeString("de-DE")}` }};// ? params.value.split("-").reverse().join(".") : '-'};
                case "number":
                    return {...def, filter: true, sortable, cellRenderer: params => params.value ? new Intl.NumberFormat("de").format(params.value) : '-'};
                case "price":
                    return {...def, filter: true, sortable, cellRenderer: params => params.value ? `${new Intl.NumberFormat("de").format(params.value)} Dr.`: '-'};
                case "boolean":
                    return {...def, filter: true, sortable, cellRenderer: params => params.value ? "ja" : "-"};
                case "text": case "text--long":
                    return {...def, filter: true, sortable, cellRenderer: params => params.value || "-"};
                case "number input":
                    return {...def, filter: true, sortable, cellRenderer: params => `<input type="number" placeholder="0" value="${params.value}">`};
                default: return def;
            }
        });

    if (buyable) {
        headings.push({display: "", field: "buy", cellRenderer: params => params.data.url ? `<button onclick='window.location.href = "${params.data.url}"'>Kaufen</button>` : ''});
    }
    return headings;
}

function get_filter(type) {
    switch(type) {
        case "image":
            return document.createElement('select');
        case "number":
            const von = document.createElement('input');
            const bis = document.createElement('input');
            von.type = 'number';
            bis.type = 'number';
            const container = document.createElement('div');
            container.appendChild(von);
            container.appendChild(bis);
            return container;
        case "price":
            const input_tag = document.createElement('input');
            input_tag.type = 'number';
            return input_tag;
        case "boolean":
            return document.createElement('select');
        case "text": case "text--long":
            return document.createElement('input');
    }
}

function draw_headings_and_filter(headings) {
    if (!TABLE_TAG) { return; }

    const heading_tr_tag = document.createElement('tr');
    const filter_tr_tag = document.createElement('tr');
    heading_tr_tag.setAttribute("data-contains", 'heading');
    filter_tr_tag.setAttribute("data-contains", 'filter');

    for (heading of headings) {
        // heading
        const heading_th_tag = document.createElement('th');
        heading_th_tag.innerText = heading.display;
        heading_th_tag.setAttribute("data-field", heading.field);
        if (heading.sortable) {
            heading_th_tag.setAttribute("data-sortable", true);
        }
        
        heading_tr_tag.appendChild(heading_th_tag);

        // filter
        const filter_td_tag = document.createElement('td');
        // TODO re-add filter
        // if (heading.filter) {
        //     filter_td_tag.appendChild(get_filter(heading.type));
        // }
        filter_tr_tag.appendChild(filter_td_tag);
    }
    
    TABLE_TAG.appendChild(heading_tr_tag);
    if (filter_tr_tag.querySelector("input")) { TABLE_TAG.appendChild(filter_tr_tag); }
}


function get_rows(buyable) {
    // collect data
    const rows = JSON.parse(document.querySelector("#rows").textContent);

    if (buyable) {
        rows.forEach(row => row.buy = row.url);
    }
    return rows;
}

function draw_rows(rows, headings) {
    if (!TABLE_TAG) { return; }

    for (const row of rows) {
        const tr_tag = document.createElement('tr');
        tr_tag.setAttribute("data-contains", 'content');
        tr_tag.setAttribute("data-id", row.pk);

        for (heading of headings) {
            const td_tag = document.createElement('td');
            td_tag.innerHTML =  heading.cellRenderer({data: row, value: heading.type === "text" ? row[heading.field]?.replaceAll("\n", "<br>") : row[heading.field]});
            tr_tag.appendChild(td_tag);
        }

        TABLE_TAG.appendChild(tr_tag);
    }
}


function init_table() {
    if (!TABLE_TAG) { return; }

    const buyable = JSON.parse(document.querySelector("#buyable").textContent)

    headings = get_headings(buyable);
    draw_headings_and_filter(headings);

    const rows = get_rows(buyable);
    draw_rows(rows, headings);

    // table is displayed, save data for later reference
    row_data = rows;

    // event listeners
    window.addEventListener('hashchange', focus_row);
    TABLE_TAG.querySelectorAll("[data-sortable]").forEach(tag => tag.addEventListener("click", callback_sort_by));
}



/******************** init ***************************** */
init_table();

/******************** Callbacks ************************ */

/**** sort *** */
function callback_sort_by(event) {
    const field = event.target.dataset.field;
    const heading = headings.find(heading => heading.field === field && heading.display === event.target.textContent);
    const prev_sort = event.target.dataset.sort;
    const sort_direction = prev_sort === "asc" ? "desc" : "asc";

    TABLE_TAG.querySelectorAll("[data-sort]").forEach(tag => tag.setAttribute("data-sort", ""))
    event.target.dataset.sort = sort_direction;

    // DESC
    if (sort_direction === "desc") { return sort_table_desc(); }

    // ASC

    // sort function
    const sort = (dataRow_a, dataRow_b) => {
        const [a, b] = [dataRow_a[heading.field], dataRow_b[heading.field]];
        let result;

        switch(heading.type) {
            case "text": case "text--long":
                result = a.toLowerCase() <= b.toLowerCase() ? -1 : 1; break;
            case "number": case "price":
                result = parseFloat(a) <= parseFloat(b) ? -1 : 1; break;
            case "boolean": case "image":
                result = !a || (a && b) ? -1 : 1; break;
            case "date": case "datetime":
                new Date(a) <= new Date(b) ? -1 : 1; break;
        }
        return result;
    }
    sort_table_asc(row_data, sort);
}

// see https://www.w3schools.com/howto/howto_js_sort_table.asp
function sort_table_asc(data_rows, sort) {
    var switching, shouldSwitch;
    switching = true;
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {

      // Start by saying: no switching is done:
      switching = false;
      const rows = [...TABLE_TAG.rows].filter(row => row.dataset.contains === "content");

      let prev_row = rows.shift();
      let row;
      /* Loop through all table rows (except the
      first, which contains table headers): */
      for (row of rows) {
        // Start by saying there should be no switching:
        shouldSwitch = false;
        /* Get the two elements you want to compare,
        one from current row and one from the next: */
        const prev = data_rows.find(data_row => data_row.pk == prev_row.dataset.id);
        const curr = data_rows.find(data_row => data_row.pk == row.dataset.id);
        // Check if the two rows should switch place:
        if (sort(prev, curr) > 0) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }

        prev_row = row;
      }
      if (shouldSwitch) {
        /* If a switch has been marked, make the switch
        and mark that a switch has been done: */
        TABLE_TAG.insertBefore(row, prev_row);
        switching = true;
      }
    }
}

// just inverse table completely, because it was ordered asc before.
function sort_table_desc() {
    const rows = [...TABLE_TAG.rows].filter(row => row.dataset.contains === "content");
    const first_row = rows.shift();
    for (row of rows.reverse()) {
        TABLE_TAG.insertBefore(row, first_row);
    }
}


/**** filter *** */
// TODO