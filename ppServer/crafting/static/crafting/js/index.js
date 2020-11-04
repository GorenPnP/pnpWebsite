function toggleCheckbox() {
	document.getElementById('restriction').classList.toggle('checked');
	document.getElementById("hiddenCheckbox").checked = document.getElementById('restriction').classList.contains('checked')
}


document.addEventListener("DOMContentLoaded", () => {

	document.getElementById("name").addEventListener("keydown", (e) => {
		// on keydown of enter, i.e. ascii-code 13
		if (e.keyCode === 13) {
			document.getElementById("search-btn").click();
		}
	})

	document.getElementById("name").addEventListener("input", ({ currentTarget }) => {
		document.getElementsByClassName("check")[0].style.display = !Array.from(document.getElementsByTagName("option")).some(e => e.value.includes(currentTarget.value)) ? "grid" : "none"
	})
})
