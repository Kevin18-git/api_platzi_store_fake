from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer
)
from .forms import UserRegistrationForm, UserLoginForm

@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    """
    Vista API para el registro de nuevos usuarios.
    
    Endpoint: POST /api/register/
    
    Parámetros esperados:
    - username: nombre de usuario único
    - email: correo electrónico válido
    - password: contraseña (mínimo 8 caracteres)
    - password2: confirmación de contraseña
    - first_name: nombre (opcional)
    - last_name: apellido (opcional)
    
    Respuestas:
    - 201: Usuario creado exitosamente
    - 400: Error en validación de datos
    """
    if request.method == 'POST':
        # Creamos el serializer con los datos recibidos
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Guardamos el nuevo usuario
            user = serializer.save()
            
            # Creamos o obtenemos el token de autenticación para el usuario
            token, created = Token.objects.get_or_create(user=user)
            
            # Preparamos la respuesta con los datos del usuario y su token
            response_data = {
                'success': True,
                'message': 'Usuario registrado satisfactoriamente',
                'user': UserSerializer(user).data,
                'token': token.key
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        # Si hay errores de validación, los devolvemos
        return Response({
            'success': False,
            'message': 'Error en el registro',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """
    Vista API para el inicio de sesión de usuarios.
    
    Endpoint: POST /api/login/
    
    Parámetros esperados:
    - username: nombre de usuario
    - password: contraseña
    
    Respuestas:
    - 200: Autenticación exitosa
    - 400: Error en credenciales
    """
    if request.method == 'POST':
        # Creamos el serializer con los datos de login
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Obtenemos el usuario validado
            user = serializer.validated_data['user']
            
            # Iniciamos sesión en Django (opcional, para mantener sesión)
            login(request, user)
            
            # Creamos o obtenemos el token de autenticación
            token, created = Token.objects.get_or_create(user=user)
            
            # Preparamos la respuesta exitosa
            response_data = {
                'success': True,
                'message': 'Autenticación satisfactoria',
                'user': UserSerializer(user).data,
                'token': token.key
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        # Si hay errores de autenticación
        return Response({
            'success': False,
            'message': 'Error en la autenticación',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """
    Vista API para cerrar sesión.
    
    Endpoint: POST /api/logout/
    Requiere: Token de autenticación en headers
    
    Respuestas:
    - 200: Sesión cerrada exitosamente
    - 401: No autorizado (sin token válido)
    """
    if request.method == 'POST':
        try:
            # Eliminamos el token del usuario
            request.user.auth_token.delete()
            
            # Cerramos la sesión de Django
            logout(request)
            
            return Response({
                'success': True,
                'message': 'Sesión cerrada exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error al cerrar sesión',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_api(request):
    """
    Vista API para obtener el perfil del usuario actual.
    
    Endpoint: GET /api/profile/
    Requiere: Token de autenticación en headers
    
    Respuestas:
    - 200: Datos del usuario
    - 401: No autorizado (sin token válido)
    """
    if request.method == 'GET':
        # Devolvemos los datos del usuario autenticado
        serializer = UserSerializer(request.user)
        
        return Response({
            'success': True,
            'user': serializer.data
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_username_api(request):
    """
    Vista API para verificar disponibilidad de nombre de usuario.
    
    Endpoint: GET /api/check-username/?username=nombreusuario
    
    Parámetros de query:
    - username: nombre de usuario a verificar
    
    Respuestas:
    - 200: Información sobre disponibilidad
    """
    username = request.GET.get('username', '')
    
    if not username:
        return Response({
            'success': False,
            'message': 'Debe proporcionar un nombre de usuario'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verificamos si el username existe
    exists = User.objects.filter(username=username).exists()
    
    return Response({
        'success': True,
        'available': not exists,
        'message': 'Nombre de usuario no disponible' if exists else 'Nombre de usuario disponible'
    }, status=status.HTTP_200_OK)

# --- Vistas de Autenticación Basadas en Formularios ---

def register_view(request):
    """
    Vista para el registro de usuarios a través de un formulario web.
    """
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Creamos el usuario usando el método seguro que hashea la contraseña
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', '')
            )
            login(request, user)
            messages.success(request, 'Tu cuenta ha sido creada correctamente. ¡Bienvenido!', extra_tags='register-success')
            return redirect('products:home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """
    Vista para el inicio de sesión de usuarios a través de un formulario web.
    """
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Hola de nuevo, {user.username}!')
                
                # Redirigir a la página siguiente si existe, o a home
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('products:home')
            else:
                # Este error se mostrará como un non_field_error en el formulario
                form.add_error(None, 'Usuario o contraseña incorrectos.')
    else:
        form = UserLoginForm()
        
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """
    Vista para cerrar la sesión del usuario.
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Has cerrado sesión exitosamente.')
        return redirect('products:home')
    
    # Si se accede por GET, redirigir a home
    return redirect('products:home')