# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('provider_registration', '0002_registrationinfo_registration_complete'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationinfo',
            name='metadata_complete',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
