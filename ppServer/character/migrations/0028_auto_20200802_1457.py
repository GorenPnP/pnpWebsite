# Generated by Django 2.2.14 on 2020-08-02 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0027_remove_gfsstufenplan_ap_max'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gfsstufenplan',
            name='weiteres',
            field=models.TextField(blank=True, default=None, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='professionstufenplan',
            name='weiteres',
            field=models.TextField(blank=True, default=None, max_length=1000, null=True),
        ),
    ]
