let item_id;

// assemble details box for item beneath inventory
function openDetails(id) {
	post({details: id}, data => {
		item_id = id;

		// mapping
		document.querySelector("#overlay__icon").src = data.icon
		document.querySelector("#overlay__icon").alt = data.name
		document.querySelector("#overlay__name").innerText = data.name || "-"

		document.querySelector("#overlay__owned").innerText = data.own.toLocaleString("de-DE") || "-"

		document.querySelector("#overlay__spezial").innerText = data.spezial.join(", ") || "-"
		document.querySelector("#overlay__wissen").innerText = data.wissen.join(", ") || "-"

		document.querySelector("#overlay__kategory").innerText = data.kategory || "-"
		document.querySelector("#overlay__duration").innerText = data.duration || "-"
		document.querySelector("#overlay__description").innerText = data.description || "-"

		var values = data.values
		if (data.other) values = values ? [values, data.other].join(", ") : data.other
		document.querySelector("#overlay__values").innerText = values || "-"

		document.querySelector("#overlay__stufe").innerText = data.ab_stufe || 0

		document.querySelector("#overlay__table").innerHTML = data.table.icon || data.table.name ?
		`<div class="overlay__item"><img src="${data.table.icon}" alt="${data.table.name}">
		<span>${data.table.name}</span></div>` : `-`

		const ingredients = data.ingredients.map(i => `<div class="overlay__item"><img src="${i.icon}" alt="${i.name}"><span>${i.num.toLocaleString("de-DE") || "?"}x ${i.name}</span></div>`)
		document.querySelector("#overlay__ingredients").innerHTML = ingredients.join("") || "-"
		document.querySelector("#overlay__num-prod").innerText = data.num_prod.toLocaleString("de-DE") || "-"

		document.querySelector("#overlay__link").href = data.link
		document.querySelector("#overlay__wooble_sell").dataset.cost = data.wooble_sell
		document.querySelector("#overlay__wooble_sell").innerText = data.wooble_sell.toLocaleString("de-DE")
		document.querySelector("#overlay__wooble_buy").dataset.cost = data.wooble_buy
		document.querySelector("#overlay__wooble_buy").innerText = data.wooble_buy.toLocaleString("de-DE")
		document.querySelector("#overlay__sell").max = document.querySelector("#overlay__owned").innerText

		// set woobles
		document.querySelectorAll(".overlay .mini-form input").forEach(input => input.dispatchEvent(new Event("input")));

		// display overlay
		document.querySelector(".overlay").classList.toggle("overlay--perk", data.is_perk);
		document.querySelector(".overlay").classList.add("overlay--visible");

		window.scrollTo({ top: 0, behavior: 'smooth' });
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
	const per_item = parseFloat(form.querySelector("#overlay__wooble_buy, #overlay__wooble_sell").dataset.cost);
	form.querySelector(".wooble_sum").innerText = (per_item * event.target.value).toLocaleString("de-DE");
}


// search submitted, display according items
function search() {
	const text = document.querySelector("#search-input").value.toLowerCase();

	[...document.querySelectorAll(".grid .item")].forEach(item => {
		item.classList.toggle("item--visible", item.dataset.name.toLowerCase().includes(text));
	});
}