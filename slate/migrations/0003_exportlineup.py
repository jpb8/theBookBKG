# Generated by Django 2.1.2 on 2019-03-14 03:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('slate', '0002_auto_20190313_2030'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportLineup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('p1', models.CharField(max_length=124, null=True)),
                ('p2', models.CharField(max_length=124, null=True)),
                ('c', models.CharField(max_length=124, null=True)),
                ('fB', models.CharField(max_length=124, null=True)),
                ('sB', models.CharField(max_length=124, null=True)),
                ('tB', models.CharField(max_length=124, null=True)),
                ('ss', models.CharField(max_length=124, null=True)),
                ('of1', models.CharField(max_length=124, null=True)),
                ('of2', models.CharField(max_length=124, null=True)),
                ('of3', models.CharField(max_length=124, null=True)),
                ('salary', models.IntegerField(default=0)),
                ('team1', models.CharField(max_length=10, null=True)),
                ('team2', models.CharField(max_length=10, null=True)),
                ('lu_type', models.CharField(max_length=10, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
