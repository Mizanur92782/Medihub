from django.db import models
from blog.models.blog_post_mod import BlogPost
from core.enum import BlogMediaTypeChoices


class BlogMedia(models.Model):

    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=BlogMediaTypeChoices.choices)
    file = models.FileField(upload_to='blog/media/')
    caption = models.CharField(max_length=300, blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.post.title} - {self.media_type}'
