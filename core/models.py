import os
from django.db import models
import uuid

# Create your models here.
class datafile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    upload = models.FileField(upload_to='datasets/', unique=True)
    choices = [
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]
    status = models.CharField(max_length=50, choices=choices, default='Processing')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def filename(self):
        return os.path.basename(self.upload.name)
    
    def __str__(self):
        return self.name + self.filename
    
    class Meta:
        ordering = ['-created_at']
    
class agent_response(models.Model):
    file = models.OneToOneField(datafile, on_delete=models.CASCADE, editable=False)
    response_text = models.TextField(editable=False)
    actions_to_take = models.TextField(editable=False)
    choices = [
        ('Wear', 'Wear'),
        ('RootCrack', 'RootCrack'),
        ('MissingTooth', 'MissingTooth'),
        ('Healthy', 'Healthy'),
        ('Broken', 'Broken'),
    ]
    gear_Status = models.CharField(max_length=256, editable=False, choices=choices, default='NIL')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response for {self.file.name}"