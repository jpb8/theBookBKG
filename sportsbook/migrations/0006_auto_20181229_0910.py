# Generated by Django 2.1.2 on 2018-12-29 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sportsbook', '0005_gameodds'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameodds',
            name='time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
