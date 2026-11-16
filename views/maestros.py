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

class MaestrosAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        user = request.user
        #TODO: Regresar perfil del usuario
        return Response({})

class MaestrosView(generics.CreateAPIView):
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

            #Se guarda en la BD el tipo de rol -> Maestro
            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)

            #Almacenar los datos adicionales del maestro
            maestro = Maestros.objects.create(
                user=user,
                id_trabajador=request.data.get("id_trabajador"),
                fecha_nacimiento=request.data.get("fecha_nacimiento") or None,
                telefono=request.data.get("telefono"),
                rfc=(request.data.get("rfc") or "").upper(),
                cubiculo=request.data.get("cubiculo"),
                edad=request.data.get("edad") or None,
                area_investigacion=request.data.get("area_investigacion"),
                materias_array=json.dumps(request.data.get("materias_array", []), ensure_ascii=False),
            )
            maestro.save()

            return Response({"Maestro creado correctamente": maestro.id}, 201)

        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)