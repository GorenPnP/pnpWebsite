# Generated by Django 4.2.8 on 2025-04-06 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crafting', '0033_alter_miningperk_options_alter_tool_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='block',
            old_name='effektive_tool',
            new_name='effective_tool',
        ),
    ]
