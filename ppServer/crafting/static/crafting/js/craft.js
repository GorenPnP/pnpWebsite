/*
	HELPER FUNCTIONS
*/
function displayFloat(f) {
	return parseFloat(f)?.toFixed(1).toString().replace(".", ",").replace(",0", "")
}

// helper function. Constructs HTML-recipelist out of recipe-data
function constructRecipes(recipes, include_table=false) {
	var html = ""

	// opening container
	recipes.forEach(recipe => {
		var html_recipe =
			`<div div class="row id-${recipe.id}" >
					<div class="recipe">
						<div class="ingredients">`

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
			<div class="arrow-container">`

		if (include_table) {
			html_recipe +=
			`<div class="table item table--arrow`

			if (!recipe.locked)
				html_recipe += ` available`

			html_recipe += `">
				<img src = "${recipe.table.icon}" alt = "${recipe.table.name}" >
			</div>
			<span class="name name--table">${recipe.table.name}</span>`
		}

		html_recipe +=
				`<div class="arrow"></div>
			</div>
				<div class="products">`


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
					<input type="number" name="craftNum" class="craftNum id-${recipe.id}" min=1 value=1 oninput="craftChange(event)">
					<button class="btn id-${recipe.id}" onclick="craft(event)" data-locked="${recipe.locked }">Craft</button>
				</div>

				<a class="info" href="/crafting/details/${recipe.id}">
					<img src="/static/res/img/info.svg" alt="Info">
				</a>
			</div>`

		html += html_recipe
	})
	return html
}


// helper function. Updates disabled-status of crafting for each recipe by triggering the onInput-eventhandler of .craftNum
function updateRecipeStatus() {
	var event = new Event('input')

	Array.from(document.getElementsByClassName("craftNum")).forEach(num_input => {
		num_input.dispatchEvent(event)
	})
}


/*
	callbacks triggered on dragging of tables
*/

function drag_start_callback(element) {

	// show table recipes
	tableChange(element.id, false)
}

function drag_end_callback() {
	// save new ordering to db
	var tables = [...document.getElementsByClassName('table')]
		.map(table => { return parseInt(/\d+/.exec(table.id)) })
		.filter(table_id => typeof table_id === 'number');

	post({ table_ordering: tables }, reaction, reaction, false)
}

/*
	EVENT HANDLERS
*/

// select a different table and show its recipes instead of the current ones
function tableChange(id, display_spinner=true) {
	var selected_tag = document.getElementById(/*"tid-" +*/ id)

	// markup for selection
	Array.from(document.getElementsByClassName("table selected")).forEach(table => {table.classList.remove("selected")})
	selected_tag.classList.add("selected")

	// set topic to selected
	document.getElementsByTagName("title")[0].innerHTML = selected_tag.dataset.title
	document.getElementsByClassName("topic")[0].innerHTML = selected_tag.dataset.title

	post({ table: /\d+/.exec(id)[0] }, data => {
		document.getElementsByClassName("recipes")[0].innerHTML = constructRecipes(data.recipes)

		// disable recipes where necessary
		updateRecipeStatus()
	}, null, display_spinner)
}


// adapt required amounts onInput-event of input-element[type:number]
function craftChange({ currentTarget }) {

	// amount of product
	var num = parseInt(currentTarget.value || 0)

	// get common id (used as class on html)
	var id_class = ""
	currentTarget.classList.forEach(e => {if (e.startsWith("id-")) id_class = e});

	var row = document.getElementsByClassName("row " + id_class)[0]

	// should crafting be allowed?
	var disable_btn = document.getElementsByClassName("btn " + id_class)[0].dataset.locked == "true"

	// calc amount for products
	Array.from(row.getElementsByClassName("pnum")).forEach(pnum_tag => {
		var base = parseFloat(pnum_tag.dataset.default)
		pnum_tag.innerHTML = (base * num).toFixed(1).toString().replace(".", ",").replace(",0", "")		// round to one digit after decimal sign, leave out if it is a 0
	})

	// calc amount for ingredients
	Array.from(row.getElementsByClassName("inum ")).forEach(inum_tag => {
		var needed_tag = inum_tag.getElementsByClassName("needed-num")[0]
		var own_tag = inum_tag.getElementsByClassName("own-num")[0]

		// calc needed
		var needed_num = parseFloat(needed_tag.dataset.default) * num
		needed_tag.innerHTML = needed_num.toFixed(1).toString().replace(".", ",").replace(",0", "")		// round to one digit after decimal sign, leave out if it is a 0

		// still own sufficient amount?
		if (needed_num > parseFloat(own_tag.innerHTML)) {
			inum_tag.classList.add("insufficient")
			disable_btn = true
		}
		else {
			inum_tag.classList.remove("insufficient")
		}
	})

	// disable btn?
	row.getElementsByClassName("btn")[0].disabled = disable_btn
}


// craft num of items
function craft({ currentTarget }) {

	if (currentTarget.disabled) return

	// get common recipe_id
	var id_class = ""
	currentTarget.classList.forEach(e => { if (e.startsWith("id-")) id_class = e })

	// get num produced items
	var num = document.getElementsByClassName("craftNum " + id_class)[0].value
	var id = /\d+/.exec(id_class)[0]

	post({ craft: id, num: num}, _ => {

		// if crafted element was a table, enable it
		Array.from(document.getElementsByClassName("product " + id_class)).forEach(product => {
			var pid = -1
			product.classList.forEach(e => { if (e.startsWith("pid-")) pid = /\d+/.exec(e) })

			document.getElementById("tid-" + pid)?.classList.add("available")
		})

		// reload by table
		var selected_table = document.getElementsByClassName("table selected")
		if (selected_table.length)
			tableChange(selected_table[0].id)

		// reload by search term
		else {
			var event = new Event('click');
			document.getElementById("search-btn").dispatchEvent(event)
		}
	})
}


// used to autocomplete search bar while typing. Event fires onInput-change
// retrieve a list of entries

// need to add
// oninput="searchChange(event)"
// on input again, temporarily disabled
function searchChange({ currentTarget }) {
	var text = currentTarget.value

	// post -> get fitting entries back
	post({search: text}, data => {

		// repopulate datalist of searchbar
		var datalist = document.getElementById("item-search")
		datalist.innerHTML = ""
		data.res.forEach(item => {
			datalist.append(`<option value="${item.name}"></option>`)
		})

		// TODO figure out autocomplete in searchbar
		//document.getElementsByClassName("recipes")[0].innerHTML = constructRecipes(data.recipes)

		// disable recipes where necessary
		//updateRecipeStatus()
	}, reaction, false)		// false => don't display spinner
}


// search submitted, retrieve recipes and display them. Unselect table in sidebar
function search() {
	var text = document.getElementById("search-input").value

	post({ search_btn: text }, data => {

		// reset table selection
		Array.from(document.getElementsByClassName("table selected")).forEach(table => { table.classList.remove("selected") })

		// set topic to search text
		document.getElementsByTagName("title")[0].innerHTML = `Suche nach '${text}'`
		document.getElementsByClassName("topic")[0].innerHTML = `Suche nach '${text}'`

		// display recipes with search term as product and ingredient
		document.getElementsByClassName("recipes")[0].innerHTML =
			`<h1>ALS PRODUKT:</h1>${constructRecipes(data.as_product, true) || `<div>-</div>`}
			<h1>ALS ZUTAT:</h1>${constructRecipes(data.as_ingredient, true) || `<div>-</div>`}`

		// adapt recipe status
		updateRecipeStatus()
	})
}


document.addEventListener("DOMContentLoaded", () => {

	// load page content

	// get all recipes of first table
	tableChange(document.getElementsByClassName("table")[0].id)


	// initially disable recipes where necessary
	updateRecipeStatus()



	// event handlers
	init_draggable_reorder()

	// send input data per btn event on keydown of enter key
	Array.from( document.getElementsByTagName("input") ).forEach(el => el.addEventListener("keydown", (e) => {
		// on keydown of enter, i.e. ascii-code 13
		if (e.keyCode === 13) {

			// click (first) sibling btn
			e.currentTarget.parentElement.getElementsByClassName("btn")[0].click();
		}
	}))
})
