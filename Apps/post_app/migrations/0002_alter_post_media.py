# Generated by Django 5.2 on 2025-07-03 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='media',
            field=models.URLField(),
        ),
    ]
