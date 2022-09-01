# Generated by Django 3.1.7 on 2022-04-15 07:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('time_space', '0009_auto_20220412_1453'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metasplinter',
            fields=[
                ('splinter_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='time_space.splinter')),
            ],
            options={
                'abstract': False,
            },
            bases=('time_space.splinter',),
        ),
        migrations.AlterField(
            model_name='timedelayer',
            name='prev_output',
            field=models.TextField(blank=True, default=''),
        ),
    ]