# Generated by Django 4.2.8 on 2025-03-28 14:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crafting', '0021_region_allowed_profiles_alter_drop_chance'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tool',
            options={'ordering': ['-speed', '-is_pick', '-is_axe', '-is_shovel'], 'verbose_name': 'Werkzeug', 'verbose_name_plural': 'Werkzeuge'},
        ),
    ]
