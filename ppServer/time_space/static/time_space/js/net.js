var network = null;
var nodeChoices = null;

var nextId = -1	// handle new ids (all negative, desc) of nodes to replace in backend
var nextNodeType;

const locales = {
	de: {
		addDescription: "Klicke auf eine freie Stelle, um ein neues Element zu plazieren.",
		addEdge: "Verbindung hinzuf\u00fcgen",
		addNode: "Element hinzuf\u00fcgen",
		back: "Zur\u00fcck",
		close: "Schließen",
		createEdgeError: "Es ist nicht m\u00f6glich, Verbindungen mit Clustern zu verbinden.",
		del: "L\u00f6sche Auswahl",
		deleteClusterError: "Cluster k\u00f6nnen nicht gel\u00f6scht werden.",
		edgeDescription: "Klicke auf ein Element und ziehe die Verbindung zu einem Anderen, um diese zu verbinden.",
		edit: "Bearbeiten",
		editClusterError: "Cluster k\u00f6nnen nicht bearbeitet werden.",
		editEdge: "Verbindung bearbeiten",
		editEdgeDescription: "Klicke auf die Punkte und verschiebe diese auf ein anderes Element.",
		editNode: "Element bearbeiten",
	}
}

const options = {
	autoResize: true,
	locale: 'de',
	locales,
	height: '100%',
	width: '100%',
	layout: {
		hierarchical: {
			sortMethod: "directed",
			shakeTowards: "roots",
			direction: "DU"
		},
	},
	edges: {
		smooth: true,
		arrows: { to: true },
		color: "white"
	},
	interaction: {
		hover: true,
		hoverConnectedEdges: true,
		navigationButtons: true,
		multiselect: true
	},
	manipulation: {
		addNode: (nodeData, callback) => {
			nodeData = {...nodeData, ...nextNodeType, id: `${nextNodeType.id}-${nextId--}`};

			callback(nodeData);
		},
		addEdge: function (edgeData, callback) {
			if (edgeData.from !== edgeData.to) {
				callback(edgeData);
			} else {
				alert("Zum Verbinden gedrückt halten.")
				callback({})
			}
		},
		editNode: function (nodeData, callback) {
			nodeData.label = '...';
			callback(nodeData);
		},
		editEdge: true,
	}
	// configure: {
	// 	enabled: true,
	// 	filter: 'physics',
	// }
};


var blockToFlexObserver = new MutationObserver(function (mutations) {
	mutations.forEach(mutationRecord => {
		if (mutationRecord.target.style.display === "block")
			mutationRecord.target.style.display = "flex"
	});
});

function loadStyles() {
	return fetch('/time_space/netDesign').then(res => res.json());
}

function loadGraph(nodes, edges) {

	if (network) {
		network.setData({nodes, edges})
		return
	}

	// create a network
	var container = document.getElementById('mynetwork');

	// initialize your network!
	network = new vis.Network(container, {nodes, edges}, options);
}

document.addEventListener("DOMContentLoaded", async _ => {

	nodeStyles = await loadStyles();
	document.querySelector("#add-node-select").addEventListener("change", function(event) {
		const nodeType_id = event.target.value;
		nextNodeType = nodeStyles[nodeType_id];
	});
	document.querySelector("#add-node-select").dispatchEvent(new Event('change'))
	

	document.querySelector('#terminal form').addEventListener("keydown", function(event) {
		if (event.key === "Enter") {
			event.preventDefault();
			post({
					cause: "command",
					command: this.querySelector('#command').value
				},
				({status, outputs}) => {
					if (status === "valid") {
						document.querySelector("output").innerHTML = outputs.join("<br>")
					}
				},
				err => {console.error(err)}
			);
		}
	});

	post({cause: "load"}, data => {
		loadGraph(data.nodes, data.edges)

		// display button tags in manipulation bar (the one on top)
		const targetManipulation = document.querySelector('.vis-manipulation')
		const targetEdit = document.querySelector('.vis-edit-mode')
		blockToFlexObserver.observe(targetManipulation, { attributes: true, attributeFilter: ['style'] })
		blockToFlexObserver.observe(targetEdit, { attributes: true, attributeFilter: ['style'] })
		




		// add custom save-button
		document.querySelector(".vis-network").appendChild(
			document.createRange().createContextualFragment(
				`<button class="vis-button vis-save" style="touch-action: pan-y; user-select: none;" >
				<div class="vis-label">Speichern</div>
			</button>
		`))

		// add on click to save-button
		document.querySelector(".vis-save").addEventListener("click", __ => {
			const nodes = network.body.data.nodes.map(n => ({ id: n.id }))
			const edges = network.body.data.edges.map(e => ({ from: e.from, to: e.to }))

			post({ cause: "save", nodes, edges },
			save_data => {
				loadGraph(save_data.nodes, save_data.edges)
			},
			err => {
				console.error(err)
				alert("Konnte nicht gespeichert werden. " + err.message)
			})
		})
	})
})
