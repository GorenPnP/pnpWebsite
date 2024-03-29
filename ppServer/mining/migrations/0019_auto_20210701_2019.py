# Generated by Django 3.1.5 on 2021-07-01 18:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0054_auto_20201223_1709'),
        ('crafting', '0017_auto_20210425_1400'),
        ('mining', '0018_auto_20210629_2217'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inventory',
            options={'verbose_name': 'Inventar', 'verbose_name_plural': 'Inventare'},
        ),
        migrations.AlterModelOptions(
            name='inventoryitem',
            options={'ordering': ['inventory'], 'verbose_name': 'Inventar-Item', 'verbose_name_plural': 'Inventar-Items'},
        ),
        migrations.AlterModelOptions(
            name='item',
            options={'ordering': ['crafting_item__name'], 'verbose_name': 'Item Model fürs Inventar', 'verbose_name_plural': 'Item Models fürs Inventar'},
        ),
        migrations.CreateModel(
            name='RelProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inventory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mining.inventory')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crafting.profile')),
                ('spieler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.spieler', unique=True)),
            ],
            options={
                'ordering': ['spieler', 'profile'],
                'unique_together': {('spieler', 'profile')},
            },
        ),
    ]
