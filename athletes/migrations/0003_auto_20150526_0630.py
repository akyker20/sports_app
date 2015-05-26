# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('athletes', '0002_auto_20150526_0628'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feedcontent',
            old_name='athletes',
            new_name='athletes_to_receive',
        ),
    ]
