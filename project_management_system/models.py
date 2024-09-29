from django.db import models
from datetime import datetime
from django.contrib.auth.hashers import make_password


class Profile(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Employee')
    designation = models.CharField(max_length=100, blank=True, null=True)
    STATUS_CHOICES = [
        ('Active', 'Active'),      # Status when the user is active
        ('Inactive', 'Inactive'),  # Status for inactive users
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    createDate = models.DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        # Hash password before saving
        if self.password and not self.password.startswith('pbkdf2'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Project(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='project_logos/', blank=True, null=True)  # Project logo image
    description = models.TextField()  # Detailed description of the project
    hostlink = models.URLField(max_length=500, blank=True, null=True)  # URL to the project's host
    documentation = models.URLField(max_length=500, blank=True, null=True)  # Optional URL for documentation
    flowchat = models.URLField(max_length=500, blank=True, null=True)  # Optional URL for flowchart
    uiDesign = models.URLField(max_length=500, blank=True, null=True)  # Optional URL for UI design
    gitUsername = models.CharField(max_length=255)  # Git username for the project repository
    gitPassword = models.CharField(max_length=255)  # Git password/token for the project repository (store securely)
    createBy = models.ForeignKey(Profile, on_delete=models.CASCADE)  # Foreign key reference to Profile model
    createDate = models.DateTimeField(default=datetime.now)  # Auto-populates the creation date
    STATUS_CHOICES = [
        ('Current', 'Current'),
        ('Completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Current')
    
    def __str__(self):
        return self.name



class Collaborator(models.Model):
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)
    profileID = models.ForeignKey(Profile, on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('Creator', 'Creator'),
        ('Modifier', 'Modifier'),
        ('Viewer', 'Viewer'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('projectID', 'profileID')  # Ensuring no duplicate collaborators

    def __str__(self):
        return f"{self.profileID.name} ({self.role}) in {self.projectID.name}"



class GitRepo(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    repoName = models.CharField(max_length=255)  # Name of the repository
    repoUrl = models.URLField(max_length=500)    # URL to the Git repository
    TYPE_CHOICES = [
        ('Frontend', 'Frontend'),
        ('Backend', 'Backend'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.repoName} ({self.type}) for {self.project.name}"



class HostLinks(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    hostName = models.CharField(max_length=255)  # Name of the host (e.g., "AWS", "Heroku")
    hostUrl = models.URLField(max_length=500)    # URL to the host environment
    TYPE_CHOICES = [
        ('Frontend', 'Frontend'),
        ('Backend', 'Backend'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.hostName} ({self.type}) for {self.project.name}"



class ToDo(models.Model):
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)
    assignedBy = models.ForeignKey(Profile, related_name='assigned_tasks', on_delete=models.CASCADE)  # Profile that assigned the task
    assignedTo = models.ForeignKey(Profile, related_name='received_tasks', on_delete=models.CASCADE)  # Profile the task is assigned to
    task = models.TextField()  # The actual task description
    progress = models.IntegerField(default=0)
    assignedOn = models.DateTimeField(default=datetime.now)  # Automatically sets the date the task was assigned
    
    def __str__(self):
        return f"Task: {self.task} | Assigned to: {self.assignedTo.name} | Status: {self.progress}"