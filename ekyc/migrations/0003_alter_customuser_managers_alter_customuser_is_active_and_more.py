# Generated by Django 5.1.5 on 2025-02-08 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ekyc", "0002_alter_customuser_is_superuser"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="customuser",
            managers=[],
        ),
        migrations.AlterField(
            model_name="customuser",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="username",
            field=models.CharField(max_length=150, unique=True),
        ),
    ]
