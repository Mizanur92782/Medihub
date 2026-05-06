from django.db import models
from profiles.models.user_mod import User
from blog.models.blog_post_mod import BlogPost


class BlogLike(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_likes')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f'{self.user} liked {self.post}'

    def increase_like_count(self):
        BlogPost.objects.filter(pk=self.post_id).update(like_count=models.F('like_count') + 1)

    def decrease_like_count(self):
        BlogPost.objects.filter(pk=self.post_id).update(like_count=models.F('like_count') - 1)

    @classmethod
    def add_like(cls, post, user):
        like, created = cls.objects.get_or_create(post=post, user=user)
        if created:
            like.increase_like_count()
        return created

    @classmethod
    def remove_like(cls, post, user):
        like = cls.objects.filter(post=post, user=user).first()
        if like:
            like.decrease_like_count()
            like.delete()
            return True
        return False
