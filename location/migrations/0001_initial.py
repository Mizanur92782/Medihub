# Generated migration - updated to match current models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('division_id', models.IntegerField(unique=True)),
                ('division_name_bn', models.CharField(max_length=100)),
                ('division_name_eng', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('district_id', models.IntegerField(unique=True)),
                ('district_name_bn', models.CharField(max_length=100)),
                ('district_name_eng', models.CharField(max_length=100)),
                ('lattitude', models.DecimalField(decimal_places=10, max_digits=12)),
                ('logitude', models.DecimalField(decimal_places=10, max_digits=12)),
                ('division', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.division')),
            ],
        ),
        migrations.CreateModel(
            name='Upozila',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upozila', models.IntegerField(unique=True)),
                ('upoila_name_bn', models.CharField(max_length=100)),
                ('upozila_name_eng', models.CharField(max_length=100)),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.district')),
            ],
        ),
        migrations.CreateModel(
            name='Union',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('union', models.IntegerField(unique=True)),
                ('union_name_bn', models.CharField(max_length=100)),
                ('union_name_eng', models.CharField(max_length=100)),
                ('upozila', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.upozila')),
            ],
        ),
    ]
