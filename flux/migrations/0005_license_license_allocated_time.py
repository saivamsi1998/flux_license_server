# Generated by Django 4.2.5 on 2023-09-11 20:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('flux', '0004_offerusermap'),
    ]

    operations = [
        migrations.AddField(
            model_name='license',
            name='license_allocated_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]