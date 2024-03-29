# Generated by Django 3.1.7 on 2022-05-27 11:48

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0044_auto_20220514_1539'),
    ]

    operations = [
        migrations.CreateModel(
            name='Begleiter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50, unique=True)),
                ('beschreibung', models.TextField(blank=True, default='', max_length=1500)),
                ('icon', models.ImageField(blank=True, null=True, upload_to='')),
                ('ab_stufe', models.IntegerField(blank=True, default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('illegal', models.BooleanField(default=False)),
                ('lizenz_benötigt', models.BooleanField(default=False)),
                ('frei_editierbar', models.BooleanField(default=True)),
                ('stufenabhängig', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Begleiter',
                'verbose_name_plural': 'Begleiter',
                'ordering': ['name'],
            },
        ),
        migrations.RemoveField(
            model_name='firma',
            name='price_factor',
        ),
        migrations.CreateModel(
            name='FirmaBegleiter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preis', models.IntegerField(default=0, null=True)),
                ('verfügbarkeit', models.PositiveIntegerField(default=0)),
                ('firma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.firma')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.begleiter')),
            ],
            options={
                'verbose_name': 'Firma',
                'verbose_name_plural': 'Firmen',
                'ordering': ['item', 'firma'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='begleiter',
            name='firmen',
            field=models.ManyToManyField(blank=True, through='shop.FirmaBegleiter', to='shop.Firma'),
        ),
    ]
