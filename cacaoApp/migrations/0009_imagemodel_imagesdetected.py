# Generated by Django 4.2.13 on 2024-05-19 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cacaoApp', '0008_alter_imagemodel_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagemodel',
            name='imagesDetected',
            field=models.ImageField(blank=True, null=True, upload_to='cacaodetected/'),
        ),
    ]
