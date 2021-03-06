# Generated by Django 2.0.5 on 2019-03-12 00:14

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('character', '0009_auto_20190311_1518'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(default='', max_length=200)),
                ('correct', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Answer',
                'verbose_name_plural': 'Answers',
                'ordering': ['to_question', 'text'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('difficulty', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(13)])),
                ('question', models.TextField(default='', max_length=300)),
                ('points', models.PositiveSmallIntegerField(default=0)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='')),
            ],
            options={
                'verbose_name': 'Question',
                'verbose_name_plural': 'Questions',
                'ordering': ['topic', 'difficulty'],
            },
        ),
        migrations.CreateModel(
            name='QuestionSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('achieved', models.PositiveSmallIntegerField(blank=True, default=0)),
                ('max', models.PositiveSmallIntegerField(blank=True, default=0)),
            ],
            options={
                'verbose_name': 'Question-Session',
                'verbose_name_plural': 'Question-Sessions',
                'ordering': ['spieler'],
            },
        ),
        migrations.CreateModel(
            name='SpielerQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('correct', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Question')),
                ('spieler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.Spieler')),
            ],
            options={
                'verbose_name': "Spieler's Question",
                'verbose_name_plural': "Spieler's Questions",
                'ordering': ['spieler', 'question'],
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titel', models.CharField(default='', max_length=100)),
            ],
            options={
                'verbose_name': 'Subject',
                'verbose_name_plural': 'Subjects',
                'ordering': ['titel'],
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titel', models.CharField(default='', max_length=100)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Subject')),
            ],
            options={
                'verbose_name': 'Topic',
                'verbose_name_plural': 'Topics',
                'ordering': ['subject', 'titel'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='subject',
            unique_together={('titel',)},
        ),
        migrations.AddField(
            model_name='questionsession',
            name='results',
            field=models.ManyToManyField(related_name='results', related_query_name='results', to='quiz.SpielerQuestion'),
        ),
        migrations.AddField(
            model_name='questionsession',
            name='spieler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.Spieler'),
        ),
        migrations.AddField(
            model_name='question',
            name='beantwortet_von',
            field=models.ManyToManyField(related_name='beantwortet_von', related_query_name='beantwortet_von', through='quiz.SpielerQuestion', to='character.Spieler'),
        ),
        migrations.AddField(
            model_name='question',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Topic'),
        ),
        migrations.AddField(
            model_name='answer',
            name='to_question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Question'),
        ),
        migrations.AlterUniqueTogether(
            name='topic',
            unique_together={('titel', 'subject')},
        ),
        migrations.AlterUniqueTogether(
            name='spielerquestion',
            unique_together={('spieler', 'question')},
        ),
        migrations.AlterUniqueTogether(
            name='questionsession',
            unique_together={('spieler',)},
        ),
        migrations.AlterUniqueTogether(
            name='question',
            unique_together={('question', 'difficulty', 'topic')},
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together={('to_question', 'text')},
        ),
    ]
