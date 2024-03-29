# Generated by Django 4.2.8 on 2024-02-12 20:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

def add_settings(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    PushSettings = apps.get_model('webPush', 'PushSettings')

    for user in User.objects.all():
        PushSettings.objects.get_or_create(user=user)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PushSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat', models.BooleanField(default=True)),
                ('news', models.BooleanField(default=True)),
                ('quiz', models.BooleanField(default=True)),
                ('changelog', models.BooleanField(default=True)),
                ('polls', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user'],
            },
        ),
        migrations.RunPython(add_settings)
    ]
