# Generated by Django 4.1.7 on 2023-07-31 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0124_remove_gfsnachteil_anzahl_remove_gfsvorteil_anzahl_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wesenkraft',
            old_name='zusatz_gfsspezifisch',
            new_name='skilled_gfs',
        ),
    ]
