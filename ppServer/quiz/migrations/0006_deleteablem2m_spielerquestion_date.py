# Generated by Django 2.0.5 on 2019-03-15 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0005_auto_20190315_1314'),
    ]

    operations = [
        migrations.AddField(
            model_name='deleteablem2m_spielerquestion',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
