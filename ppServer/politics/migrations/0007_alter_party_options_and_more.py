# Generated by Django 4.2.8 on 2024-09-24 08:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('politics', '0006_remove_party_description_party_program_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='party',
            options={'ordering': ['leftwing_tendency', 'name'], 'verbose_name': 'Partei', 'verbose_name_plural': 'Parteien'},
        ),
        migrations.RenameField(
            model_name='party',
            old_name='rightwing_tendency',
            new_name='leftwing_tendency',
        ),
    ]
