# Generated by Django 4.1.7 on 2023-03-17 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0064_gfsstufenplanbase_tp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gfsstufenplan',
            old_name='weiteres',
            new_name='special_ability_description',
        ),
    ]
