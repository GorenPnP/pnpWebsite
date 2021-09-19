# Generated by Django 3.1.5 on 2021-06-29 20:08

from django.db import migrations, models
import django.db.models.deletion
import mining.models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0042_auto_20210629_2208'),
        ('mining', '0016_auto_20210530_2113'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('width', models.PositiveSmallIntegerField(default=1)),
                ('height', models.PositiveSmallIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('width', models.PositiveSmallIntegerField(default=1)),
                ('height', models.PositiveSmallIntegerField(default=1)),
                ('max_amount', models.PositiveSmallIntegerField(default=1)),
                ('bg_color', models.CharField(default='#555555', max_length=7, validators=[mining.models.is_rgb_color])),
                ('crafting_item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='shop.tinker')),
            ],
            options={
                'ordering': ['crafting_item__name'],
            },
        ),
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(default=0)),
                ('position', models.JSONField(default=dict)),
                ('rotated', models.BooleanField(default=False)),
                ('inventory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mining.inventory')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mining.item')),
            ],
            options={
                'ordering': ['inventory'],
            },
        ),
        migrations.AddField(
            model_name='entity',
            name='inventory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mining.inventory'),
        ),
        migrations.AddField(
            model_name='profileentity',
            name='inventory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mining.inventory'),
        ),
    ]