# Generated by Django 2.0.5 on 2019-03-19 00:04

from django.db import migrations, models
import quiz.models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0009_auto_20190318_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='notizen_nie_angezeigt',
            field=models.TextField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='question',
            name='notizen_nie_angezeigt',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='answer',
            name='picture',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=quiz.models.upload_and_rename_picture),
        ),
        migrations.AlterField(
            model_name='question',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to=quiz.models.upload_and_rename_picture),
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together={('to_question', 'text', 'picture')},
        ),
    ]
