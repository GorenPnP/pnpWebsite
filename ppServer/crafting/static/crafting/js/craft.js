/** one of: ["table", "search", "fav"] */
let currently_showing_recipes_of = "table";

/*
	HELPER FUNCTIONS
*/

/** helper function. Constructs HTML-recipelist out of recipe-data */
function construct_recipes(recipes) {
	const displayFloat = (f) => parseFloat(f)?.toFixed(1).toString().replace(".", ",").replace(",0", "");

	let html = "";

	// opening container
	recipes.forEach(recipe => {
		var html_recipe =
			`<div div class="recipe-row id-${recipe.id}" >
					<div class="recipe">
						<div class="ingredients">`;

		// ingredients
		recipe.ingredients.forEach(i =>
			html_recipe +=
				`<div class="ingredient">
						<img src="${i.icon}" alt="${i.name}" loading="lazy">

						<div class="text">
							<span class="inum">
								<span class="own-num">${displayFloat(i.own)}</span>/<span class="needed-num" data-default=${i.num}>${displayFloat(i.num)}</span>
							</span>
							<span class="name">${i.name}</span>
						</div>
					</div>`
		)

		// arrow
		html_recipe +=
			`</div>
			<div class="arrow-container">`;

		if (currently_showing_recipes_of != "table") {
			html_recipe += `<div class="table item table--arrow`;

			if (!recipe.locked)
				html_recipe += ` available`;

			html_recipe += `">
				<img src = "${recipe.table.icon}" alt = "${recipe.table.name}" loading="lazy">
			</div>
			<span class="name name--table">${recipe.table.name}</span>`;
		}

		html_recipe +=
				`<div class="arrow"></div>
			</div>
				<div class="products">`;


		// products
		recipe.products.forEach(p =>
			html_recipe +=
			`<div class="product pid-${ p.id } id-${recipe.id}">
							<img src="${p.icon}" alt="${p.name}" loading="lazy">

							<div class="text">
								<span class="pnum" data-default=${p.num}>${displayFloat(p.num)}</span>
								<span class="name">${p.name}</span>
							</div>
					</div>`
		)

		// closing container with crafting combo
		html_recipe +=
			`</div>
				</div>

				<div class="craft input-with-btn">
					<input type="number" name="craftNum" class="craftNum id-${recipe.id}" min=1 value=1 ${recipe.produces_perk ? 'max=1 disabled' : ''} oninput="calc_recipe_numbers(event)">
					<button class="btn btn-primary id-${recipe.id}" onclick="craft(event)" data-locked="${recipe.locked }">Craft</button>
				</div>

				<a class="info" href="/crafting/details/${recipe.id}/">
					<img src="/static/res/img/info.svg" alt="Info" loading="lazy">
				</a>
				<button class="btn btn-outline-warning fav-btn" onclick="toggle_Fav(${recipe.id})">${recipe.is_fav ? '⭑' : '⭒'}</button>
			</div>`;

		html += html_recipe;
	});
	return html || "keine Rezepte vorhanden :(";
}


// helper function. Updates disabled-status of crafting for each recipe by triggering the onInput-eventhandler of .craftNum
function update_all_recipe_numbers() {
	const event = new Event('input');

	// trigger calc_recipe_numbers() on every recipes' number input
	document.querySelectorAll(".craftNum").forEach(num_input => num_input.dispatchEvent(event));
}


/*
	callbacks triggered on dragging of tables
*/

function init_table_reorder() {

	// the container
	const tables = document.querySelector(".tables");

	// use sortable.js for drag & drop of tables
	const list = new Sortable(tables, {
		animation: 150,
		swapThreshold: 0.65,
		filter: '#tid-fav',	// fav is not draggable (but tables can be dragged above?)
		ghostClass: 'table--ghost',	// class a dragged table-duplicate has. For styling
	});

	// save new order to BE when user drops table
	tables.addEventListener("end", function() {
		table_ids = list.toArray()	// list of .table->data-id strings
			.map(id => parseInt(id))
			.filter(id => !isNaN(id));	// filter "fav" away
		
		post({ update_table_ordering: table_ids });
	});

}

/*
	EVENT HANDLERS
*/

