from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# like a blog

class Post(models.Model):
    title = models.CharField(max_length=64)
    content = models.TextField()
    #date_posted = models.DateTimeField(auto_now=True)
    #date_posted = models.DateTimeField(auto_now_add=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
