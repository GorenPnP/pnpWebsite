# Generated by Django 4.1.7 on 2023-12-19 11:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dex', '0020_monsterteam_textfarbe'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterteam',
            name='gefangen_am',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]