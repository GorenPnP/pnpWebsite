# Generated by Django 3.1.5 on 2021-04-25 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mining', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Decoration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('icon', models.ImageField(upload_to='')),
            ],
            options={
                'verbose_name': 'Dekoration',
                'verbose_name_plural': 'Dekorationen',
            },
        ),
    ]
