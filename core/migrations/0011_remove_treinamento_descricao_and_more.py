# Generated by Django 5.1.1 on 2024-11-19 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_cargo_descricao'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='treinamento',
            name='descricao',
        ),
        migrations.AlterField(
            model_name='treinamento',
            name='data_fim',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='treinamento',
            name='funcionarios',
            field=models.ManyToManyField(to='core.funcionario'),
        ),
        migrations.AlterField(
            model_name='treinamento',
            name='nome',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='treinamento',
            name='skills',
            field=models.ManyToManyField(to='core.skill'),
        ),
    ]