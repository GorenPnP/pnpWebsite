from rest_framework import serializers

from mining.models import *


class MaterialSerializer (serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['name', 'rigidity', 'tier', 'icon']