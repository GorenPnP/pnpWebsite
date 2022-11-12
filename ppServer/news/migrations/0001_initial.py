# Generated by Django 3.1.7 on 2022-09-04 18:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('beschreibung', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Kategorien',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
            options={
                'verbose_name': 'Herausgeber',
                'verbose_name_plural': 'Herausgeber',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titel', models.TextField()),
                ('summary', models.CharField(max_length=300)),
                ('text', models.TextField(blank=True, null=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('last_edit', models.DateTimeField(auto_now=True)),
                ('published', models.BooleanField(default=False)),
                ('categories', models.ManyToManyField(to='news.Category')),
                ('publisher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='news.publisher')),
            ],
            options={
                'verbose_name': 'News',
                'verbose_name_plural': 'News',
                'ordering': ['titel', 'summary'],
            },
        ),
    ]