from django.db import models

# Create your models here.

class ExecHisotry(models.Model):
    identifier = models.CharField('唯一标识符', max_length=512)
    exec_starttime = models.DateTimeField('执行时间', auto_now_add=True)
    exec_endtime = models.DateTimeField('结束时间', auto_now_add=True)
    action_user = models.CharField('用户', max_length=256)
    action_ip = models.CharField('用户IP', max_length=16)
    action = models.CharField(max_length=20, verbose_name=u'动作')
    exec_type = models.CharField('执行类型', max_length=32)
    exec_state = models.CharField('执行状态', max_length=20)
    exec_node = models.CharField('节点列表', max_length=512)
    exec_module = models.CharField('执行模块', max_length=64, default="shell")
    ssh_user = models.CharField('ssh登录的用户', max_length=32, blank=True, null=True)
    ssh_passwd = models.CharField('ssh登录的密码', max_length=64, blank=True, null=True)
    ssh_port = models.CharField('ssh登录的端口', max_length=32, default="22")
    ssh_rsa = models.CharField('登录使用的私钥', max_length=64,blank=True, null=True)
    rsa_pass = models.CharField('私钥的密钥', max_length=64, blank=True, null=True)
    exec_bash = models.TextField(verbose_name='执行命令')
    exec_result = models.TextField(verbose_name='执行结果')

    class Meta:
        verbose_name = u'执行历史信息表'
        verbose_name_plural = verbose_name
        managed = True
        db_table = "t_exec_history"
        ordering = ['-exec_starttime']

class ModuleConf(models.Model):
    module_name = models.CharField('模块名称', max_length=32, unique=True)
    module_path = models.CharField('模块路径', max_length=512)

    class Meta:
        verbose_name = u'模块配置'
        verbose_name_plural = verbose_name
        managed = True
        db_table = "t_module_conf"