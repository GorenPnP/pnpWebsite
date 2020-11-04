# Generated by Django 2.2.13 on 2020-10-12 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0036_auto_20201012_1121'),
        ('character', '0052_auto_20200923_1257'),
    ]

    operations = [
        migrations.CreateModel(
            name='Crafter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('craftingTime', models.DurationField(blank=True, null=True)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.Spieler')),
            ],
        ),
        migrations.CreateModel(
            name='inventory_item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('char', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crafting.Crafter')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Tinker')),
            ],
        ),
    ]
