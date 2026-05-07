from django.db import models
from django.conf import settings
from blog.models.blog_post_mod import BlogPost


class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    like_count = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f'{self.user} on {self.post}'

    def increase_like_count(self):
        BlogComment.objects.filter(pk=self.pk).update(like_count=models.F('like_count') + 1)

    def decrease_like_count(self):
        BlogComment.objects.filter(pk=self.pk).update(like_count=models.F('like_count') - 1)

    def increase_comment_count(self):
        BlogPost.objects.filter(pk=self.post_id).update(comment_count=models.F('comment_count') + 1)

    def decrease_comment_count(self):
        BlogPost.objects.filter(pk=self.post_id).update(comment_count=models.F('comment_count') - 1)

    @classmethod
    def add_comment(cls, post, user, content, parent=None):
        comment = cls.objects.create(post=post, user=user, content=content, parent=parent)
        if parent is None:
            comment.increase_comment_count()
        return comment

    @classmethod
    def remove_comment(cls, comment_id, user):
        comment = cls.objects.filter(pk=comment_id, user=user).first()
        if not comment:
            return False
        is_root = comment.parent is None
        if is_root:
            comment.decrease_comment_count()
        comment.delete()
        return True


class BlogCommentLike(models.Model):
    comment = models.ForeignKey(BlogComment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_comment_likes')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')

    def __str__(self):
        return f'{self.user} liked comment {self.comment.id}'

    def increase_like_count(self):
        self.comment.increase_like_count()

    def decrease_like_count(self):
        self.comment.decrease_like_count()

    @classmethod
    def add_like(cls, comment, user):
        like, created = cls.objects.get_or_create(comment=comment, user=user)
        if created:
            like.increase_like_count()
        return created

    @classmethod
    def remove_like(cls, comment, user):
        like = cls.objects.filter(comment=comment, user=user).first()
        if like:
            like.decrease_like_count()
            like.delete()
            return True
        return False
