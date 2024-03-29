# Generated by Django 4.1.7 on 2023-07-19 17:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0099_alter_gfsability_unique_together_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gfsstufenplan',
            name='special_ability',
        ),
        migrations.RemoveField(
            model_name='gfsstufenplan',
            name='special_ability_description',
        ),
        migrations.CreateModel(
            name='RelGfsAbility',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notizen', models.TextField(blank=True, null=True)),
                ('ability', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.gfsability')),
                ('char', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.charakter')),
            ],
            options={
                'verbose_name': 'Gfs-Fähigkeit',
                'verbose_name_plural': 'Gfs-Fähigkeiten',
                'ordering': ['char', 'ability'],
                'unique_together': {('char', 'ability')},
            },
        ),
        migrations.AddField(
            model_name='charakter',
            name='gfs_fähigkeiten',
            field=models.ManyToManyField(blank=True, through='character.RelGfsAbility', to='character.gfsability'),
        ),
    ]
