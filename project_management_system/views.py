from rest_framework import viewsets
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view
from rest_framework.response import Response
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
