import json
from typing import List, Tuple

from django.db import models

from time_space.enums import NodeType, Signal
from time_space.models.interfaces import Node


class Net(models.Model):

	class Meta:
		verbose_name = "Netz"
		verbose_name_plural = "Netze"

	startNode = models.TextField(default="")
	text = models.TextField(null=True, blank=True)

	def __str__(self):
		return "{} (Netz)".format(self.text[:50] if self.text else '')

	def getStartNode(self):
		if not self.startNode or not len(self.startNode): return None

		return Node.toNode(*json.loads(self.startNode))


	def getLayers(self):

		if 'layers' not in self.__dict__.keys():
			self._constructLayers()

		return self.layers

	def _setLayers(self, layers):
		self.layers = layers


	def updateLayers(self):
		del self.__dict__["layers"]

		return self.getLayers()


	def setStartNode(self, node):
		if not node:
			raise ValueError("Will not set Start Node to nothing")

		self.startNode = json.dumps(Node.toSpecs(node))
		self.save(update_fields=["startNode"])

	# recursive walk through graph
	# breadth-first search
	# in case of loop structures: stop if previously visited was hit
	def sendSignal(self, signal: Signal):

		if not self.getStartNode():
			return

		# process input signal
		initialLayer = {self.getStartNode(): [signal]}
		outputs, nodes = self._sendSignal(initialLayer)

		# postprocess (outputs)
		outputs = sorted(outputs, key=lambda output: int(output.split(":")[0].replace("#", "").strip()))
		for node in nodes:
			outputs = node.postprocessSignal(outputs)

		return outputs

	def _sendSignal(self, layer) -> Tuple[List[str], List[Node]]:

		nextLayer = {}
		outputs = []

		for toNode, signals in layer.items():

			# gate processes signal
			processedSignal, output = toNode.processSignal(signals)
			if output: outputs.append(output)
			print("{} : {} -> {}".format(toNode, signals, output))

			# signal did not pass through, stop here
			if processedSignal is None:
				continue

			# add next nodes to new layer
			for nodeSpec in toNode.getNext():
				node = Node.toNode(*nodeSpec)

				if node not in nextLayer.keys(): nextLayer[node] = []

				nextLayer[node].append(processedSignal)
		print()
		allNodes = list(layer.keys())

		# process underlying layers
		if nextLayer:
			deeper_outputs, deeper_nodes = self._sendSignal(nextLayer)
			outputs += deeper_outputs
			allNodes += deeper_nodes
		
		return outputs, allNodes


	# randomGate, random location (set next[] on new and existing nodes)
	def _addGate(self):
		# TODO implement logic
		# TODO save new gate
		pass


	# random fissure after random gate (no fissure should not have nodes after)
	def _addTemporalFissure(self):
		# TODO implement logic
		# TODO save new fissure
		pass


	def addNode(self, nodeType: NodeType):
		return self._addNode( NodeType(nodeType).toModel() )

	def _addNode(self, model: Node):
		# TODO wanna save them on the Net?
		return model.objects.create()


	def removeNodeSpec(self, nodeType, nodeId):
		return self.removeNode(Node.toNode(nodeType, nodeId))

	def removeNode(self, node):
		node.destroy()
		self._constructLayers()


	def addNodeBranch(self, nodes):

		if not nodes: return

		for i in range(len(nodes) - 1):

			node = nodes[i]
			nextNode = nodes[i+1]

			node.addToNext(nextNode)

		if self.getStartNode() is None:
			self.setStartNode(nodes[0])

		self._constructLayers()


	# recursive walk through graph
	# breadth-first search
	# in case of loop structures: stop if previously visited was hit
	def _constructLayers(self):
		if not self.getStartNode():
			self._setLayers([[]])
			return

		layers = self.__constructLayers([set([self.getStartNode()])], [])

		self._setLayers(layers)
		self._deleteUnusedReferences()

	def __constructLayers(self, layers, history):

		nextLayer = []
		currentLayer = layers[-1]
		deleteFromCurrentLayer = []

		for toNode in currentLayer:

			# detected loop, stop here
			if toNode in history:
				deleteFromCurrentLayer.append(toNode)
				continue

			# gate processes signal
			history.append(toNode)

			# add next nodes to new layer
			for n in toNode.getNext():
				try:
					nextLayer.append(Node.toNode(*n))
				except:
					toNode.removeFromNext(*n)

		# postprocess current layer
		for n in deleteFromCurrentLayer:
			currentLayer.remove(n)

		# process underlying layers recursively
		if nextLayer:
			layers.append(set(nextLayer))
			return self.__constructLayers(layers, history)

		# deepest layer found, return from recursion
		return layers if len(layers[-1]) else layers[:-1]


	def _deleteUnusedReferences(self):
		layers = self.getLayers()

		for index, layer in enumerate(layers):

			# gotten to last layer, delete all potential children since there is no layer afterwards
			if index + 1 >= len(layers):
				for node in layer:
					children = node.getNext()
					for child in children:
						node.removeFromNext(*child)
				continue

			# see if a child is still in the cleaned-up version. if not, delete reference of parent
			parents = layer
			current = layers[index + 1]

			for parent in parents:
				allChildren = parent.getNext()

				for child in allChildren:
					child = Node.toNode(*child)

					if child not in current:
						parent.removeNodeFromNext(child)
