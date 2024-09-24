# Generated by Django 4.2.8 on 2024-09-24 08:41

from django.db import migrations
import markdownfield.models


class Migration(migrations.Migration):

    dependencies = [
        ('politics', '0005_remove_legalact_voting_deadline'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='party',
            name='description',
        ),
        migrations.AddField(
            model_name='party',
            name='program',
            field=markdownfield.models.MarkdownField(blank=True, null=True, rendered_field='text_rendered'),
        ),
        migrations.AddField(
            model_name='party',
            name='program_rendered',
            field=markdownfield.models.RenderedMarkdownField(null=True),
        ),
    ]
