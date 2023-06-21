# Generated by Django 4.1.7 on 2023-06-13 19:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0054_engelsroboter_in_engelsroboter_ma_engelsroboter_st_and_more'),
        ('character', '0081_charakter_prestige_charakter_verzehr'),
    ]

    operations = [
        migrations.AddField(
            model_name='nachteil',
            name='needs_attribut',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='nachteil',
            name='needs_engelsroboter',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='nachteil',
            name='needs_fertigkeit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='nachteil',
            name='needs_ip',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='nachteil',
            name='needs_notiz',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='relnachteil',
            name='engelsroboter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.engelsroboter'),
        ),
        migrations.AddField(
            model_name='relnachteil',
            name='fertigkeit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.fertigkeit'),
        ),
        migrations.AddField(
            model_name='relnachteil',
            name='ip',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='relvorteil',
            name='ip',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vorteil',
            name='needs_attribut',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vorteil',
            name='needs_engelsroboter',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vorteil',
            name='needs_fertigkeit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vorteil',
            name='needs_ip',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vorteil',
            name='needs_notiz',
            field=models.BooleanField(default=False),
        ),
    ]
