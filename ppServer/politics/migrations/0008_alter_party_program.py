# Generated by Django 4.2.8 on 2024-09-24 09:13

from django.db import migrations
import markdownfield.models


class Migration(migrations.Migration):

    dependencies = [
        ('politics', '0007_alter_party_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='program',
            field=markdownfield.models.MarkdownField(blank=True, null=True, rendered_field='program_rendered'),
        ),
    ]