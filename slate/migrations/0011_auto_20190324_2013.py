# Generated by Django 2.1.2 on 2019-03-25 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slate', '0010_lineup_pts'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportlineup',
            name='combo',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='lineup',
            name='combo',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
