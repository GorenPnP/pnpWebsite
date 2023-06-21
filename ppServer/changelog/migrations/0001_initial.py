# Generated by Django 4.1.7 on 2023-06-03 19:59

from django.db import migrations, models
import markdownfield.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Changelog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_created=True)),
                ('text', markdownfield.models.MarkdownField(rendered_field='text_rendered')),
                ('text_rendered', markdownfield.models.RenderedMarkdownField()),
            ],
        ),
    ]