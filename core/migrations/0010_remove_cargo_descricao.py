# Generated by Django 5.1.1 on 2024-11-19 15:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_cargo_competencias_cargo_escopo_atividade'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cargo',
            name='descricao',
        ),
    ]
