# Generated by Django 2.2.13 on 2020-07-31 04:50

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0020_remove_charakter_magie_moeglich'),
    ]

    operations = [
        migrations.CreateModel(
            name='GfsFertigkeit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fp', models.IntegerField(default=0)),
                ('pool', models.IntegerField(default=0)),
                ('fertigkeit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.Fertigkeit')),
            ],
            options={
                'verbose_name': 'Fertigkeit',
                'verbose_name_plural': 'Fertigkeiten',
                'ordering': ['gfs', 'fertigkeit'],
            },
        ),
        migrations.CreateModel(
            name='GfsStufenplan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stufe', models.PositiveIntegerField(default=0)),
                ('ep', models.PositiveIntegerField(default=0)),
                ('ap', models.PositiveSmallIntegerField(default=0)),
                ('ap_max', models.PositiveSmallIntegerField(default=0)),
                ('fp', models.PositiveSmallIntegerField(default=0)),
                ('fg', models.PositiveSmallIntegerField(default=0)),
                ('zauber', models.PositiveSmallIntegerField(default=0)),
                ('weiteres', models.TextField(blank=True, default=None, max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'Stufenplan',
                'verbose_name_plural': 'Stufenpläne',
                'ordering': ['gfs', 'stufe'],
            },
        ),
        migrations.CreateModel(
            name='GfsWesenkraft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Wesenkraft',
                'verbose_name_plural': 'Wesenkräfte',
                'ordering': ['gfs', 'wesenkraft'],
            },
        ),
        migrations.CreateModel(
            name='ProfessionStufenplan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stufe', models.PositiveIntegerField(default=0)),
                ('ep', models.PositiveIntegerField(default=0)),
                ('tp', models.PositiveSmallIntegerField(default=0)),
                ('spezial', models.PositiveSmallIntegerField(default=0)),
                ('wissensp', models.PositiveSmallIntegerField(default=0)),
                ('weiteres', models.TextField(blank=True, default=None, max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'Stufenplan',
                'verbose_name_plural': 'Stufenpläne',
                'ordering': ['profession', 'stufe'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='professionvorteil',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='professionvorteil',
            name='profession',
        ),
        migrations.RemoveField(
            model_name='professionvorteil',
            name='teil',
        ),
        migrations.AlterUniqueTogether(
            name='speziesnachteil',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='speziesnachteil',
            name='spezies',
        ),
        migrations.RemoveField(
            model_name='speziesnachteil',
            name='teil',
        ),
        migrations.AlterUniqueTogether(
            name='speziesvorteil',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='speziesvorteil',
            name='spezies',
        ),
        migrations.RemoveField(
            model_name='speziesvorteil',
            name='teil',
        ),
        migrations.AlterModelOptions(
            name='spezies',
            options={'ordering': ['komplexität'], 'verbose_name': 'Wesen', 'verbose_name_plural': 'Wesen'},
        ),
        migrations.RemoveField(
            model_name='profession',
            name='ap',
        ),
        migrations.RemoveField(
            model_name='profession',
            name='nachteile',
        ),
        migrations.RemoveField(
            model_name='profession',
            name='vorteile',
        ),
        migrations.RemoveField(
            model_name='spezies',
            name='ap',
        ),
        migrations.RemoveField(
            model_name='spezies',
            name='nachteile',
        ),
        migrations.RemoveField(
            model_name='spezies',
            name='startmanifest',
        ),
        migrations.RemoveField(
            model_name='spezies',
            name='vorteile',
        ),
        migrations.RemoveField(
            model_name='spezies',
            name='wesenschaden_andere_gestalt',
        ),
        migrations.RemoveField(
            model_name='spezies',
            name='wesenschaden_waff_kampf',
        ),
        migrations.AddField(
            model_name='gfs',
            name='startmanifest',
            field=models.DecimalField(decimal_places=2, default=10.0, max_digits=4, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0)], verbose_name='Startmanifest'),
        ),
        migrations.AddField(
            model_name='gfs',
            name='wesenschaden_andere_gestalt',
            field=models.IntegerField(blank=True, null=True, verbose_name='BS andere Gestalt'),
        ),
        migrations.AddField(
            model_name='gfs',
            name='wesenschaden_waff_kampf',
            field=models.IntegerField(default=0, verbose_name='BS'),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='ip',
            field=models.IntegerField(default=0, verbose_name='ip'),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='tp',
            field=models.IntegerField(default=0, verbose_name='tp'),
        ),
        migrations.DeleteModel(
            name='ProfessionNachteil',
        ),
        migrations.DeleteModel(
            name='ProfessionVorteil',
        ),
        migrations.DeleteModel(
            name='SpeziesNachteil',
        ),
        migrations.DeleteModel(
            name='SpeziesVorteil',
        ),
        migrations.AddField(
            model_name='professionstufenplan',
            name='profession',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.Spezies'),
        ),
        migrations.AddField(
            model_name='gfswesenkraft',
            name='gfs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.Gfs'),
        ),
        migrations.AddField(
            model_name='gfswesenkraft',
            name='wesenkraft',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.Wesenkraft'),
        ),
        migrations.AddField(
            model_name='gfsstufenplan',
            name='gfs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.Gfs'),
        ),
        migrations.AddField(
            model_name='gfsstufenplan',
            name='vorteile',
            field=models.ManyToManyField(blank=True, to='character.Vorteil'),
        ),
        migrations.AddField(
            model_name='gfsstufenplan',
            name='wesenkräfte',
            field=models.ManyToManyField(blank=True, to='character.Wesenkraft'),
        ),
        migrations.AddField(
            model_name='gfsfertigkeit',
            name='gfs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.Gfs'),
        ),
        migrations.AddField(
            model_name='gfs',
            name='fertigkeiten',
            field=models.ManyToManyField(through='character.GfsFertigkeit', to='character.Fertigkeit'),
        ),
        migrations.AddField(
            model_name='gfs',
            name='wesenkraft',
            field=models.ManyToManyField(through='character.GfsWesenkraft', to='character.Wesenkraft'),
        ),
        migrations.AlterUniqueTogether(
            name='professionstufenplan',
            unique_together={('profession', 'stufe')},
        ),
        migrations.AlterUniqueTogether(
            name='gfswesenkraft',
            unique_together={('gfs', 'wesenkraft')},
        ),
        migrations.AlterUniqueTogether(
            name='gfsstufenplan',
            unique_together={('gfs', 'stufe')},
        ),
        migrations.AlterUniqueTogether(
            name='gfsfertigkeit',
            unique_together={('gfs', 'fertigkeit')},
        ),
    ]
