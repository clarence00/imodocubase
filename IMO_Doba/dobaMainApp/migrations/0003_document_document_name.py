# Generated by Django 5.0.3 on 2024-03-30 12:58

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dobaMainApp', '0002_remove_document_document_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='document_name',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]