# Generated by Django 2.2.4 on 2019-08-29 00:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('teams', '0008_team_start_time'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('players', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lineup',
            fields=[
                ('lu_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
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
                ('all_teams', models.CharField(max_length=124, null=True)),
                ('pts', models.DecimalField(decimal_places=2, default=0.0, max_digits=100)),
                ('lu_type', models.CharField(max_length=10, null=True)),
                ('combo', models.CharField(max_length=10, null=True)),
                ('dedupe', models.CharField(max_length=124, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.Team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StackPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_spot', models.IntegerField(default=0)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='players.Player')),
                ('stack', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='slate.Stack')),
            ],
        ),
        migrations.CreateModel(
            name='Punt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dkid', models.IntegerField()),
                ('name_id', models.CharField(max_length=124)),
                ('position', models.CharField(max_length=10)),
                ('salary', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
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
                ('combo', models.CharField(max_length=10, null=True)),
                ('dedupe', models.CharField(max_length=122, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
