from django.db.models import *
from django.db import transaction
from app_escolar_backend.serializers import UserSerializer
from app_escolar_backend.serializers import *
from app_escolar_backend.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group
import json

class AlumnosAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        user = request.user
        #TODO: Regresar perfil del usuario
        return Response({})

class AlumnosView(generics.CreateAPIView):
    # Permisos por método (sobrescribe el comportamiento default)
    # Verifica que el usuario esté autenticado para las peticiones GET, PUT y DELETE
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación

    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        # Validamos los datos de autenticación del usuario
        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid():
            #Grabar datos del usuario --- esto va en la tabla authUser
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']

            #Valida si existe el usuario o bien el email registrado
            if User.objects.filter(email=email).exists():
                return Response({"message": "Usuario " + email + ", ya está registrado"}, 400)

            #Crea el usuario (create_user ya cifra la contraseña)
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )

            #Se guarda en la BD el tipo de rol -> Alumno
            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)

            #Almacenar los datos adicionales del alumno
            alumno = Alumnos.objects.create(
                user=user,
                matricula=request.data.get("matricula"),
                fecha_nacimiento=request.data.get("fecha_nacimiento") or None,
                curp=request.data.get("curp"),
                rfc=(request.data.get("rfc") or "").upper(),
                edad=request.data.get("edad") or None,
                telefono=request.data.get("telefono"),
                ocupacion=request.data.get("ocupacion")
            )
            alumno.save()

            return Response({"Alumno creado correctamente": alumno.id}, 201)

        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)