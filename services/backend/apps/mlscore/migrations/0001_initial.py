# Generated by Django 5.1.6 on 2025-02-14 16:40

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('advertiser', '0001_initial'),
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mlscore',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('score', models.PositiveIntegerField()),
                ('advertiser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mlscores', to='advertiser.advertiser')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mlscores', to='client.client')),
            ],
            options={
                'unique_together': {('advertiser', 'client')},
            },
        ),
    ]
