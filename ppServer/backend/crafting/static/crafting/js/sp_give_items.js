// add item to inventory without crafting
function addItem() {
	Array.from(document.getElementsByClassName("alert")).forEach(tag => tag.style.display = "none")

	var num = document.getElementById("num").value

	var items = document.getElementById("items")
	var item = items?.getElementsByTagName("option")[items?.selectedIndex].value

	var profiles = document.getElementById("profiles")
	var profile = profiles?.getElementsByTagName("option")[profiles?.selectedIndex].value

	post({ num, profile, item },
				_ => {
					document.getElementsByClassName("alert--success")[0].innerHTML = "Hat geklappt"
					document.getElementsByClassName("alert--success")[0].style.display = "block"
				},
				_ => {
					document.getElementsByClassName("alert--error")[0].innerHTML = "Hat nicht geklappt"
					document.getElementsByClassName("alert--error")[0].style.display = "block"
				}
			)
}
