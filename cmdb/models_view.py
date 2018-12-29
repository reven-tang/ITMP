from .models import *

class Resource_Info(models.Model):
    dev_status = (
        ('online', '在线'),
        ('offline', '下线'),
        ('unknown', '未知'),
        ('fault', '故障'),
        ('backup', '备用'),
        )
    dev_type = (
        ('VM', '虚拟机'),
        ('PM', '物理机'),
        ('Other', '其他'),
    )

    devid = models.AutoField('设备ID', primary_key=True)
    devip = models.CharField('设备IP地址', max_length=16, unique=True, db_index=True)
    devname = models.CharField('设备名称', max_length=32)
    devnamealias = models.CharField('设备别名', max_length=32)
    ostype = models.CharField('操作系统', max_length=64, blank=True, null=True)
    devtype = models.CharField('设备类型', choices=dev_type, max_length=16, default='VM')
    devstatus = models.CharField('设备状态', choices=dev_status, max_length=16, default='online')
    cpusize = models.FloatField('CPU大小(GHz)', blank=True, null=True)
    cpucorecount = models.PositiveSmallIntegerField('CPU核数', blank=True, null=True)
    memsize = models.IntegerField('内存大小(GB)', blank=True, null=True)
    disksize = models.FloatField('磁盘容量(GB)', blank=True, null=True)
    location = models.CharField('机房位置', max_length=64, blank=True, null=True)
    devdesc = models.CharField('设备描述', max_length=256, blank=True, null=True)
    pid = models.CharField('项目ID', max_length=16, blank=True, null=True)
    projname = models.CharField('项目名称', max_length=16, unique=True)
    appsystem = models.CharField('应用系统', max_length=64)
    projdesc = models.CharField('项目描述', max_length=256, blank=True, null=True)
    projcontactname = models.CharField('项目联系人姓名', max_length=10, blank=True, null=True)
    projcontactphone = models.CharField('项目联系人电话', max_length=16, blank=True, null=True)
    projcontactemail = models.EmailField('项目联系人邮箱', max_length=256, blank=True, null=True)
    appcontactname = models.CharField('应用联系人姓名', max_length=10, blank=True, null=True)
    appcontactphone = models.CharField('应用联系人电话', max_length=16, blank=True, null=True)
    appcontactemail = models.EmailField('应用联系人邮箱', max_length=256, blank=True, null=True)
    groupname = models.CharField('小组名称', max_length=32, blank=True, null=True)
    sid = models.CharField('软件ID', max_length=16, blank=True, null=True)
    sname = models.CharField('软件名称', max_length=64)
    stype = models.CharField('软件类型', max_length=16, blank=True, null=True)
    sport = models.CharField('软件端口', max_length=6, blank=True, null=True)
    sversion = models.CharField('版本', max_length=16, blank=True, null=True)
    spath = models.CharField('路径', max_length=128, blank=True, null=True)
    sdesc = models.CharField('软件描述', max_length=256, blank=True, null=True)
    rid = models.CharField('关系ID', max_length=16, blank=True, null=True)
    upip = models.CharField('上联设备', max_length=16, blank=True, null=True)
    updesc = models.CharField('上联描述', max_length=256, blank=True, null=True)
    downip = models.CharField('下联设备', max_length=16, blank=True, null=True)
    downdesc = models.CharField('下联描述', max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'v_resource_info'
        managed = False

'''
定义视图
create view v_resource_info as
select p.pid,p.projname,p.appsystem,p.projdesc,p.projcontactname,p.projcontactphone,p.projcontactemail,p.appcontactname,p.appcontactphone,p.appcontactemail,p.groupname,
d.devid,d.devip,d.devname,d.devnamealias,d.ostype,d.devstatus,d.devtype,d.cpusize,d.cpucorecount,d.memsize,d.disksize,d.location ,d.devdesc,
s.sid,s.sname,s.stype,s.sport,s.sversion,s.spath,s.sdesc,
r.rid,r.upip,r.updesc,r.downip,r.downdesc
from t_cmdb_device_info d
LEFT JOIN t_cmdb_device_info_pdappsystem dp ON dp.deviceinfo_id=d.devid
LEFT JOIN t_cmdb_project_info p ON p.pid=dp.projectinfo_id
LEFT JOIN t_cmdb_software_info s ON s.dsdevip_id=d.devid and s.psappsystem_id=p.pid
LEFT JOIN t_cmdb_relations r ON r.drdevip_id=d.devid and r.srsname_id=s.sid
'''
