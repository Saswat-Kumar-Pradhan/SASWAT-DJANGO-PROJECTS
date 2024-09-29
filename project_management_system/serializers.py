from rest_framework import serializers
from .models import Profile, Project, Collaborator, GitRepo, HostLinks, ToDo

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class CollaboratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collaborator
        fields = '__all__'

class GitRepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitRepo
        fields = '__all__'

class HostLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostLinks
        fields = '__all__'

class ToDoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDo
        fields = '__all__'
