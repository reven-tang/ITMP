# Generated by Django 2.0.7 on 2018-08-22 13:53

from django.db import migrations
import mdeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0009_auto_20180821_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='body',
            field=mdeditor.fields.MDTextField(verbose_name='内容'),
        ),
    ]
