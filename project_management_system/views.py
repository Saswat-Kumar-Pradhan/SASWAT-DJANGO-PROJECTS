from rest_framework import viewsets
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views import View
from django.core.files.storage import default_storage
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from .models import Profile, Project, Collaborator, GitRepo, HostLinks, ToDo
from .serializers import ProfileSerializer, ProjectSerializer, CollaboratorSerializer, GitRepoSerializer, HostLinksSerializer, ToDoSerializer


@api_view(['POST'])
def loginView(request):
    email = request.data.get('email')
    password = request.data.get('password')

    # Validate input
    if not email or not password:
        return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        profile = Profile.objects.get(email=email)
    except Profile.DoesNotExist:
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    # Check if the password matches
    if not check_password(password, profile.password):
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    # Check if the profile is active
    if profile.status != 'Active':
        return Response({"detail": "Account is not active."}, status=status.HTTP_403_FORBIDDEN)

    # Generate custom JWT token
    payload = {
        'email': profile.email,
        'name': profile.name,
        'role': profile.role,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Set token expiration
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return Response({
        "access": token,
        "name": profile.name,
        "email": profile.email,
        "role": profile.role,
    }, status=status.HTTP_200_OK)


def decode_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


@api_view(['POST'])
def create_project(request):
    # Get the token from headers
    token = request.headers.get('Authorization')
    if not token:
        return Response({'error': 'Token is required'}, status=400)

    # Decode the token using your existing decode_jwt function
    payload = decode_jwt(token)
    if not payload:
        return Response({'error': 'Invalid or expired token'}, status=401)

    # Check user role
    role = payload.get('role')
    if role not in ['Admin', 'Manager']:
        return Response({'error': 'You are not authorized to create a project'}, status=403)

    # Get the authenticated user from the token
    email = payload.get('email')  # Assuming user_id is in the token
    try:
        profile = Profile.objects.get(email=email)
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=404)

    # Handle file upload for the logo
    logo = request.FILES.get('logo')
    if logo:
        file_name = default_storage.save(f'project_logos/{logo.name}', ContentFile(logo.read()))
    else:
        file_name = None

    # Prepare data for the serializer
    data = request.data.copy()
    if file_name:
        data['logo'] = file_name
    data['createBy'] = profile.id

    # Use the serializer to validate and save the project
    serializer = ProjectSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Project created successfully', 'project': serializer.data}, status=201)
    else:
        return Response({'error': serializer.errors}, status=400)


@api_view(['POST'])
def create_profile(request):
    # Get the token from headers
    token = request.headers.get('Authorization')
    if not token:
        return Response({'error': 'Token is required'}, status=400)

    # Decode the token using your existing decode_jwt function
    payload = decode_jwt(token)
    if not payload:
        return Response({'error': 'Invalid or expired token'}, status=401)

    # Check user role, only 'Admin' can create profiles
    role = payload.get('role')
    if role not in ['Admin', 'Manager']:
        return Response({'error': 'You are not authorized to create a profile'}, status=403)

    # Handle file upload for the profile image
    image = request.FILES.get('image')
    if image:
        file_name = default_storage.save(f'profile_images/{image.name}', ContentFile(image.read()))
    else:
        file_name = None

    # Prepare data for the serializer
    data = request.data.copy()
    if file_name:
        data['image'] = file_name

    # Use the serializer to validate and save the profile
    serializer = ProfileSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Profile created successfully', 'profile': serializer.data}, status=201)
    else:
        return Response({'error': serializer.errors}, status=400)
    

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class CollaboratorViewSet(viewsets.ModelViewSet):
    queryset = Collaborator.objects.all()
    serializer_class = CollaboratorSerializer

class GitRepoViewSet(viewsets.ModelViewSet):
    queryset = GitRepo.objects.all()
    serializer_class = GitRepoSerializer

class HostLinksViewSet(viewsets.ModelViewSet):
    queryset = HostLinks.objects.all()
    serializer_class = HostLinksSerializer

class ToDoViewSet(viewsets.ModelViewSet):
    queryset = ToDo.objects.all()
    serializer_class = ToDoSerializer
