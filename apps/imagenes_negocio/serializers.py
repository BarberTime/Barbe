from rest_framework import serializers
from .models import ImagenesNegocio 

class ImagenesNegocioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenesNegocio
        fields = ['id_imagen', 'negocio', 'imagen']
        read_only_fields = ['id_imagen']

class ImagenesNegocioDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenesNegocio
        fields = ['id_imagen', 'negocio', 'imagen']
        read_only_fields = ['id_imagen']