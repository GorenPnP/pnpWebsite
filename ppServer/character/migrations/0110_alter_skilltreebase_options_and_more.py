# Generated by Django 4.1.7 on 2023-07-25 11:01

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0109_auto_20230725_1213'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='skilltreebase',
            options={'ordering': ['stufe'], 'verbose_name': 'Base Skilltree', 'verbose_name_plural': 'Base Skilltrees'},
        ),
        migrations.AlterUniqueTogether(
            name='skilltreebase',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='gfs',
            name='icon',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, null=True, quality=-1, scale=None, size=[64, 64], upload_to=''),
        ),
        migrations.AddField(
            model_name='gfs',
            name='image',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, null=True, quality=-1, scale=None, size=[1024, 1024], upload_to=''),
        ),
        migrations.AlterField(
            model_name='skilltreebase',
            name='stufe',
            field=models.PositiveIntegerField(default=1, unique=True, validators=[django.core.validators.MaxValueValidator(10)]),
        ),
        migrations.CreateModel(
            name='MachinereadableSkilltreeEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation', models.CharField(choices=[('a', 'AP'), ('f', 'FP'), ('F', 'FG'), ('i', 'IP'), ('t', 'TP'), ('s', 'neue Spezialfertigkeit'), ('w', 'neue Wissensfertigkeit'), ('S', 'WP in Spezialfertigkeit'), ('W', 'WP in Wissensfertigkeit'), ('', 'Roleplay-Text')], default='', max_length=1)),
                ('amount', models.SmallIntegerField(default=1)),
                ('text', models.TextField(blank=True, null=True)),
                ('fertigkeit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.fertigkeit')),
                ('nachteil', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.nachteil')),
                ('skilltree_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.skilltreeentrygfs')),
                ('spezialfertigkeit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.spezialfertigkeit')),
                ('vorteil', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.vorteil')),
                ('wissensfertigkeit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.wissensfertigkeit')),
            ],
        ),
        migrations.RemoveField(
            model_name='skilltreebase',
            name='kind',
        ),
    ]
