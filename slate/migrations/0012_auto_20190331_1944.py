# Generated by Django 2.1.2 on 2019-04-01 00:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('slate', '0011_auto_20190324_2013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportlineup',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]