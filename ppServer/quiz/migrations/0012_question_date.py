# Generated by Django 2.0.5 on 2019-03-28 22:27

from django.db import migrations, models
import quiz.models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0011_answer_message_on_wrong_answered'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='date',
            field=models.DateField(),
        ),
    ]
