import json
from django.core.management.base import BaseCommand
from blog.models.blog_post_mod import BlogPost
from blog.models.blog_media_mod import BlogMedia
from blog.models.blog_like_mod import BlogLike
from blog.models.blog_comment_mod import BlogComment, BlogCommentLike
from authentication.models import User
from profiles.models.doctor_prof_mod import Doctor
from medihub import settings


class Command(BaseCommand):
    help = 'Populate Blog posts with likes, comments and replies'

    def handle(self, *args, **kwargs):
        if BlogPost.objects.exists():
            self.stdout.write(self.style.SUCCESS('Blog posts already populated'))
            return

        filepath = settings.BASE_DIR / 'dataset' / 'blog_post.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            user = User.objects.filter(email=item['doctor_email']).first()
            if not user:
                self.stdout.write(self.style.WARNING(f'User {item["doctor_email"]} not found, skipping'))
                continue

            doctor = Doctor.objects.filter(user=user).first()
            if not doctor:
                self.stdout.write(self.style.WARNING(f'Doctor for {item["doctor_email"]} not found, skipping'))
                continue

            post = BlogPost.objects.create(
                doctor=doctor,
                title=item['title'],
                slug=item['slug'],
                content=item['content'],
                category=item['category'],
                tags=item.get('tags', ''),
                status=item['status'],
            )

            BlogMedia.objects.bulk_create([
                BlogMedia(
                    post=post,
                    media_type=media['media_type'],
                    file=media['file'],
                    caption=media.get('caption', ''),
                    order=media.get('order', 0),
                )
                for media in item.get('media', [])
            ])

            for like_email in item.get('likes', []):
                like_user = User.objects.filter(email=like_email).first()
                if like_user:
                    BlogLike.add_like(post=post, user=like_user)

            for comment_data in item.get('comments', []):
                comment_user = User.objects.filter(email=comment_data['user']).first()
                if not comment_user:
                    continue

                comment = BlogComment.add_comment(
                    post=post,
                    user=comment_user,
                    content=comment_data['content'],
                )

                for reply_data in comment_data.get('replies', []):
                    reply_user = User.objects.filter(email=reply_data['user']).first()
                    if reply_user:
                        BlogComment.add_comment(
                            post=post,
                            user=reply_user,
                            content=reply_data['content'],
                            parent=comment,
                        )

        self.stdout.write(self.style.SUCCESS('Blog posts populated successfully'))
