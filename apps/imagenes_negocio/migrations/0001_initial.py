# Generated by Django 5.2.2 on 2025-06-18 05:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('negocio', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImagenesNegocio',
            fields=[
                ('id_imagen', models.AutoField(primary_key=True, serialize=False)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='negocios/imagenes/')),
                ('negocio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='negocio.negocio')),
            ],
            options={
                'verbose_name': 'ImagenesNegocio',
                'verbose_name_plural': 'ImagenesNegocios',
                'db_table': 'imagenes_negocio',
            },
        ),
    ]