// select a different table and show its recipes instead of the current ones
function change_to_table(id) {
	const selected_tag = document.querySelector(`#${id}`);
	const table_id = id.replace(/^tid\-/, "");
	
	location.hash = table_id;
	currently_showing_recipes_of = table_id === "fav" ? "fav" : "table";

	// markup for selection
	document.querySelectorAll(".table.selected").forEach(table => table.classList.remove("selected"));
	selected_tag.classList.add("selected");

	// set topic to selected
	document.querySelector("title").innerHTML = selected_tag.dataset.title;
	document.querySelector("header .navbar-brand .topic").innerHTML = selected_tag.dataset.title;

	return new Promise((resolve, reject) => {
		post({ search_recipes_by_table: table_id }, data => {

			// update durability on table in table list on the left
			if (data.part) {
				selected_tag.querySelector(".progressbar-inner").style.width = data.percent_durability_left + "%";
				selected_tag.classList.toggle("broken",  data.durability_left === 0);
			}

			// construct table part
			document.querySelector(".recipes").innerHTML = "";
			if (data.part && data.durability_left === 0) {
				document.querySelector(".recipes").innerHTML = `<div class="alert alert-danger" role="alert">
						Bauteil "${data.part.name}" ist kaputt gegangen. Um die Werkstation weiter zu verwenden, musst du es erst${!data.owns_part ? ' besorgen und' : ''} erneuern${!data.owns_part ? '.' : ':'}
					</div>`;
				
				// has part?
				if (data.owns_part) {
					document.querySelector(".recipes").innerHTML += `<button class="btn btn-danger ingredient" onclick="repair_table(${table_id})">
						<img src="${data.part.icon_url}" alt="${data.part.name}" loading="lazy">
						<span class="text">Bauteil ${data.part.name} erneuern</span>
					</button>`;
				}
			}
			document.querySelector(".recipes").innerHTML += construct_recipes(data.recipes);

			// disable recipes where necessary
			update_all_recipe_numbers();

			resolve();
		}, async error => {
			alert(error.response?.data?.message || error);

			await update_tables();
			await update_recipes();

			resolve();
		});
	});
}

function toggle_Fav(id) {
	post({ fav: id }, () => {

		// toggle pressed fav button
		const fav_btn = document.querySelector(`.recipes .recipe-row.id-${id} .fav-btn`);
		fav_btn.innerHTML = fav_btn.innerHTML === '⭒' ? '⭑' : '⭒';

		if (currently_showing_recipes_of === "fav") {
			// currently on fav-"table" and need to remove recipe from view
			change_to_table("tid-fav");
		}

		// update availability of fav-"table"
		update_tables();
	}, error => {
		alert(error.response?.data?.message || error);

		update_recipes();
	});
}


// adapt required amounts onInput-event of input-element[type:number]
function calc_recipe_numbers({ currentTarget }) {

	// amount of product
	const num = parseInt(currentTarget.value) || 0;

	// get common id (used as class on html)
	let id_class = ""
	currentTarget.classList.forEach(e => {if (e.startsWith("id-")) id_class = e});

	const row = document.querySelector(".recipe-row." + id_class);

	// should crafting be allowed?
	let disable_btn = document.querySelector(".btn." + id_class).dataset.locked == "true";

	// calc amount for products
	row.querySelectorAll(".pnum").forEach(pnum_tag => {
		const base = parseFloat(pnum_tag.dataset.default);
		pnum_tag.innerHTML = (base * num).toFixed(1).toString().replace(".", ",").replace(",0", "");		// round to one digit after decimal sign, leave out if it is a 0
	})

	// calc amount for ingredients
	row.querySelectorAll(".inum").forEach(inum_tag => {
		const needed_tag = inum_tag.querySelector(".needed-num");
		const own_tag = inum_tag.querySelector(".own-num");

		// calc needed
		const needed_num = parseFloat(needed_tag.dataset.default) * num;
		needed_tag.innerHTML = needed_num.toFixed(1).toString().replace(".", ",").replace(",0", "");		// round to one digit after decimal sign, leave out if it is a 0

		// still own sufficient amount?
		if (needed_num > parseFloat(own_tag.innerHTML)) {
			inum_tag.classList.add("insufficient");
			disable_btn = true;
		}
		else {
			inum_tag.classList.remove("insufficient");
		}
	})

	// check table availability
	const table_available =
		(currently_showing_recipes_of === "table" && document.querySelector(".tables .table.selected.available")) ||
		row.querySelector(".table--arrow.available")

	// disable btn?
	row.querySelector(".btn").disabled = disable_btn || !table_available;
}


