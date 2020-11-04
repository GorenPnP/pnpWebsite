# Generated by Django 2.2.13 on 2020-08-13 02:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0040_auto_20200813_0438'),
        ('create', '0015_auto_20200813_0417'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewCharakterTalent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'ordering': ['char', 'talent'],
                'verbose_name_plural': 'Starttalente',
                'verbose_name': 'Starttalent',
            },
        ),
        migrations.RemoveField(
            model_name='newcharakter',
            name='wesenkräfte',
        ),
        migrations.DeleteModel(
            name='NewCharakterWesenkraft',
        ),
        migrations.AddField(
            model_name='newcharaktertalent',
            name='char',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='create.NewCharakter'),
        ),
        migrations.AddField(
            model_name='newcharaktertalent',
            name='talent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.Talent'),
        ),
        migrations.AddField(
            model_name='newcharakter',
            name='talente',
            field=models.ManyToManyField(through='create.NewCharakterTalent', to='character.Talent'),
        ),
        migrations.AlterUniqueTogether(
            name='newcharaktertalent',
            unique_together={('talent', 'char')},
        ),
    ]
