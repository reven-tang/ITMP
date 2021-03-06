# Generated by Django 2.0.7 on 2018-08-07 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0006_dpmap'),
    ]

    operations = [
        migrations.AddField(
            model_name='deviceinfo',
            name='devstatus',
            field=models.CharField(choices=[('Online', '在线'), ('Offline', '下线'), ('Unknown', '未知'), ('Fault', '故障'), ('Backup', '备用')], default='Online', max_length=16, verbose_name='设备状态'),
        ),
        migrations.AddField(
            model_name='deviceinfo',
            name='devtype',
            field=models.CharField(choices=[('VM', '虚拟机'), ('PM', '物理机'), ('Other', '其他')], default='VM', max_length=16, verbose_name='设备类型'),
        ),
        migrations.AlterField(
            model_name='deviceinfo',
            name='ostype',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='操作系统'),
        ),
    ]
