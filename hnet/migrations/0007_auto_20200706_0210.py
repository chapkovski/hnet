# Generated by Django 3.0.7 on 2020-07-06 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hnet', '0006_auto_20200706_0155'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='secondary',
        ),
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.CharField(default=1, max_length=1000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='institution',
            name='description',
            field=models.CharField(default=1, max_length=1000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='position',
            name='description',
            field=models.CharField(default=1, max_length=1000),
            preserve_default=False,
        ),
    ]
