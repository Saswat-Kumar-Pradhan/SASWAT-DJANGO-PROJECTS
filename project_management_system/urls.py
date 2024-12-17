from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import loginView, create_project, create_profile, ProfileViewSet, ProjectViewSet, CollaboratorViewSet, GitRepoViewSet, HostLinksViewSet, ToDoViewSet

# Initialize the DefaultRouter
router = DefaultRouter()

# Register your ViewSets with the router
router.register(r'profiles', ProfileViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'collaborators', CollaboratorViewSet)
router.register(r'gitrepos', GitRepoViewSet)
router.register(r'hostlinks', HostLinksViewSet)
router.register(r'todos', ToDoViewSet)

# Include router urls
urlpatterns = [
    path('login/', loginView, name='login'),
    path('create_project/', create_project, name='create_project'),
    path('create_profile/', create_profile, name='create_profile'),
    path('', include(router.urls)),
]
