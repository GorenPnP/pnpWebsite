# Generated by Django 3.1.4 on 2021-01-02 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0062_auto_20201228_2308'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modulequestion',
            options={'ordering': ['module', 'num'], 'verbose_name': 'Frage eines Moduls', 'verbose_name_plural': 'Fragen eines Moduls'},
        ),
        migrations.AlterModelOptions(
            name='spielerquestion',
            options={'ordering': ['spieler'], 'verbose_name': 'Fragendurchlauf eines Spielers', 'verbose_name_plural': 'Fragendurchläufe eines Spielers'},
        ),
        migrations.AddField(
            model_name='modulequestion',
            name='num',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='spielerquestion',
            name='moduleQuestions',
            field=models.ManyToManyField(to='quiz.ModuleQuestion'),
        ),
        migrations.AlterUniqueTogether(
            name='modulequestion',
            unique_together={('module', 'question')},
        ),
    ]
