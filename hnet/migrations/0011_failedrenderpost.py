# Generated by Django 3.0.7 on 2020-11-30 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hnet', '0010_auto_20201130_1014'),
    ]

    operations = [
        migrations.CreateModel(
            name='FailedRenderPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField()),
            ],
        ),
    ]
