# Generated by Django 2.0.5 on 2019-03-28 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0012_question_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
