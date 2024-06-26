# Generated by Django 4.2.8 on 2024-05-27 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0149_remove_charakter_konzentration_bonus'),
        ('shop', '0060_alter_alchemie_kategorie_and_more'),
        ('effect', '0010_alter_effect_options_alter_releffect_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='effect',
            name='source_shopAusrüstungTechnik',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.ausrüstung_technik'),
        ),
        migrations.AddField(
            model_name='effect',
            name='source_shopBegleiter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.begleiter'),
        ),
        migrations.AddField(
            model_name='effect',
            name='source_shopEinbauten',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.einbauten'),
        ),
        migrations.AddField(
            model_name='effect',
            name='source_shopMagischeAusrüstung',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.magische_ausrüstung'),
        ),
        migrations.AddField(
            model_name='effect',
            name='source_shopRüstung',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.rüstungen'),
        ),
        migrations.AddField(
            model_name='releffect',
            name='source_shopAusrüstungTechnik',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='character.relausrüstung_technik'),
        ),
        migrations.AddField(
            model_name='releffect',
            name='source_shopBegleiter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='character.relbegleiter'),
        ),
        migrations.AddField(
            model_name='releffect',
            name='source_shopEinbauten',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='character.releinbauten'),
        ),
        migrations.AddField(
            model_name='releffect',
            name='source_shopMagischeAusrüstung',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='character.relmagische_ausrüstung'),
        ),
        migrations.AddField(
            model_name='releffect',
            name='source_shopRüstung',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='character.relrüstung'),
        ),
    ]
