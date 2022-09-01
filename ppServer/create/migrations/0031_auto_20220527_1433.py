# Generated by Django 3.1.7 on 2022-05-27 12:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0062_charakter_begleiter'),
        ('create', '0030_newcharakter_konzentration'),
    ]

    operations = [
        migrations.AddField(
            model_name='priotable',
            name='spF_wF',
            field=models.PositiveIntegerField(default=0, verbose_name='Anz. Sp-F und Wissens-F.'),
        ),
        migrations.CreateModel(
            name='NewCharacterPersönlichkeit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('char', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='create.newcharakter')),
                ('persönlichkeit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.persönlichkeit')),
            ],
            options={
                'ordering': ['char', 'persönlichkeit'],
                'unique_together': {('persönlichkeit', 'char')},
            },
        ),
    ]