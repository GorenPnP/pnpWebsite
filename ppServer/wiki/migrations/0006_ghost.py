# Generated by Django 4.2.8 on 2024-01-24 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0005_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ghost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titel', models.CharField(max_length=64, unique=True)),
                ('schnelligkeit', models.CharField(default='', max_length=64)),
                ('angriff', models.CharField(default='', max_length=64)),
                ('ma', models.CharField(default='', max_length=64)),
                ('wk', models.CharField(default='', max_length=64)),
                ('st', models.CharField(default='', max_length=64)),
                ('schaWI', models.CharField(default='', max_length=64)),
                ('reaktion', models.CharField(default='', max_length=64)),
                ('schaden_pro_erfolg', models.CharField(default='', max_length=64)),
                ('initiative', models.CharField(default='', max_length=64)),
                ('astralschaden', models.CharField(default='', max_length=64)),
            ],
            options={
                'verbose_name': 'Geist',
                'verbose_name_plural': 'Geister',
                'ordering': ['titel'],
            },
        ),
    ]
