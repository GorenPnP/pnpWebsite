# Generated by Django 2.2.13 on 2020-08-15 17:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0032_auto_20200815_1924'),
    ]

    operations = [
        migrations.RenameField(
            model_name='firmaalchemie',
            old_name='preis_int',
            new_name='preis',
        ),
        migrations.RenameField(
            model_name='firmaausrüstung_technik',
            old_name='preis_int',
            new_name='preis',
        ),
        migrations.RenameField(
            model_name='firmaeinbauten',
            old_name='preis_int',
            new_name='preis',
        ),
        migrations.RenameField(
            model_name='firmafahrzeug',
            old_name='preis_int',
            new_name='preis',
        ),
        migrations.RenameField(
            model_name='firmaitem',
            old_name='preis_int',
            new_name='preis',
        ),
        migrations.RenameField(
            model_name='firmamagazin',
            old_name='preis_int',
            new_name='preis',
        ),
        migrations.RenameField(
            model_name='firmamagische_ausrüstung',
            old_name='preis_int',
            new_name='preis',
        ),
        migrations.RenameField(
            model_name='firmapfeil_bolzen',
            old_name='preis_int',
            new_name='preis',
        ),
        migrations.RenameField(
            model_name='firmarüstungen',
            old_name='preis_int',
            new_name='preis',
        ),
        migrations.RenameField(
            model_name='firmaschusswaffen',
            old_name='preis_int',
            new_name='preis',
        ),
        migrations.RenameField(
            model_name='firmatinker',
            old_name='preis_int',
            new_name='preis',
        ),
        migrations.RenameField(
            model_name='firmawaffen_werkzeuge',
            old_name='preis_int',
            new_name='preis',
        ),
        migrations.RenameField(
            model_name='firmazauber',
            old_name='preis_int',
            new_name='preis',
        ),
    ]
