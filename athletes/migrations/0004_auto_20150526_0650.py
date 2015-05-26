# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('athletes', '0003_auto_20150526_0630'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sharedclip',
            old_name='athlete',
            new_name='sharing_athlete',
        ),
    ]
