# Generated by Django 2.1.2 on 2019-03-18 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('dk_name', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('fg_name', models.CharField(max_length=10)),
                ('rw_name', models.CharField(max_length=10)),
                ('league', models.CharField(max_length=10)),
            ],
        ),
    ]
