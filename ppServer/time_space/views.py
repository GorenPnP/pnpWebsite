import json
from time_space.models.time_fissures import Looper
from time_space.models.gates import Mirror
from time_space.models.interfaces import Node
from time_space.enums import NodeType
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Net

def index(request):

	context = {
		"topic": "Zeituhr",
		"nets": Net.objects.all()
	}
	return render(request, "time_space/index.html", context)


def net(request, id):

	net = get_object_or_404(Net, id=id)

	if request.method == "GET":
		return render(request, "time_space/net.html", {"topic": net.text})

	if request.method == "POST":

		json_dict = json.loads(request.body.decode("utf-8"))
		cause = json_dict["cause"]

		if cause == "load":

			# TODO: add list of all nodeTypes for adding them in the view
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

			# return new net.getLayers (make function out of 'if cause == "load"' above and use it here)

			return JsonResponse(loadNet(net))


def createNet(request):

	net = Net.objects.create()
	e0 = Mirror()
	e1 = Mirror()
	e2 = Mirror()
	e33 = Mirror()
	L0 = Looper()

	[g.save() for g in [e0, e1, L0]]

	branches = [
						[e0, e1, 					e2,						L0],
						[e1,   				Mirror()],
						[e0, Mirror(), 							L0],
						[e0, 							e2,    				Mirror(), e33, Mirror()],
						[e2,    				Mirror()],
						[e33, Mirror()],
	]
	# branches = [
	# 								[e0, e1, 					e2,						L0],
	# 									[e1,   				Mirror()],
	# 									[e2,    				Mirror()]
	# ]
	# branches = [
	# 	[e0, e1],
	# 	[e1, Mirror()],
	# 	[e1, Mirror(), Mirror()],
	# ]

	for b in branches:
		for n in b: n.save()
		net.addNodeBranch(b)

	return redirect("time_space:index")


def loadNet(net: Net):

	colors = {
		NodeType.Mirror: "yellow",
		NodeType.Looper: "green"
	}

	shape = {
		NodeType.Mirror: "ellipse",
		NodeType.Looper: "box"
	}

	nodes = []
	edges = []
	for layer in net.getLayers():
		for node in layer:
			nodeType = NodeType.fromModel(type(node))
			nodes.append({
				"id": "{}-{}".format(nodeType, node.id),
				"label": type(node).__name__,
				"color": colors[nodeType],
				"shape": shape[nodeType]
			})

			for toNodeSpec in node.getNext():
				edges.append({
					"from": "{}-{}".format(nodeType, node.id),
					"to": "{}-{}".format(toNodeSpec[0], toNodeSpec[1]),
					"color": "#ddd"
				})

	return {"nodes": nodes, "edges": edges}
