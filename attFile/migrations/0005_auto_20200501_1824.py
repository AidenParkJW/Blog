# Generated by Django 2.1.15 on 2020-05-01 18:24

import attFile.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attFile', '0004_auto_20200420_0010'),
    ]

    operations = [
        migrations.AddField(
            model_name='attfile',
            name='att_size',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=20, verbose_name='Attachment File Size'),
        ),
        migrations.AlterField(
            model_name='attfile',
            name='att_file',
            field=models.FileField(blank=True, max_length=512, unique=True, upload_to=attFile.models.get_file_path, verbose_name='Attachment File'),
        ),
    ]
