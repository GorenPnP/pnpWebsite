// assemble details box for item beneath inventory
function openDetails(id) {
	post({details: id}, data => {

		// mapping
		document.getElementById("overlay__icon").src = data.icon
		document.getElementById("overlay__icon").alt = data.name
		document.getElementById("overlay__name").innerHTML = data.name || "-"

		document.getElementById("overlay__owned").innerHTML = parseFloat(data.own)?.toFixed(1).replace(".", ",").replace(",0", "") || "-"

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

		var ingredients = data.ingredients.map(i => { return `<div class="ingredient"><img src="${i.icon}" alt="${i.name}"><span>${parseFloat(i.num)?.toFixed(1).replace(".", ",").replace(",0", "") || "?"}x ${i.name}</span></div>` })
		document.getElementById("overlay__ingredients").innerHTML = ingredients.join("") || "-"
		document.getElementById("overlay__num-prod").innerHTML = parseFloat(data.num_prod)?.toFixed(1).replace(".", ",").replace(",0", "") || "?"

		document.getElementById("overlay__link").href = data.link

		// display overlay
		document.getElementsByClassName("overlay")[0].style.display = "grid"
	})
}


// add item to inventory without crafting
function addItem() {
	var num = document.getElementById("num").value
	var item = document.getElementsByTagName("option")[document.getElementById("items").selectedIndex].value

	post({num, item}, _ => location = location) // reload afterwards
}


document.addEventListener("DOMContentLoaded", () => {

})
