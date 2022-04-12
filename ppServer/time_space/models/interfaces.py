from abc import abstractmethod
import json
from random import choice
from typing import List, Tuple

from django.core.validators import MinValueValidator
from django.db import models

from time_space.enums import NodeType, Signal


# interface, implemented by gate & temporal fissure
class Node(models.Model):

	class Meta:
		abstract = True

	# init with empty _before- & _next relations
	before = models.TextField(default="[]")	# all ids of nodes
	next = models.TextField(default="[]")  # all ids of nodes


	def getNext(self):
		return json.loads(self.next)

	def _getBefore(self):
		return json.loads(self.before)

	def _setNext(self, next):
		# TODO check validity of nodes (e.g.: id is not None)
		self.next = json.dumps([Node.toSpecs(n) for n in next])
		self.save()

	def _setBefore(self, before):
		# TODO check validity of nodes (e.g.: id is not None)
		self.before = json.dumps([Node.toSpecs(n) for n in before])
		self.save()

	def postprocessSignal(self, outputs: List[str]) -> List[str]:
		return outputs


	# returns null if the signal didn't pass through
	@abstractmethod
	def processSignal(self, signals) -> Tuple[Signal, str]:
		raise NotImplementedError()


	def __str__(self):
		return "({} id:{})".format(type(self).__name__, self.id)


	# destroy this node after rewiring _before & after nodes to each other
	def destroy(self):
		for beforeSpec in self._getBefore():
			for nextSpec in self.getNext():
				beforeNode = Node.toNode(*beforeSpec)
				beforeNode.addToNext(*nextSpec)

		self.delete()


	# needed if neighbors are destroyed
	# IMPORTANT: automatic management of _before every time _next is changed!
	def addNodeToNext(self, node):

		spec = Node.toSpecs(node)
		return self.addToNext(spec[0], spec[1])


	def addToNext(self, nodeType, nodeId):

		if [nodeType, nodeId] in self.getNext():
			return

		node = Node.toNode(nodeType, nodeId)
		self._setNext([Node.toNode(*n) for n in self.getNext()] + [node])
		node._addNodeToBefore(self)


	def removeNodeFromNext(self, node):

		nodeType, nodeId = Node.toSpecs(node)
		return self.removeFromNext(nodeType, nodeId)


	def removeFromNext(self, nodeType, nodeId):

		# remove node's deleteSpec (all duplicates if existing)
		nextList = [spec for spec in self.getNext()
			if spec[0] != nodeType or spec[1] != nodeId]

		self._setNext([Node.toNode(*n) for n in nextList])

		# apply in reverse, too
		try:
			node = Node.toNode(nodeType, nodeId)
		except: return
		node._removeNodeFromBefore(self)


	# 	private starting here 	#

	def _addNodeToBefore(self, node):

		spec = Node.toSpecs(node)
		return self._addToBefore(spec[0], spec[1])


	def _addToBefore(self, nodeType, nodeId):

		if [nodeType, nodeId] in self._getBefore():
			return

		node = Node.toNode(nodeType, nodeId)
		self._setBefore([Node.toNode(*n) for n in self._getBefore()] + [node])


	def _removeNodeFromBefore(self, node):

		nodeType, nodeId = Node.toSpecs(node)
		return self._removeFromBefore(nodeType, nodeId)

	def _removeFromBefore(self, nodeType, nodeId):

		# remove node's deleteSpec (all duplicates if existing)
		specList = [spec for spec in self._getBefore()
							if spec[0] != nodeType or spec[1] != nodeId]

		beforeList = []
		for spec in specList:
			try:
				node = Node.toNode(*spec)
			except: continue
			beforeList.append(node)

		self._setBefore(beforeList)


	@classmethod
	def toNode(cls, nodeType, nodeId):
		node = NodeType(nodeType).toModel().objects.get(id=nodeId)
		return node

	@classmethod
	def toSpecs(cls, node):
		return [NodeType.fromModel(type(node)), node.id]

class Gate(Node):

	class Meta:
		abstract = True


class TemporalFissure(Node):

	class Meta:
		abstract = True

	net_id = models.PositiveSmallIntegerField(default=1)
	stufe = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
	next_required_input_at = models.PositiveSmallIntegerField(default=0)


	_output = {}
	_required_input = []

	def _get_output(self, signals = []):

		if self.next_required_input_at >= len(self._required_input):
			return "dead"

		# update required input index based on incoming signals
		if self._required_input[self.next_required_input_at] not in signals:
			self.next_required_input_at = 0
		else:
			self.next_required_input_at += 1
		
		self.save()

		# killed
		if self.next_required_input_at >= len(self._required_input):
			# self.destroy()
			return choice(self._output["killed"]) if "killed" in self._output else choice(self._output["always"])
			# return "killed"

		# hit
		if self.next_required_input_at != 0:
			return choice(self._output["hit"]) if "hit" in self._output else choice(self._output["always"])
			# return "hit"

		# missed
		return choice(self._output["always"])
		# return "missed"


	def processSignal(self, signals) -> Tuple[Signal, str]:
		output = self._get_output(signals)
		return None, "#{}: {}".format(self.net_id, output)


	def addNodeToNext(self, node):
		raise NotImplementedError("Temporal Fissure can not have following nodes")

	def removeNodeFromNext(self, node):
		raise NotImplementedError("Temporal Fissure can not have following nodes")
