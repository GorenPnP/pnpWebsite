# Generated by Django 2.2.13 on 2020-09-23 10:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0046_auto_20200916_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='icon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='icon', related_query_name='icon', to='quiz.Image'),
        ),
        migrations.AlterField(
            model_name='multiplechoicefield',
            name='img',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quiz.Image'),
        ),
    ]
