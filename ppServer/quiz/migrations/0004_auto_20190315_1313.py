# Generated by Django 2.0.5 on 2019-03-15 12:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_auto_20190314_0141'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeleteableM2M_Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Question')),
            ],
        ),
        migrations.CreateModel(
            name='DeleteableM2M_SpielerQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='questionsession',
            name='questions_to_answer',
        ),
        migrations.RemoveField(
            model_name='questionsession',
            name='results',
        ),
        migrations.AddField(
            model_name='questionsession',
            name='actual_question',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='quiz.Question'),
        ),
        migrations.AddField(
            model_name='deleteablem2m_spielerquestion',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.QuestionSession'),
        ),
        migrations.AddField(
            model_name='deleteablem2m_spielerquestion',
            name='spielerQuestion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.SpielerQuestion'),
        ),
        migrations.AddField(
            model_name='deleteablem2m_question',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.QuestionSession'),
        ),
    ]
