from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BloodNeedPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_name', models.CharField(max_length=200)),
                ('patient_age', models.PositiveSmallIntegerField()),
                ('patient_gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10)),
                ('blood_group', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], max_length=5)),
                ('bags_needed', models.PositiveSmallIntegerField(default=1)),
                ('hospital_name', models.CharField(max_length=300)),
                ('hospital_address', models.TextField(blank=True, null=True)),
                ('needed_date', models.DateField()),
                ('needed_time', models.TimeField()),
                ('contact_number', models.CharField(max_length=15)),
                ('urgency', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='high', max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('open', 'Open'), ('fulfilled', 'Fulfilled'), ('closed', 'Closed')], default='open', max_length=15)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blood_need_posts', to=settings.AUTH_USER_MODEL)),
                ('division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.division')),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.district')),
                ('upozila', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.upozila')),
            ],
            options={'ordering': ['-created']},
        ),
        migrations.CreateModel(
            name='MedicineNeedPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicine_name', models.CharField(max_length=300)),
                ('quantity', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('contact_number', models.CharField(max_length=15)),
                ('urgency', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', max_length=10)),
                ('status', models.CharField(choices=[('open', 'Open'), ('fulfilled', 'Fulfilled'), ('closed', 'Closed')], default='open', max_length=15)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medicine_need_posts', to=settings.AUTH_USER_MODEL)),
                ('division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.division')),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.district')),
                ('upozila', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.upozila')),
            ],
            options={'ordering': ['-created']},
        ),
        migrations.CreateModel(
            name='EquipmentNeedPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('equipment_name', models.CharField(max_length=300)),
                ('quantity', models.CharField(max_length=100)),
                ('condition', models.CharField(choices=[('new', 'New'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')], default='good', max_length=10)),
                ('image', models.ImageField(blank=True, null=True, upload_to='post/equipment/')),
                ('description', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('contact_number', models.CharField(max_length=15)),
                ('urgency', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', max_length=10)),
                ('status', models.CharField(choices=[('open', 'Open'), ('fulfilled', 'Fulfilled'), ('closed', 'Closed')], default='open', max_length=15)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipment_need_posts', to=settings.AUTH_USER_MODEL)),
                ('division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.division')),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.district')),
                ('upozila', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.upozila')),
            ],
            options={'ordering': ['-created']},
        ),
        migrations.CreateModel(
            name='GeneralPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('content', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='post/general/')),
                ('contact_number', models.CharField(blank=True, max_length=15, null=True)),
                ('status', models.CharField(choices=[('open', 'Open'), ('fulfilled', 'Fulfilled'), ('closed', 'Closed')], default='open', max_length=15)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='general_posts', to=settings.AUTH_USER_MODEL)),
                ('division', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.division')),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.district')),
                ('upozila', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.upozila')),
            ],
            options={'ordering': ['-created']},
        ),
    ]
