from django.db import models
from profiles.models.doctor_prof_mod import Doctor
from core.enum import BlogStatusChoices, BlogCategoryChoices


class BlogPost(models.Model):

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='blogs')
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=BlogCategoryChoices.choices, default=BlogCategoryChoices.GENERAL)
    tags = models.CharField(max_length=500, blank=True, null=True, help_text='Comma separated tags')
    thumbnail = models.ImageField(upload_to='blog/thumbnails/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=BlogStatusChoices.choices, default=BlogStatusChoices.DRAFT)
    views = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title
