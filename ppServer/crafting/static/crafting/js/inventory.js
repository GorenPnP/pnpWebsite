let item_id;

// assemble details box for item beneath inventory
function openDetails(id) {
	post({details: id}, data => {
		item_id = id;

		// mapping
		document.getElementById("overlay__icon").src = data.icon
		document.getElementById("overlay__icon").alt = data.name
		document.getElementById("overlay__name").innerHTML = data.name || "-"

		document.getElementById("overlay__owned").innerHTML = data.own.toLocaleString("de-DE") || "-"

		document.getElementById("overlay__spezial").innerHTML = data.spezial.join(", ") || "-"
		document.getElementById("overlay__wissen").innerHTML = data.wissen.join(", ") || "-"

		document.getElementById("overlay__kategory").innerHTML = data.kategory || "-"
		document.getElementById("overlay__duration").innerHTML = data.duration || "-"
		document.getElementById("overlay__description").innerHTML = data.description || "-"

		var values = data.values
		if (data.other) values = values ? [values, data.other].join(", ") : data.other
		document.getElementById("overlay__values").innerHTML = values || "-"

		document.getElementById("overlay__stufe").innerHTML = data.ab_stufe || 0

		document.getElementById("overlay__table").innerHTML = data.table.icon || data.table.name ?
		`<img src="${data.table.icon}" alt="${data.table.name}">
		<span>${data.table.name}</span>` :
		`-`

		var ingredients = data.ingredients.map(i => { return `<div class="ingredient"><img src="${i.icon}" alt="${i.name}"><span>${i.num.toLocaleString("de-DE") || "?"}x ${i.name}</span></div>` })
		document.getElementById("overlay__ingredients").innerHTML = ingredients.join("") || "-"
		document.getElementById("overlay__num-prod").innerHTML = data.num_prod.toLocaleString("de-DE") || "-"

		document.getElementById("overlay__link").href = data.link
		document.getElementById("overlay__wooble_sell").dataset.cost = data.wooble_sell
		document.getElementById("overlay__wooble_sell").innerText = data.wooble_sell.toLocaleString("de-DE")
		document.getElementById("overlay__wooble_buy").dataset.cost = data.wooble_buy
		document.getElementById("overlay__wooble_buy").innerText = data.wooble_buy.toLocaleString("de-DE")
		document.getElementById("overlay__sell").max = document.getElementById("overlay__owned").innerText

		// set woobles
		document.querySelectorAll(".overlay .mini-form input").forEach(input => input.dispatchEvent(new Event("input")));

		// display overlay
		document.getElementsByClassName("overlay")[0].style.display = "grid"
	})
}


function buy_item() {
	const num = document.querySelector("input#input-buy").value;
	post(
		{item_id, num, buy: true},
		_ => location.reload(),
		error => alert(error.response.data.message)
	);
}

function sell_item() {
	const num = document.querySelector("input#input-sell").value;
	post(
		{item_id, num, sell: true},
		_ => location.reload(),
		error => alert(error.response.data.message)
	);
}


function update_woobles(event) {
	const form = event.target.closest(".mini-form");
	const per_item = parseInt(form.querySelector("#overlay__wooble_buy, #overlay__wooble_sell").dataset.cost);
	form.querySelector(".wooble_sum").innerText = (per_item * event.target.value).toLocaleString("de-DE");
}


// search submitted, retrieve recipes and display them. Unselect table in sidebar
function search() {
	const text = document.querySelector("#search-input").value;

	post({ search_btn: text }, data => {
		document.querySelectorAll(".grid").forEach(grid => grid.innerHTML = "");

		const dummy = document.createElement("div");

		data.items
			.map(item => ({
				item,
				html: `<div class="item ${ !item.owned ? 'item--unowned' : ''}" onclick="openDetails(${ item.id })">
					<img src="${ item.icon_url }" alt="${ item.name }">
						${ item.num ? ('<span class="num">' + item.num.toLocaleString('de-DE') + '</span>') : ''}
					</div>`,
			})
		)
		.forEach(({html, item}) => {
			dummy.innerHTML = html;
			document.querySelector(`.grid--category-${ item.category.replace(" ", "").replace("/", "") }`).appendChild(dummy.firstChild);
		});

		dummy.remove();

		// trigger css re-calc
		window.getComputedStyle();
	})
}