# Generated by Django 4.1.7 on 2023-07-31 19:37

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0126_alter_wesenkraft_skilled_gfs'),
    ]

    operations = [
        migrations.AddField(
            model_name='charakter',
            name='image',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, null=True, quality=-1, scale=None, size=[1024, 1024], upload_to=''),
        ),
    ]
