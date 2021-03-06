# Generated by Django 2.2.13 on 2020-09-16 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0045_auto_20200916_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='spielerquestion',
            name='answer_file',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quiz.File'),
        ),
        migrations.AddField(
            model_name='spielerquestion',
            name='answer_img',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quiz.Image'),
        ),
        migrations.AddField(
            model_name='spielerquestion',
            name='answer_mc',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='spielerquestion',
            name='answer_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
