from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from mining.models import *
from .serializers import *


class MaterialViews(viewsets.ViewSet):
	permission_classes = [permissions.IsAuthenticated]
	queryset = Material.objects.all()
	
	def list (self, request):
		serializer_class = MaterialSerializer(self.queryset, many=True)
		return Response(serializer_class.data)

	def retrieve(self, request, pk=None):
		print(pk, type(pk))
		material = get_object_or_404(self.queryset, pk=pk) if pk.isnumeric() else get_object_or_404(self.queryset, name=pk)
		serializer_class = MaterialSerializer(material)
		return Response(serializer_class.data)