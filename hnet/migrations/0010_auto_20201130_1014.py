# Generated by Django 3.0.7 on 2020-11-30 10:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hnet', '0009_unfoundrecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='structuredpost',
            name='original',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='hnet.Raw'),
        ),
    ]
