# Generated by Django 2.1.2 on 2019-04-12 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slate', '0012_auto_20190331_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineup',
            name='dedupe',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]