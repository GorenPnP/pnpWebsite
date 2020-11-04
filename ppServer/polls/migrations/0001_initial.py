# Generated by Django 2.0.5 on 2018-11-19 18:30

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import polls.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('character', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('votes', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Wahl',
                'verbose_name_plural': 'Wahlen',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('anz_stimmen', models.PositiveIntegerField(default=1, verbose_name='Stimmen pro Person')),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date published')),
                ('deadline', models.DateTimeField(default=polls.models.default_deadline, verbose_name='deadline')),
            ],
            options={
                'verbose_name': 'Umfrage',
                'verbose_name_plural': 'Umfragen',
            },
        ),
        migrations.CreateModel(
            name='QuestionSpieler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.Question')),
                ('spieler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.Spieler')),
            ],
            options={
                'verbose_name': 'hat abgestimmt',
                'verbose_name_plural': 'haben abgestimmt',
            },
        ),
        migrations.AddField(
            model_name='question',
            name='spieler_voted',
            field=models.ManyToManyField(through='polls.QuestionSpieler', to='character.Spieler'),
        ),
        migrations.AddField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.Question'),
        ),
        migrations.AlterUniqueTogether(
            name='questionspieler',
            unique_together={('question', 'spieler')},
        ),
    ]
