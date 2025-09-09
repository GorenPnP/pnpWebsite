/*
	HELPER FUNCTIONS
*/
function displayFloat(f) {
	return parseFloat(f)?.toFixed(1).toString().replace(".", ",").replace(",0", "")
}

// helper function. Constructs HTML-recipelist out of recipe-data
function constructRecipes(recipes, include_table=false) {
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
						<img src="${i.icon}" alt="${i.name}">

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

		if (include_table) {
			html_recipe += `<div class="table item table--arrow`;

			if (!recipe.locked)
				html_recipe += ` available`;

			html_recipe += `">
				<img src = "${recipe.table.icon}" alt = "${recipe.table.name}" >
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
							<img src="${p.icon}" alt="${p.name}">

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
					<input type="number" name="craftNum" class="craftNum id-${recipe.id}" min=1 value=1 ${recipe.produces_perk ? 'max=1 disabled' : ''} oninput="craftChange(event)">
					<button class="btn btn-primary id-${recipe.id}" onclick="craft(event)" data-locked="${recipe.locked }">Craft</button>
				</div>

				<a class="info" href="/crafting/details/${recipe.id}/">
					<img src="/static/res/img/info.svg" alt="Info">
				</a>
				<button class="btn btn-outline-warning fav-btn" onclick="toggleFav(${recipe.id})">${recipe.is_fav ? '⭑' : '⭒'}</button>
			</div>`;

		html += html_recipe;
	});
	return html || "keine Rezepte vorhanden :(";
}


// helper function. Updates disabled-status of crafting for each recipe by triggering the onInput-eventhandler of .craftNum
function updateRecipeStatus() {
	const event = new Event('input');

	document.querySelectorAll(".craftNum").forEach(num_input => {
		num_input.dispatchEvent(event)
	});
}


/*
	callbacks triggered on dragging of tables
*/

function drag_start_callback(element) {

	// show table recipes
	tableChange(element.id)
}

function drag_end_callback() {
	// save new ordering to db
	var tables = [...document.querySelectorAll('.table')]
		.map(table => { return parseInt(/\d+/.exec(table.id)) })
		.filter(table_id => typeof table_id === 'number');

	post({ table_ordering: tables }, reaction, reaction, false)
}

/*
	EVENT HANDLERS
*/

// select a different table and show its recipes instead of the current ones
function tableChange(id) {
	const selected_tag = document.querySelector(`#${id}`);
	const table_id = id.replace(/^tid\-/, "");

	location.hash = table_id;

	// markup for selection
	document.querySelectorAll(".table.selected").forEach(table => table.classList.remove("selected"));
	selected_tag.classList.add("selected");

	// set topic to selected
	document.querySelector("title").innerHTML = selected_tag.dataset.title;
	document.querySelector("header .navbar-brand .topic").innerHTML = selected_tag.dataset.title;

	post({ table: table_id }, data => {

		// update durability on table in table list on the left
		if (data.part) {
			selected_tag.querySelector(".progressbar-inner").style.width = data.percent_durability_left + "%";
			selected_tag.classList.toggle("broken",  data.durability_left === 0);
		}

		// construct table part
		document.querySelector(".recipes").innerHTML = "";
		if (data.part && data.durability_left === 0) {
			document.querySelector(".recipes").innerHTML = `<div class="alert alert-danger" role="alert">
					Bauteil "${data.part.name}" ist kaputt gegangen. Um die Werkstation weiter zu verwenden musst du es erst${!data.owns_part ? ' besorgen und' : ''} eneuern${!data.owns_part ? '.' : ':'}
				</div>`;
			
			// has part?
			if (data.owns_part) {
				document.querySelector(".recipes").innerHTML += `<button class="btn btn-danger ingredient" onclick="repair_table(${table_id})">
					<img src="${data.part.icon_url}" alt="${data.part.name}">
					<span class="text">Bauteil ${data.part.name} erneuern</span>
				</button>`;
			}
		}
		document.querySelector(".recipes").innerHTML += constructRecipes(data.recipes, table_id === "fav");

		// disable recipes where necessary
		updateRecipeStatus();
	}, null)
}

function toggleFav(id) {
	
	post({ fav: id }, ({ num_favs }) => {

		// toggle pressed fav button
		const fav_btn = document.querySelector(`.recipes .recipe-row.id-${id} .fav-btn`);
		fav_btn.innerHTML = fav_btn.innerHTML === '⭒' ? '⭑' : '⭒';

		// currently on fav-"table" and need to remove recipe from view
		if (fav_btn.innerHTML === '⭒' && location.hash === "#fav") {
			document.querySelector(`.recipes .recipe-row.id-${id}`).remove();
		}

		// update availability of fav-"table"
		document.querySelector(`#tid-fav`).classList.toggle("available", num_favs > 0);
	}, null)
}


// adapt required amounts onInput-event of input-element[type:number]
function craftChange({ currentTarget }) {

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

	// disable btn?
	row.querySelector(".btn").disabled = disable_btn;
}


