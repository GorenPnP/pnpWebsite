# Generated by Django 3.1.5 on 2021-05-30 19:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mining', '0015_auto_20210530_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profileentity',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mining.region'),
        ),
    ]