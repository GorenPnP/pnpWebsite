# Generated by Django 4.1.7 on 2023-12-18 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dex', '0016_spielermonster'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spielermonster',
            name='name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
