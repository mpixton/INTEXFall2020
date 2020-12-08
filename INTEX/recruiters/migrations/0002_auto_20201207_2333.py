# Generated by Django 3.1.2 on 2020-12-08 06:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recruiters', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruiter',
            name='org',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recruiters.organization', verbose_name='Organization Name'),
        ),
    ]