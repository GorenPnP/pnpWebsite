from copy import deepcopy
import json

from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse

from .models import Net
from .models.time_fissures import Looper
from .models.gates import Mirror
from .models.interfaces import Node
from time_space.enums import NodeType, Signal


def index(request):

	context = {
		"topic": "Zeituhr",
		"plus_url": "/time_space/createNet",
		"nets": Net.objects.all()
	}
	return render(request, "time_space/index.html", context)


def net(request, id):

	net = get_object_or_404(Net, id=id)

	if request.method == "GET":
		node_designs = netDesign().values()
		design = {
			"time_fissures": [n for n in node_designs if n["id"] < 30],
			"time_annanomalies": [n for n in node_designs if n["id"] >= 30 and n["id"] < 70],
			"room_fissures": [n for n in node_designs if n["id"] >= 70 and n["id"] < 100],
			"gates": [n for n in node_designs if n["id"] >= 100],
		}
		return render(request, "time_space/net.html", {"topic": net.text, "design": design})

	if request.method == "POST":

		json_dict = json.loads(request.body.decode("utf-8"))
		cause = json_dict["cause"]

		if cause == "load":
			return JsonResponse(loadNet(net))


		if cause == "save":
			nodes = json_dict["nodes"]
			edges = json_dict["edges"]

			newSpecStrings = [n["id"] for n in nodes]

			# get a list from net of all used nodes
			netSpecs = []
			for layer in net.getLayers():
				netSpecs +=  [Node.toSpecs(n) for n in layer]

			# delete all those which are not in received nodes
			for spec in netSpecs:

				specString = "{}-{}".format(*spec)

				# delete node
				if specString not in newSpecStrings:
					net.removeNodeSpec(*spec)

				else:
					# delete all known, leaving newly added nodes ...
					newSpecStrings.remove(specString)

			# ... and add all which haven't been in there before
			connectedNodes = set()
			for edge in edges:
				connectedNodes.add(edge["from"])
				connectedNodes.add(edge["to"])

			for newSpecString in newSpecStrings:

				# test if there are edges connecting the new node
				# if not, don't instantiate it
				if newSpecString not in connectedNodes: continue

				# add new node
				nodeType = int( newSpecString.split("-")[0] )

				newNode = net.addNode(nodeType)

				# update edges with new id of node
				nodeSpecString = "{}-{}".format(nodeType, newNode.id)
				for edge in edges:
					if edge["from"] == newSpecString: edge["from"] = nodeSpecString
					if edge["to"] == newSpecString:   edge["to"] = nodeSpecString


			# get all new edges
			newEdges = {}
			for e in edges:
				if e["from"] not in newEdges.keys(): newEdges[e["from"]] = []

				toSpec = [int(i) for i in e["to"].split("-")]
				newEdges[e["from"]].append(Node.toNode( *toSpec) )

			# go through all nodes and update their edges (add & delete) where changed
			for nodeSpecString, next in newEdges.items():

				nodeSpec = [int(i) for i in nodeSpecString.split("-")]
				node = Node.toNode(*nodeSpec)

				# delete all old
				childSpecs = node.getNext()
				for child in childSpecs:
					node.removeFromNext(*child)

				# create new
				for n in next:
					node.addNodeToNext(n)

			# update graph
			net.updateLayers()

			return JsonResponse(loadNet(net))

		if cause == "command":
			valid_command = json_dict["command"] in [m.value for m in Signal.__members__.values()]
			if not valid_command:
				return JsonResponse({"message": "invalid"})

			signal = Signal(json_dict["command"])
			outputs = net.sendSignal(signal)
			return JsonResponse({"status": "valid", "outputs": outputs})


def createNet(request):
	net = Net.objects.create()
	return redirect(reverse("time_space:net", args=[net.id]))


def netDesign():

	gate_design = {
		"color": "#ddd",
		"shape": "ellipse",
		"font": { "color": "black" }
	}
	time_fissure_blue = {
		"color": "#00dcf5",
		"shape": "box",
		"font": { "color": "black" }
	}
	time_fissure_red = {
		"color": "#de073c",
		"shape": "box",
		"font": { "color": "white" }
	}
	time_fissure_yellow = {
		"color": "#FFB61E",
		"shape": "box",
		"font": { "color": "black" }
	}
	time_fissure_black = {
		"color": "black",
		"shape": "box",
		"font": { "color": "white" }
	}
	time_fissure_transparent = {
		"color": {
			"border": "black",
			"background": "#808080"
		},
		"shape": "box",
		"font": { "color": "black" }
	}

	design = {
		NodeType.Mirror: gate_design,
		NodeType.Inverter: gate_design,
		NodeType.Aktivator: gate_design,
		NodeType.Switch: gate_design,
		NodeType.Konverter: gate_design,
		NodeType.Barriere: gate_design,
		NodeType.Manadegenerator: gate_design,
		NodeType.Manabombe: gate_design,
		NodeType.Supportgatter: gate_design,
		NodeType.Teleportgatter: gate_design,
		NodeType.Sensorgatter: gate_design,
		NodeType.Tracinggatter: gate_design,

		NodeType.Linearriss: time_fissure_blue,
		NodeType.Liniendeletion: time_fissure_black,
		NodeType.Splinter: time_fissure_red,
		NodeType.Duplikator: time_fissure_blue,
		NodeType.Looper: time_fissure_blue,
		NodeType.Timelagger: time_fissure_transparent,
		NodeType.Timedelayer: time_fissure_blue,
		NodeType.Runner: time_fissure_blue,
		NodeType.Metasplinter: time_fissure_yellow,
	}

	designs = {}
	for node_type in NodeType:

		node_design = deepcopy(design[node_type]) if node_type in design else {}
		node_design.update({
			"id": node_type.value,
			"label": node_type.name,
			"heightConstraint": {"minimum": 20}
		})
		designs[node_type.value] = node_design

	return designs

def getNetDesign(request):
	return JsonResponse(netDesign())

def loadNet(net: Net):
	design = netDesign()

	nodes = []
	edges = []
	for layer in net.getLayers():
		for node in layer:
			nodeType = NodeType.fromModel(type(node))
			n = deepcopy(design[nodeType]) if nodeType in design else {}
			n.update({
				"id": "{}-{}".format(n["id"], node.id),
				"heightConstraint": {"minimum": 20}
			})
			nodes.append(n)

			for toNodeSpec in node.getNext():
				edges.append({
					"from": "{}-{}".format(nodeType, node.id),
					"to": "{}-{}".format(toNodeSpec[0], toNodeSpec[1]),
					"color": "#ddd"
				})

	return {"nodes": nodes, "edges": edges}
