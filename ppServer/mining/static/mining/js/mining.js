var materials;
var currentMaterial;
var currentRigidity;

var amountsMined = {};

function mining() {
	if (miningBlocked) {return;}
	
    // subtract from currentRigidity (need to know about tool)
    updateRigidity(currentRigidity - 1);
	
    if (currentRigidity <= 0) {
        return addBlocksToInventory();
    }
}

var miningBlocked = false;
function addBlocksToInventory() {
	miningBlocked = true;
	const timer = setTimeout(() => {
		alert(`Die Verbindung zum Server ist ganz schön langsam / nicht vorhanden. Eventuell Seite nochmal neu laden.\n` +
			`Aber keine Angst, der Loot wurde außer dem Letzten hier gespeichert ;)`);
	}, 1000);

	return post({id: currentMaterial.id}, success = function(data, _) {
		clearTimeout(timer);

		displayAmountMined(JSON.parse(data.amount));
		initMaterial(data.id);

		miningBlocked = false;
	}, undefined, false);
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
