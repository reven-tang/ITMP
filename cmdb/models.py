from django.db import models

# Create your models here.

class DeviceInfo(models.Model):
    dev_status = (
        ('Online', '在线'),
        ('Offline', '下线'),
        ('Unknown', '未知'),
        ('Fault', '故障'),
        ('Backup', '备用'),
        )
    dev_type = (
        ('VM', '虚拟机'),
        ('PM', '物理机'),
        ('Other', '其他'),
    )
    devid = models.AutoField('设备ID', primary_key=True)
    devip = models.CharField('设备IP地址', max_length=16, unique=True)
    devname = models.CharField('设备名称', max_length=32, blank=True, null=True)
    devnamealias = models.CharField('设备别名', max_length=32, blank=True, null=True)
    ostype = models.CharField('操作系统', max_length=64, blank=True, null=True)
    devtype = models.CharField('设备类型', choices=dev_type, max_length=16, default='VM')
    devstatus = models.CharField('设备状态', choices=dev_status, max_length=16, default='Online')
    cpusize = models.FloatField('CPU大小(GHz)', default=0.0)
    cpucorecount = models.PositiveSmallIntegerField('CPU核数', default=0)
    memsize = models.IntegerField('内存大小(GB)', default=0)
    disksize = models.FloatField('磁盘容量(GB)', default=0.0)
    location = models.CharField('机房位置', max_length=64, blank=True, null=True)
    devdesc = models.CharField('设备描述', max_length=256, blank=True, null=True)
    pdappsystem = models.ManyToManyField('ProjectInfo', blank=True, verbose_name="应用系统")
    customer1 = models.CharField('自定义字段1', max_length=256, blank=True, null=True)
    customer2 = models.CharField('自定义字段2', max_length=256, blank=True, null=True)
    customer3 = models.CharField('自定义字段3', max_length=256, blank=True, null=True)
    customer4 = models.CharField('自定义字段4', max_length=256, blank=True, null=True)
    customer5 = models.CharField('自定义字段5', max_length=256, blank=True, null=True)
    customer6 = models.CharField('自定义字段6', max_length=256, blank=True, null=True)
    customer7 = models.CharField('自定义字段7', max_length=256, blank=True, null=True)
    customer8 = models.CharField('自定义字段8', max_length=256, blank=True, null=True)

    def __str__(self):
        return self.devip

    class Meta:
        verbose_name = '设备信息表'
        verbose_name_plural = "设备信息表"
        managed = True
        db_table = 't_cmdb_device_info'
        unique_together = (('devid', 'devip'),)

class ProjectInfo(models.Model):
    pid = models.AutoField('项目ID', primary_key=True)
    projname = models.CharField('项目名称', max_length=16)
    appsystem = models.CharField('应用系统', max_length=64, unique=True)
    # dpdevip = models.ManyToManyField('DeviceInfo', blank=True, verbose_name="设备IP地址")
    projdesc = models.CharField('项目描述', max_length=256, blank=True, null=True)
    projcontactname = models.CharField('项目联系人姓名', max_length=10, blank=True, null=True)
    projcontactphone = models.CharField('项目联系人电话', max_length=16, blank=True, null=True)
    projcontactemail = models.EmailField('项目联系人邮箱', max_length=256, blank=True, null=True)
    appcontactname = models.CharField('应用联系人姓名', max_length=10, blank=True, null=True)
    appcontactphone = models.CharField('应用联系人电话', max_length=16, blank=True, null=True)
    appcontactemail = models.EmailField('应用联系人邮箱', max_length=256, blank=True, null=True)
    groupname = models.CharField('小组名称', max_length=32, blank=True, null=True)
    customer1 = models.CharField('自定义字段1', max_length=256, blank=True, null=True)
    customer2 = models.CharField('自定义字段2', max_length=256, blank=True, null=True)
    customer3 = models.CharField('自定义字段3', max_length=256, blank=True, null=True)
    customer4 = models.CharField('自定义字段4', max_length=256, blank=True, null=True)
    customer5 = models.CharField('自定义字段5', max_length=256, blank=True, null=True)

    def __str__(self):
        return self.appsystem

    class Meta:
        verbose_name = '项目信息表'
        verbose_name_plural = "项目信息表"
        managed = True
        db_table = 't_cmdb_project_info'
        unique_together = (('pid', 'appsystem'),)

class SoftwareInfo(models.Model):
    sid = models.AutoField('软件ID', primary_key=True)
    dsdevip = models.ForeignKey('DeviceInfo', on_delete=models.CASCADE, verbose_name='设备IP地址')
    psappsystem = models.ForeignKey('ProjectInfo', on_delete=models.CASCADE, verbose_name='应用系统')
    sname = models.CharField('软件名称', max_length=64)
    stype = models.CharField('软件类型', max_length=16, blank=True, null=True)
    sport = models.CharField('软件端口', max_length=6, blank=True, null=True)
    sversion = models.CharField('版本', max_length=16, blank=True, null=True)
    spath = models.CharField('路径', max_length=128, blank=True, null=True)
    sdesc = models.CharField('软件描述', max_length=256, blank=True, null=True)
    customer1 = models.CharField('自定义字段1', max_length=256, blank=True, null=True)
    customer2 = models.CharField('自定义字段2', max_length=256, blank=True, null=True)
    customer3 = models.CharField('自定义字段3', max_length=256, blank=True, null=True)
    customer4 = models.CharField('自定义字段4', max_length=256, blank=True, null=True)
    customer5 = models.CharField('自定义字段5', max_length=256, blank=True, null=True)

    def __str__(self):
        return self.sname

    class Meta:
        verbose_name = '软件信息表'
        verbose_name_plural = "软件信息表"
        managed = True
        db_table = 't_cmdb_software_info'

class Relations(models.Model):
    rid = models.AutoField('关系ID', primary_key=True)
    drdevip = models.ForeignKey('DeviceInfo', on_delete=models.CASCADE, verbose_name='本端设备')
    srsname = models.ForeignKey('SoftwareInfo', on_delete=models.CASCADE, verbose_name='软件名称')
    upip = models.CharField('上联设备', max_length=16, blank=True, null=True)
    updesc = models.CharField('上联描述', max_length=256, blank=True, null=True)
    downip = models.CharField('下联设备', max_length=16, blank=True, null=True)
    downdesc = models.CharField('下联描述', max_length=256, blank=True, null=True)

    def __str__(self):
        return str(self.drdevip)

    class Meta:
        verbose_name = '关系表'
        verbose_name_plural = "关系表"
        managed = True
        db_table = 't_cmdb_relations'

class DpMap(models.Model):
    id = models.AutoField('映射编号', primary_key=True)
    deviceinfo_id = models.CharField('设备ID', max_length=16)
    projectinfo_id = models.CharField('系统ID', max_length=16)

    class Meta:
        verbose_name = '设备系统映射表'
        verbose_name_plural = "设备系统映射表"
        managed = False
        db_table = 't_cmdb_device_info_pdappsystem'