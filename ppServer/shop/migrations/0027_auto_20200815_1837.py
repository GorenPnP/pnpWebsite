# Generated by Django 2.2.13 on 2020-08-15 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0043_auto_20200815_1837'),
        ('shop', '0026_ausrüstung_technik_manifestverlust_str'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='firmasteinbauten',
            name='firma',
        ),
        migrations.RemoveField(
            model_name='firmasteinbauten',
            name='item',
        ),
        migrations.RemoveField(
            model_name='firmastmagische_ausrüstung',
            name='firma',
        ),
        migrations.RemoveField(
            model_name='firmastmagische_ausrüstung',
            name='item',
        ),
        migrations.RemoveField(
            model_name='firmastwaffen_werkzeuge',
            name='firma',
        ),
        migrations.RemoveField(
            model_name='firmastwaffen_werkzeuge',
            name='item',
        ),
        migrations.RemoveField(
            model_name='stausrüstung_technik',
            name='firmen',
        ),
        migrations.RemoveField(
            model_name='steinbauten',
            name='firmen',
        ),
        migrations.RemoveField(
            model_name='stmagische_ausrüstung',
            name='firmen',
        ),
        migrations.RemoveField(
            model_name='stwaffen_werkzeuge',
            name='firmen',
        ),
        migrations.DeleteModel(
            name='FirmaStAusrüstung_Technik',
        ),
        migrations.DeleteModel(
            name='FirmaStEinbauten',
        ),
        migrations.DeleteModel(
            name='FirmaStMagische_Ausrüstung',
        ),
        migrations.DeleteModel(
            name='FirmaStWaffen_Werkzeuge',
        ),
        migrations.DeleteModel(
            name='StAusrüstung_Technik',
        ),
        migrations.DeleteModel(
            name='StEinbauten',
        ),
        migrations.DeleteModel(
            name='StMagische_Ausrüstung',
        ),
        migrations.DeleteModel(
            name='StWaffen_Werkzeuge',
        ),
    ]
