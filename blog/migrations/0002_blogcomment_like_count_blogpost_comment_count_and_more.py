from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='like_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='comment_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='blogcomment',
            name='like_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
