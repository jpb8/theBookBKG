# Generated by Django 2.1.2 on 2019-03-17 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0004_player_salary'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='order_pos',
            field=models.IntegerField(default=0),
        ),
    ]
