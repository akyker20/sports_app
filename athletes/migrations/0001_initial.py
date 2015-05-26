# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('coaches', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teams', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AthleteProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_of_birth', models.DateField()),
                ('number', models.IntegerField(default=0)),
                ('height', models.IntegerField()),
                ('weight', models.IntegerField()),
                ('vertical_leap', models.IntegerField()),
                ('avg_rebounds', models.DecimalField(default=0.0, max_digits=4, decimal_places=1)),
                ('avg_steals', models.DecimalField(default=0.0, max_digits=4, decimal_places=1)),
                ('avg_blocks', models.DecimalField(default=0.0, max_digits=4, decimal_places=1)),
                ('avg_points', models.DecimalField(default=0.0, max_digits=4, decimal_places=1)),
                ('avg_assists', models.DecimalField(default=0.0, max_digits=4, decimal_places=1)),
                ('athlete', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
                ('current_team', models.ForeignKey(related_name='athletes', to='teams.Team')),
                ('watching', models.ManyToManyField(related_name='watched_by', null=True, to='athletes.AthleteProfile', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Clip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('view_count', models.IntegerField(default=0)),
                ('row', models.IntegerField(default=1)),
                ('col', models.IntegerField(default=1)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClipComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(max_length=256)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(to='athletes.AthleteProfile')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClipStar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('author', models.ForeignKey(to='athletes.AthleteProfile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeedContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('feedcontent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='athletes.FeedContent')),
                ('home_team_score', models.IntegerField(default=0)),
                ('away_team_score', models.IntegerField(default=0)),
                ('away_team', models.ForeignKey(related_name='away_games', to='teams.Team')),
                ('home_team', models.ForeignKey(related_name='home_games', to='teams.Team')),
            ],
            options={
                'ordering': ['created_at'],
            },
            bases=('athletes.feedcontent',),
        ),
        migrations.CreateModel(
            name='GameComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(max_length=256)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(to='athletes.AthleteProfile')),
                ('game', models.ForeignKey(related_name='comments', to='athletes.Game')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GameFilm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('duration', models.IntegerField(default=0)),
                ('file_size', models.IntegerField(default=0)),
                ('mpd_url', models.CharField(max_length=128)),
                ('coach_uploaded_by', models.ForeignKey(to='coaches.CoachProfile')),
                ('game', models.OneToOneField(related_name='gamefilm', to='athletes.Game')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GameFilmClip',
            fields=[
                ('clip_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='athletes.Clip')),
                ('gamefilm_start_time', models.DecimalField(default=0.0, max_digits=6, decimal_places=1)),
                ('gamefilm_end_time', models.DecimalField(default=0.0, max_digits=6, decimal_places=1)),
                ('game', models.ForeignKey(related_name='clips', to='athletes.Game')),
            ],
            options={
                'abstract': False,
            },
            bases=('athletes.clip',),
        ),
        migrations.CreateModel(
            name='GameStat',
            fields=[
                ('feedcontent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='athletes.FeedContent')),
                ('points', models.IntegerField(default=0)),
                ('rebounds', models.IntegerField(default=0)),
                ('assists', models.IntegerField(default=0)),
                ('blocks', models.IntegerField(default=0)),
                ('steals', models.IntegerField(default=0)),
                ('athlete', models.ForeignKey(to='athletes.AthleteProfile')),
                ('game', models.ForeignKey(to='athletes.Game')),
            ],
            options={
                'ordering': ['game'],
            },
            bases=('athletes.feedcontent',),
        ),
        migrations.CreateModel(
            name='GameStatStar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('author', models.ForeignKey(to='athletes.AthleteProfile')),
                ('gamestat', models.ForeignKey(related_name='stars', to='athletes.GameStat')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GameFilmPostedNotification',
            fields=[
                ('notification_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='athletes.Notification')),
                ('game_film', models.ForeignKey(to='athletes.GameFilm')),
            ],
            options={
                'abstract': False,
            },
            bases=('athletes.notification',),
        ),
        migrations.CreateModel(
            name='SharedClip',
            fields=[
                ('feedcontent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='athletes.FeedContent')),
                ('athlete', models.ForeignKey(related_name='shared_clips', to='athletes.AthleteProfile')),
            ],
            options={
                'abstract': False,
            },
            bases=('athletes.feedcontent',),
        ),
        migrations.CreateModel(
            name='UploadedClip',
            fields=[
                ('clip_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='athletes.Clip')),
                ('url', models.CharField(max_length=128)),
                ('file_size', models.IntegerField(default=0)),
                ('duration', models.DecimalField(default=0.0, max_digits=5, decimal_places=1)),
            ],
            options={
                'abstract': False,
            },
            bases=('athletes.clip',),
        ),
        migrations.AddField(
            model_name='sharedclip',
            name='clip',
            field=models.ForeignKey(related_name='shares', to='athletes.Clip'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='athlete',
            field=models.ForeignKey(related_name='notifications', to='athletes.AthleteProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_athletes.notification_set', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='gamestatstar',
            unique_together=set([('gamestat', 'author')]),
        ),
        migrations.AlterUniqueTogether(
            name='gamestat',
            unique_together=set([('athlete', 'game')]),
        ),
        migrations.AddField(
            model_name='gamefilmclip',
            name='gamestat',
            field=models.ForeignKey(related_name='clips', to='athletes.GameStat'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='feedcontent',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_athletes.feedcontent_set', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clipstar',
            name='clip',
            field=models.ForeignKey(related_name='stars', to='athletes.Clip'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='clipstar',
            unique_together=set([('clip', 'author')]),
        ),
        migrations.AddField(
            model_name='clipcomment',
            name='clip',
            field=models.ForeignKey(related_name='comments', to='athletes.Clip'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clip',
            name='athlete',
            field=models.ForeignKey(to='athletes.AthleteProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clip',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_athletes.clip_set', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
    ]
