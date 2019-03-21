# Generated by Django 2.1.2 on 2019-03-01 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DkGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('home', models.CharField(max_length=10)),
                ('away', models.CharField(max_length=10)),
                ('sport', models.CharField(max_length=10)),
                ('start_time', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='lineup_pos',
            field=models.IntegerField(default=0),
        ),
    ]
