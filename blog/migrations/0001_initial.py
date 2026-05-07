from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('slug', models.SlugField(max_length=350, unique=True)),
                ('content', models.TextField()),
                ('category', models.CharField(choices=[('general', 'General'), ('cardiology', 'Cardiology'), ('neurology', 'Neurology'), ('pediatrics', 'Pediatrics'), ('gynecology', 'Gynecology'), ('dermatology', 'Dermatology'), ('orthopedics', 'Orthopedics'), ('nutrition', 'Nutrition'), ('mental_health', 'Mental Health'), ('diabetes', 'Diabetes'), ('first_aid', 'First Aid'), ('awareness', 'Awareness')], default='general', max_length=50)),
                ('tags', models.CharField(blank=True, max_length=500, null=True)),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='blog/thumbnails/')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], default='draft', max_length=10)),
                ('views', models.PositiveIntegerField(default=0)),
                ('like_count', models.PositiveIntegerField(default=0)),
                ('comment_count', models.PositiveIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blogs', to='profiles.doctor')),
            ],
            options={'ordering': ['-created']},
        ),
        migrations.CreateModel(
            name='BlogMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_type', models.CharField(choices=[('image', 'Image'), ('video', 'Video')], max_length=10)),
                ('file', models.FileField(upload_to='blog/media/')),
                ('caption', models.CharField(blank=True, max_length=300, null=True)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media', to='blog.blogpost')),
            ],
            options={'ordering': ['order']},
        ),
        migrations.CreateModel(
            name='BlogComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('like_count', models.PositiveIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='blog.blogpost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_comments', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='blog.blogcomment')),
            ],
            options={'ordering': ['created']},
        ),
        migrations.CreateModel(
            name='BlogLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='blog.blogpost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('post', 'user')}},
        ),
        migrations.CreateModel(
            name='BlogCommentLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='blog.blogcomment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_comment_likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('comment', 'user')}},
        ),
    ]
