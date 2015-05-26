# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('athletes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AthleteContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('athlete', models.ForeignKey(to='athletes.AthleteProfile')),
                ('feed_content', models.ForeignKey(to='athletes.FeedContent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='feedcontent',
            name='athletes',
            field=models.ManyToManyField(related_name='feed_content', null=True, through='athletes.AthleteContent', to='athletes.AthleteProfile', blank=True),
            preserve_default=True,
        ),
    ]
