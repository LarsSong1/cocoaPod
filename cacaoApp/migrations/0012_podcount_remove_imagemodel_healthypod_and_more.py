# Generated by Django 4.2.13 on 2024-05-20 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cacaoApp', '0011_imagemodel_healthypod_imagemodel_moniliapod_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PodCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('healthyPod', models.IntegerField(default=0)),
                ('moniliaPod', models.IntegerField(default=0)),
                ('pythophoraPod', models.IntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name='imagemodel',
            name='healthyPod',
        ),
        migrations.RemoveField(
            model_name='imagemodel',
            name='moniliaPod',
        ),
        migrations.RemoveField(
            model_name='imagemodel',
            name='pythophoraPod',
        ),
        migrations.AddField(
            model_name='imagemodel',
            name='podCount_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cacaoApp.podcount'),
        ),
    ]
