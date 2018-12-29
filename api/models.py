from django.db import models

# Create your models here.

class MonitorInfo(models.Model):
    ipaddr = models.CharField('IP地址', max_length=16, blank=True, null=True)
    hostname = models.CharField('主机名称', max_length=32, blank=True, null=True)
    platform = models.CharField('平台', max_length=64, blank=True, null=True)
    cpucorecount = models.PositiveSmallIntegerField('CPU核数(C)', default=0)
    memsize = models.IntegerField('内存大小(GB)', default=0)
    kpi = models.CharField('性能指标', max_length=32, blank=True, null=True)
    values = models.CharField('采集值', max_length=32, blank=True, null=True)
    mtime = models.CharField('采集时间', max_length=32, blank=True, null=True)


    def __str__(self):
        return self.ipaddr

    class Meta:
        verbose_name = '监控信息表'
        verbose_name_plural = "监控信息表"
        managed = True
        db_table = 't_monitor_info'