# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoachProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_of_birth', models.DateField()),
                ('coach', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
                ('current_team', models.OneToOneField(related_name='coach', to='teams.Team')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
