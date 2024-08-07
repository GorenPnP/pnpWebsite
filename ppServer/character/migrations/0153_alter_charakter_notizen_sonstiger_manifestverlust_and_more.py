# Generated by Django 4.2.8 on 2024-07-22 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0152_charakter_astralwiderstand_pro_erfolg_bonus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charakter',
            name='notizen_sonstiger_manifestverlust',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='relalchemie',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relausrüstung_technik',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relbegleiter',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='releinbauten',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relengelsroboter',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relfahrzeug',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relitem',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relmagazin',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relmagische_ausrüstung',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relpfeil_bolzen',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relrituale_runen',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relrüstung',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relschusswaffen',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='reltinker',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relvergessenerzauber',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relwaffen_werkzeuge',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relzauber',
            name='stufe',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
    ]
