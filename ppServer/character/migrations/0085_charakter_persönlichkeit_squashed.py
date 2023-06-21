# Generated by Django 4.1.7 on 2023-06-21 16:16

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0084_nachteil_max_ip_nachteil_min_ip_vorteil_max_ip_and_more'),
        ('shop', '0054_engelsroboter_in_engelsroboter_ma_engelsroboter_st_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charakter',
            name='ap',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='fg',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='fp',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='ip',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='sp',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='tp',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='zauberplätze',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='charakter',
            name='spF_wF',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='charakter',
            name='wp',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='relattribut',
            name='aktuellerWert_fix',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='relattribut',
            name='maxWert_fix',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='gewicht',
            field=models.PositiveIntegerField(blank=True, default=75, verbose_name='Gewicht in kg'),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='größe',
            field=models.PositiveIntegerField(blank=True, default=170, verbose_name='Größe in cm'),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='präf_arm',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='präferierter Arm (rechts/links?)'),
        ),
        migrations.AddField(
            model_name='gfsvorteil',
            name='attribut',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.attribut'),
        ),
        migrations.AddField(
            model_name='gfsvorteil',
            name='engelsroboter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.engelsroboter'),
        ),
        migrations.AddField(
            model_name='gfsvorteil',
            name='fertigkeit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.fertigkeit'),
        ),
        migrations.AddField(
            model_name='gfsvorteil',
            name='ip',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='gfsnachteil',
            name='attribut',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.attribut'),
        ),
        migrations.AddField(
            model_name='gfsnachteil',
            name='engelsroboter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.engelsroboter'),
        ),
        migrations.AddField(
            model_name='gfsnachteil',
            name='fertigkeit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.fertigkeit'),
        ),
        migrations.AddField(
            model_name='gfsnachteil',
            name='ip',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='relattribut',
            name='aktuellerWert_temp',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='relattribut',
            name='maxWert_temp',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='relattribut',
            name='fg_temp',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='relfertigkeit',
            name='fp_temp',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='gfsstufenplan',
            name='special_ability',
            field=models.CharField(blank=True, default=None, max_length=100, null=True, verbose_name='Fähigkeit'),
        ),
        migrations.AddField(
            model_name='relzauber',
            name='will_create',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='relzauber',
            name='tier',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AddField(
            model_name='charakter',
            name='persönlichkeit',
            field=models.ManyToManyField(blank=True, to='character.persönlichkeit'),
        ),
        migrations.AddField(
            model_name='relzauber',
            name='tier_notes',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
