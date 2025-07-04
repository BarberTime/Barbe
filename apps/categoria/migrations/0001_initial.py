# Generated by Django 5.2.2 on 2025-06-18 05:32

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('negocio', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id_categoria', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('negocio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='negocio.negocio')),
            ],
            options={
                'verbose_name': 'Categoria',
                'verbose_name_plural': 'Categorias',
                'db_table': 'categoria',
            },
        ),
    ]
