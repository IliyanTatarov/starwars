# Generated by Django 3.2.3 on 2021-05-19 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('csv_file', models.FileField(upload_to='csv/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
