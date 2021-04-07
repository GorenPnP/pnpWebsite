var materials;
var currentMaterial;
var currentRigidity;

var amountsMined = {}

function mining() {

    // subtract from currentRigidity (need to know about tool)
    updateRigidity(currentRigidity - 1);

    if (currentRigidity <= 0) {
        return addBlocksToInventory();
    }
}

function addBlocksToInventory() {
	return post({id: currentMaterial.id}, success = function(data, _) {
		displayAmountMined(JSON.parse(data.amount));
		initMaterial(data.id);
	}, undefined, false)
}

function displayAmountMined(drops) {
	updateAmountMined(drops);

	for (const drop of drops) {
		console.log(`+${drop[0]} ${drop[1]}`);
	}
}

function initMaterial(materialId) {
	updateMaterial(materials.find(material => material.id === materialId));
	updateRigidity(currentMaterial.rigidity);
}

window.addEventListener("DOMContentLoaded", () => {
	materials = JSON.parse(document.querySelector("#materials").innerHTML);

	const initial_material_id = parseInt(document.querySelector("#initial_material_id").innerHTML)
	initMaterial(initial_material_id);
})
