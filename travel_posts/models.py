from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    # 这里绝对不能有 on_index
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    location = models.CharField(max_length=100)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    likes = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class PostMedia(models.Model):
    post = models.ForeignKey(Post, related_name='medias', on_delete=models.CASCADE)
    file = models.FileField(upload_to='travel_medias/')

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    text = models.TextField()