# Generated by Django 5.2.2 on 2025-06-20 23:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('horario', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='horario',
            options={'ordering': ['dia', 'hora_inicio'], 'verbose_name': 'Horario', 'verbose_name_plural': 'Horarios'},
        ),
    ]