// craft num of items
function craft({ currentTarget }) {
	if (currentTarget.disabled) return;

	reload_recipes = () => {
		const selected_table = document.querySelector(".table.selected");
		
		// reload by table
		if (selected_table) tableChange(selected_table.id);

		// reload by search term
		else document.querySelector("#search-btn").dispatchEvent(new Event('click'));
	};

	// get common recipe_id
	let id_class = "";
	currentTarget.classList.forEach(e => { if (e.startsWith("id-")) id_class = e });

	// get num produced items
	const num = document.querySelector(".craftNum." + id_class).value;
	const id = /\d+/.exec(id_class)[0];

	post({ craft: id, num}, data => {

		// if crafted element was a table, enable it ...
		document.querySelectorAll(".product." + id_class).forEach(product => {
			let pid = -1;
			product.classList.forEach(e => { if (e.startsWith("pid-")) pid = /\d+/.exec(e); })

			let table = document.querySelector("#tid-" + pid);
			table?.classList.add("available");

			// ... and move it up
			const first_unavailable_table = document.querySelector(".tables .table:not(.available)");
			const tables = [...document.querySelector(".tables").children];
			const table_index = tables.indexOf(table);
			const space_before = tables.indexOf(first_unavailable_table);
			if (table_index > space_before) {
				table.remove();
				document.querySelector(".tables").insertBefore(table, first_unavailable_table);
				drag_end_callback();	// save new ordering to BE
			}
		});

		reload_recipes();
		updateRunningRecipes();

		// log used parts
		if (data.used_parts && data.part) {
			const dummy = document.createElement("div");
			dummy.innerHTML = `
			<div class="toast show" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="false">
				<div class="d-flex">
					<div class="toast-body text-dark">
						<span>Werkstation-Reparatur mit <b>${data.used_parts}x</b> </span>
						<div class="d-flex flex-column">
							<img src="${data.part.icon_url}" alt="${data.part.name}">
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
	}, error => {
		alert(error.response.data.message);

		reload_recipes();
	})
}


// used to autocomplete search bar while typing. Event fires onInput-change
// retrieve a list of entries

// need to add
// oninput="searchChange(event)"
// on input again, temporarily disabled
function searchChange({ currentTarget }) {
	const text = currentTarget.value;

	// post -> get fitting entries back
	post({search: text}, data => {

		// repopulate datalist of searchbar
		document.querySelector("#item-search").innerHTML = data.res.map(name => `<option value="${name}">${name}</option>`).join("");
	}, reaction, false)		// false => don't display spinner
}


// search submitted, retrieve recipes and display them. Unselect table in sidebar
function search() {
	var text = document.querySelector("#search-input").value;

	post({ search_btn: text }, data => {

		// reset table selection
		document.querySelectorAll(".table.selected").forEach(table => table.classList.remove("selected"));

		// set topic to search text
		document.querySelector("title").innerHTML = `Suche nach '${text}'`;
		document.querySelector("header .navbar-brand .topic").innerHTML = `Suche nach '${text}'`;

		// display recipes with search term as product and ingredient
		document.querySelector(".recipes").innerHTML =
			`<h1>ALS PRODUKT:</h1>${constructRecipes(data.as_product, true) || `<div>-</div>`}
			<h1>ALS ZUTAT:</h1>${constructRecipes(data.as_ingredient, true) || `<div>-</div>`}`

		// adapt recipe status
		updateRecipeStatus();
	})
}


function repair_table(table_id) {
	post({ repair_table: table_id }, () => {
		tableChange("tid-" + table_id);
	});
}


function updateRunningRecipes() {
	post({ running_recipes: true }, ({ running_recipes }) => {

		const html = running_recipes.map(r => {
			const products = r.products.map(product => `<div>${product.num * r.num}x <img src="${product.icon_url}" alt="${product.name}"></div>`).join("");

			const start = (new Date(r.started_at)).getTime();
			const end = (new Date(r.finished_at)).getTime();
			const curr = Date.now();
			const percent = Math.round(100* (curr-start) / (end-start));
			const transition = `transition: width 200ms linear`;
			
			const date_options = (new Date(r.finished_at)).getUTCDate() == (new Date(Date.now())).getUTCDate() ?
				{hour: "2-digit", minute: "2-digit"} :
				{ year: 'numeric', month: 'numeric', day: 'numeric', hour: "2-digit", minute: "2-digit" };
			const end_date = (new Date(r.finished_at)).toLocaleString('de-DE', date_options)

			return `<div class="d-flex flex-wrap gap-3">${products}</div>
			<div class="progress" role="progressbar" aria-label="Basic example" aria-valuenow="${curr}" aria-valuemin="${start}" aria-valuemax="${end}">
				<div class="progress-bar text-bg-warning overflow-visible" style="width: ${percent}%; ${transition}">bis ${end_date}</div>
			</div>`;
		}).join("</li><li>");
		document.querySelector(".running-recipes-list").innerHTML = html ? "<li>" + html + "</li>" : "";
	}, err => console.error(err));
}


document.addEventListener("DOMContentLoaded", () => {

	// load page content

	// get all recipes of the table whose table id is in the url-# or from the first table
	tableChange(location.hash?.length ? `tid-${location.hash.substring(1)}` : document.querySelector(".table").id);


	// initially disable recipes where necessary
	updateRecipeStatus();



	// event handlers
	init_draggable_reorder();

	// send input data per btn event on keydown of enter key
	document.querySelectorAll("input").forEach(el => el.addEventListener("keydown", (e) => {
		// on keydown of enter, i.e. ascii-code 13
		if (e.keyCode === 13) {

			// click (first) sibling btn
			e.currentTarget.parentElement.querySelector(".btn").click();
		}
	}));


	// update currently crafting recipes and animate their progress
	updateRunningRecipes();
	setInterval(() => document.querySelectorAll(".running-recipes-list .progress").forEach(bar => {
		const curr = Date.now();
		bar.ariaValueNow = curr;

		if (bar.ariaValueMax <= curr) updateRunningRecipes();
		bar.querySelector(".progress-bar").style.width = 100* (curr - bar.ariaValueMin) / (bar.ariaValueMax - bar.ariaValueMin) + "%";
	}), 1000);
})
