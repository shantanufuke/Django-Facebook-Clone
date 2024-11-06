# Generated by Django 5.1.1 on 2024-11-02 17:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_friendrequest_options_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='comment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.comment'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.post'),
        ),
    ]
