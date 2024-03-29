# Generated by Django 3.1.7 on 2022-05-27 12:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0045_auto_20220527_1348'),
        ('character', '0060_auto_20220527_1354'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='relbegleiter',
            options={'verbose_name': 'Begleiter', 'verbose_name_plural': 'Begleiter'},
        ),
        migrations.AddField(
            model_name='relbegleiter',
            name='anz',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='relbegleiter',
            name='item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.begleiter'),
        ),
        migrations.AddField(
            model_name='relbegleiter',
            name='stufe',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='relbegleiter',
            name='notizen',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='relbegleiter',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='relbegleiter',
            name='begleiter',
        ),
        migrations.RemoveField(
            model_name='relbegleiter',
            name='status',
        ),
    ]
