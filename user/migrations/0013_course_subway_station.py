# Generated by Django 5.0.7 on 2024-07-27 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_remove_course_subway_delete_subway'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='subway_station',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]