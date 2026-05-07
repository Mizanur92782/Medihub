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
            name='Specialization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_eng', models.CharField(max_length=200, unique=True)),
                ('name_bn', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubSpecialization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_eng', models.CharField(max_length=200, unique=True)),
                ('name_bn', models.CharField(max_length=200, unique=True)),
                ('specialization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_specializations', to='profiles.specialization')),
            ],
        ),
        migrations.CreateModel(
            name='Qualification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_eng', models.CharField(max_length=200, unique=True)),
                ('name_bn', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_eng', models.CharField(max_length=200, unique=True)),
                ('name_bn', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10)),
                ('profile_dp', models.ImageField(blank=True, null=True, upload_to='doctor/dp/')),
                ('contact_number', models.CharField(max_length=15)),
                ('years_of_experience', models.PositiveIntegerField(default=0)),
                ('license_number', models.CharField(max_length=100, unique=True)),
                ('license_validity', models.DateField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='doctor', to=settings.AUTH_USER_MODEL)),
                ('division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.division')),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.district')),
                ('upozila', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.upozila')),
                ('union', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.union')),
                ('specialization', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.specialization')),
                ('sub_specialization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.subspecialization')),
                ('qualifications', models.ManyToManyField(blank=True, related_name='doctors', to='profiles.qualification')),
                ('hospital_affiliations', models.ManyToManyField(blank=True, related_name='doctors', to='profiles.hospital')),
            ],
        ),
        migrations.CreateModel(
            name='DoctorDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('website', models.URLField(blank=True, null=True)),
                ('social_link', models.URLField(blank=True, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('language', models.CharField(blank=True, max_length=200, null=True)),
                ('doctor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='profiles.doctor')),
            ],
        ),
        migrations.CreateModel(
            name='DoctorEducation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution', models.CharField(max_length=200)),
                ('degree', models.CharField(max_length=200)),
                ('start_at', models.DateField()),
                ('end_at', models.DateField(blank=True, null=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educations', to='profiles.doctor')),
            ],
        ),
        migrations.CreateModel(
            name='DoctorWorkingExperience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution', models.CharField(max_length=200)),
                ('position', models.CharField(max_length=200)),
                ('starting_at', models.DateField()),
                ('end_at', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiences', to='profiles.doctor')),
            ],
        ),
        migrations.CreateModel(
            name='DoctorScheduling',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('saturday', 'Saturday'), ('sunday', 'Sunday'), ('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday')], max_length=10)),
                ('start', models.TimeField()),
                ('end', models.TimeField()),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='profiles.doctor')),
            ],
        ),
        migrations.CreateModel(
            name='DoctorRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='profiles.doctor')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='given_ratings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('doctor', 'user')},
            },
        ),
        migrations.CreateModel(
            name='RegularUserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10)),
                ('profile_dp', models.ImageField(blank=True, null=True, upload_to='user/dp/')),
                ('contact_number', models.CharField(blank=True, max_length=15, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
                ('division', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.division')),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.district')),
                ('upozila', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.upozila')),
            ],
        ),
        migrations.CreateModel(
            name='AmbulanceProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_name', models.CharField(max_length=200)),
                ('contact_number', models.CharField(max_length=15)),
                ('ambulance_type', models.CharField(choices=[('basic', 'Basic'), ('advanced', 'Advanced'), ('icu', 'ICU')], max_length=20)),
                ('vehicle_number', models.CharField(max_length=50, unique=True)),
                ('is_available', models.BooleanField(default=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ambulance', to=settings.AUTH_USER_MODEL)),
                ('division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.division')),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.district')),
                ('upozila', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.upozila')),
            ],
        ),
        migrations.CreateModel(
            name='PharmacyProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pharmacy_name', models.CharField(max_length=200)),
                ('owner_name', models.CharField(max_length=200)),
                ('contact_number', models.CharField(max_length=15)),
                ('license_number', models.CharField(max_length=100, unique=True)),
                ('license_validity', models.DateField()),
                ('is_open', models.BooleanField(default=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pharmacy', to=settings.AUTH_USER_MODEL)),
                ('division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.division')),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.district')),
                ('upozila', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.upozila')),
            ],
        ),
        migrations.CreateModel(
            name='DiagnosticProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diagnostic_name', models.CharField(max_length=200)),
                ('owner_name', models.CharField(max_length=200)),
                ('contact_number', models.CharField(max_length=15)),
                ('license_number', models.CharField(max_length=100, unique=True)),
                ('license_validity', models.DateField()),
                ('is_open', models.BooleanField(default=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='diagnostic', to=settings.AUTH_USER_MODEL)),
                ('division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.division')),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.district')),
                ('upozila', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.upozila')),
            ],
        ),
        migrations.CreateModel(
            name='BloodDonor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10)),
                ('contact_number', models.CharField(max_length=15)),
                ('blood_group', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], max_length=5)),
                ('availability', models.CharField(choices=[('available', 'Available'), ('unavailable', 'Unavailable')], default='available', max_length=15)),
                ('last_donated', models.DateField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='blood_donor', to=settings.AUTH_USER_MODEL)),
                ('division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.division')),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.district')),
                ('upozila', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.upozila')),
            ],
        ),
    ]
