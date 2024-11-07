# Generated by Django 5.1 on 2024-11-07 00:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='funcionario',
            name='is_gestor',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='funcionario',
            name='is_rh',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='setor',
            name='gestor',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
