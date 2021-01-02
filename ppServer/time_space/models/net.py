import json

from time_space.models.interfaces import Node

from django.db import models

from time_space.enums import NodeType, Signal


class Net(models.Model):

	class Meta:
		verbose_name = "Netz"
		verbose_name_plural = "Netze"

	startNode = models.TextField(default="")
	text = models.TextField(null=True, blank=True)
	#layers = []

	def __str__(self):
		return "{} (Netz)".format(self.text[:50])

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
		self.save()

	# recursive walk through graph
	# breadth-first search
	# in case of loop structures: stop if previously visited was hit
	def sendSignal(self, signal: Signal):

		if not self.getStartNode():
			return

		initialLayer = {self.getStartNode(): [signal]}
		self._sendSignal(initialLayer)

	def _sendSignal(self, layer):

		nextLayer = {}
		for toNode, signals in layer.items():

			# gate processes signal
			processedSignal = toNode.processSignal(signals)

			# signal did not pass through, stop here
			if processedSignal is None:
				continue

			# add next nodes to new layer
			for nodeSpec in toNode.getNext():
				node = Node.toNode(*nodeSpec)

				if node not in nextLayer.keys(): nextLayer[node] = []

				nextLayer[node].append(processedSignal)
		print()
		# process underlying layers
		if nextLayer:
			self._sendSignal(nextLayer)


	# randomGate, random location (set next[] on new and existing nodes)
	def _addGate(self):
		# TODO implement logic
		# TODO save new gate
		pass


	# random fissue after random gate (no fissure should not have nodes after)
	def _addTemporalFissue(self):
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
