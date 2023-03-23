# Generated by Django 4.1.4 on 2023-02-02 17:29

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('character', '0064_gfsstufenplanbase_tp'),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('card_id', models.PositiveBigIntegerField()),
                ('name', models.CharField(default='default', max_length=200)),
                ('money', models.DecimalField(decimal_places=0, default=0, max_digits=15)),
                ('active', models.BooleanField(default=False)),
                ('spieler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.spieler')),
            ],
            options={
                'verbose_name': 'NFC-Karte',
                'verbose_name_plural': 'NFC-Karten',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=0, default=1, max_digits=15, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('reason', models.TextField(max_length=200)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='receiver', related_query_name='receiver', to='cards.card')),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sender', related_query_name='sender', to='cards.card')),
            ],
            options={
                'verbose_name': 'Transaktion',
                'verbose_name_plural': 'Transaktionen',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='RelCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cards.card')),
                ('spieler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.spieler')),
            ],
            options={
                'ordering': ['spieler'],
            },
        ),
    ]