function update_tables() {
	return new Promise((resolve, reject) => {

		post({ fetch_tables: true }, ({ tables, has_favorite_recipes }) => {
			const curr_table_id = location.hash.replace(/^#/, "");
			const is_selected = (table_id) => currently_showing_recipes_of !== "search" && curr_table_id == table_id;
	
			const fav_table = `<div
				class="table${is_selected('fav') ? ' selected' : ''}${has_favorite_recipes ? ' available' : ''}"
				id="tid-fav"
				onclick="change_to_table('tid-fav')"
				data-title="Favorisiert" data-id="">⭑
			</div>`;
		
			const other_tables = tables.map(table =>
				`<div
					class="table${is_selected(table.id) ? ' selected' : ''}${table.available ? ' available' : ''}${ table.part && table.durability_left == 0 ? ' broken' : ''}"
					id="tid-${ table.id }"
					onclick="change_to_table('tid-${ table.id }')"
					data-title="${ table.name }" data-id="${table.id}">
	
					<img src="${ table.icon }" alt="${ table.name }" loading="lazy">` +
					(table.part ?
					`<div class="progressbar" role="progressbar" aria-label="Haltbarkeit" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
						<div class="progressbar-inner" style="width: ${ table.percent_durability_left }%"></div>
					</div>` : '') +
				`</div>`);
			document.querySelector(".tables").innerHTML = [fav_table, ...other_tables].join("");

			resolve();
		}, reject);
	});
}

function update_recipes() {
	// reload by table
	if (currently_showing_recipes_of !== "search")
		return change_to_table(document.querySelector(".table.selected").id);

	// reload by search term
	return search();
}

// craft num of items
function craft({ currentTarget }) {
	if (currentTarget.disabled) return;


	// get common recipe_id
	let id_class = "";
	currentTarget.classList.forEach(e => { if (e.startsWith("id-")) id_class = e });

	// get num produced items
	const num = document.querySelector(".craftNum." + id_class).value;
	const id = /\d+/.exec(id_class)[0];

	post({ craft: id, num }, async data => {
		await update_running_recipes();
		await update_tables();
		await update_recipes();

		// log used parts
		if (data.used_parts && data.part) {
			const dummy = document.createElement("div");
			dummy.innerHTML = `
			<div class="toast show" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="false">
				<div class="d-flex">
					<div class="toast-body text-dark">
						<span>Werkstation-Reparatur mit <b>${data.used_parts}x</b> </span>
						<div class="d-flex flex-column">
							<img src="${data.part.icon_url}" alt="${data.part.name}" loading="lazy">
							<span class="name">${data.part.name}</span>
						</div>
					</div>
					<button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
				</div>
			</div>`;
			const toast = dummy.children[0];
			document.querySelector(".toast-container").appendChild(toast);

			new bootstrap.Toast(dummy.children[0]);
			toast.addEventListener("hidden.bs.toast", toast.remove);
		}
	}, async error => {
		alert(error.response?.data?.message || error);

		await update_running_recipes();
		await update_tables();
		await update_recipes();
	})
}


// used to autocomplete search bar while typing. Event fires onInput-change
// retrieve a list of entries

// need to add
// oninput="update_search_itemname_options(event)"
// on input again, temporarily disabled
function update_search_itemname_options({ currentTarget }) {
	const text = currentTarget.value;

	// post -> get fitting entries back
	post({fetch_itemnames: text}, data => {

		// repopulate datalist of searchbar
		document.querySelector("#item-search").innerHTML = data.res.map(name => `<option value="${name}">${name}</option>`).join("");
	}, reaction, false)		// false => don't display spinner
}


// search submitted, retrieve recipes and display them. Unselect table in sidebar
function search() {
	const text = document.querySelector("#search-input").value;

	return new Promise((resolve, reject) => {
		post({ search_recipes_by_name: text }, data => {

			// reset table selection
			currently_showing_recipes_of = "search";
			document.querySelectorAll(".table.selected").forEach(table => table.classList.remove("selected"));

			// set topic to search text
			document.querySelector("title").innerHTML = `Suche nach '${text}'`;
			document.querySelector("header .navbar-brand .topic").innerHTML = `Suche nach '${text}'`;

			// display recipes with search term as product and ingredient
			document.querySelector(".recipes").innerHTML =
				`<h1>ALS PRODUKT:</h1>${construct_recipes(data.as_product) || `<div>-</div>`}
				<h1>ALS ZUTAT:</h1>${construct_recipes(data.as_ingredient) || `<div>-</div>`}`

			// disable recipes where necessary
			update_all_recipe_numbers();

			resolve();
		}, reject);
	})
}


function repair_table(table_id) {
	return new Promise((resolve, reject) => {
		post({ repair_table: table_id }, async () => {
			await update_tables();
			await update_recipes();

			resolve();
		}, async error => {
			alert(error.response?.data?.message || error);

			await update_tables();
			await update_recipes();

			resolve();
		});
	})
}


function update_running_recipes() {
	return new Promise((resolve, reject) => {

		post({ fetch_running_recipes: true }, ({ running_recipes, changed_table_order }) => {
	
			const html = running_recipes.map(r => {
				const products = r.products.map(product => `<div>${product.num * r.num}x <img src="${product.icon_url}" alt="${product.name}" loading="lazy"></div>`).join("");
	
				const curr = Date.now();
				const begin = (new Date(r.begins_at)).getTime();
				const start = Math.min(begin, Math.max(curr, (new Date(r.starts_at)).getTime()));
				const end = (new Date(r.finishes_at)).getTime();
				const wait_percent = curr < begin ? Math.round(100* (curr-start) / (begin-start)) : 100;
				const work_percent = curr > begin ? Math.round(100* (curr-begin) / (end-begin)) : 0;
				const transition = `transition: width 200ms linear`;
				
				const date_options = (new Date(r.finishes_at)).getUTCDate() == (new Date(Date.now())).getUTCDate() ?
					{hour: "2-digit", minute: "2-digit"} :
					{ year: 'numeric', month: 'numeric', day: 'numeric', hour: "2-digit", minute: "2-digit" };
				const begin_date = (new Date(r.begins_at)).toLocaleString('de-DE', date_options);
				const end_date = (new Date(r.finishes_at)).toLocaleString('de-DE', date_options);
	
				return `<div class="d-flex flex-wrap gap-3">${products}</div>
						<div class="progress d-flex" style="gap: 1px; background: none;">
							<div class="progress" role="progressbar" aria-label="warten" aria-valuenow="${Math.max(start, curr)}" aria-valuemin="${start}" aria-valuemax="${begin}" style="width: ${100*(begin-start) / (end-start)}%; border-radius: 0; ${transition}">
								<div class="progress-bar text-bg-info overflow-visible" style="width: ${wait_percent}%; ${transition}">warten bis ${begin_date}</div>
							</div>
							<div class="progress" role="progressbar" aria-label="arbeiten" aria-valuenow="${Math.max(begin, curr)}" aria-valuemin="${begin}" aria-valuemax="${end}" style="width: ${100 - 100*(begin-start) / (end-start)}%; border-radius: 0">
								<div class="progress-bar text-bg-warning overflow-visible" style="width: ${work_percent}%; ${transition}">bis ${end_date}</div>
							</div>
						</div>`;
			}).join("</li><li>");
			document.querySelector(".running-recipes-list").innerHTML = html ? "<li>" + html + "</li>" : "";


			if (changed_table_order) {
				update_tables().then(resolve);
			} else {
				resolve();
			}
		}, reject);
	})
}

async function draw_running_recipes_loop() {
	let needs_reload = false;

	document.querySelectorAll(".running-recipes-list .progress.d-flex").forEach(progress => {
		const [waitBar, workBar] = progress.querySelectorAll(".progress");

		const start = waitBar.ariaValueMin;
		const begin = waitBar.ariaValueMax;
		const end = workBar.ariaValueMax;
		const curr = Date.now();

		waitBar.ariaValueNow = Math.max(start, curr);
		workBar.ariaValueNow = Math.max(begin, curr);

		waitBar.querySelector(".progress-bar").style.width = (curr < begin ? Math.round(100* (curr-start) / (begin-start)) : 100) + "%";
		workBar.querySelector(".progress-bar").style.width = (curr > begin ? Math.round(100* (curr-begin) / (end-begin)) : 0) + "%";

		// reload once at the end if necessary
		needs_reload = needs_reload || end <= curr;
	});

	// reload where necessary
	if (needs_reload) {
		await update_running_recipes();
	}

	setTimeout(draw_running_recipes_loop, 1000);

	// reload the non-time critical rest later/here
	if (needs_reload) {
		await update_tables();
		await update_recipes();
	}
}


document.addEventListener("DOMContentLoaded", async () => {

	// load page content

	// update currently crafting recipes
	await update_running_recipes();

	// load all tables
	await update_tables();

	// get all recipes of the table whose table id is in the url-# or from the first table
	change_to_table(location.hash?.length ? `tid-${location.hash.substring(1)}` : document.querySelector(".table").id);

	// init_table_reorder
	init_table_reorder();


	// animate currently crafting recipes and craft when done
	draw_running_recipes_loop();

	// send input data per btn event on keydown of enter key (e.G. search, amount recipes)
	document.addEventListener("keydown", e => {
		// on enter ^= ascii-code 13
		if (e.keyCode === 13 && e.target.tagName === "INPUT") {

			// click (first) sibling btn
			e.target.parentElement.querySelector(".btn")?.click();
		}
	});
});
