document.addEventListener("DOMContentLoaded", () => {
	const restriction = document.querySelector("#restriction");
	const options = [...document.querySelectorAll("option")].map(tag => tag.value);

	document.querySelector("[name=name]").addEventListener("input", ({ currentTarget }) => {
		restriction.style.display = options.includes(currentTarget.value) ? "none" : "flex";
	})
})
