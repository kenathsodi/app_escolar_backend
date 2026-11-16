from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *

#Este serializer trae los datos de autenticación de cualquier usuario
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")

#Definimos el serializer para administradores
class AdminSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Administradores
        fields = '__all__'

#Definimos el serializer para maestros
class MaestroSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Maestros
        fields = '__all__'
        
#TODO: Agregar serializer para alumnos
# class AlumnosSerializer(serializers.ModelSerializer):
#     user=UserSerializer(read_only=True)
#     class Meta:
#         model = Alumnos
#         fields = '__all__'

