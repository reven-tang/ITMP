# -*- coding: utf-8 -*-

from hosts import models as models_hosts
from hosts.lib.utils import prpcrypt
from django.shortcuts import render

class PreCheck:

    def __init__(self, request, options=None):
        """
        初始化
        :param options:  {
            "node": [],
            "username": "",
            "password": "",
            "port": ""
        }
        """
        if options:
            self.options = options
        else:
            print('参数错误！')

    def run(self):
        node = self.options.get('node')
        username = self.options.get("username")
        password = self.options.get("password")
        port = self.options.get("port")

        # 优先使用前台传过来的用户、密码、端口信息；
        # 其次，如果前台传递过来的为空或者无法登陆则使用数据库中的信息进行认证；
        # 最后使用公钥认证。
        decrypt_do = prpcrypt()
        ssh_rsa = ''
        host_data = []

        if node:
            for item in node:
                if not port:
                    try:
                        port = str(models_hosts.HostsInfo.objects.filter(ip=item).values_list('ssh_port', flat=True)[0])
                    except:
                        port = '22'

                if not username or not password:
                    try:
                        username = str(
                            models_hosts.HostsInfo.objects.filter(ip=item).values_list('ssh_user', flat=True)[0])
                    except:
                        username = ''

                    try:
                        encrypt_passwd = str(
                            models_hosts.HostsInfo.objects.filter(ip=item).values_list('ssh_passwd', flat=True)[0])
                        password = decrypt_do.decrypt(encrypt_passwd)
                    except:
                        try:
                            ssh_rsa = str(
                                models_hosts.HostsInfo.objects.filter(ip=item).values_list('ssh_rsa', flat=True)[0])
                        except:
                            password = ' '
                if password:
                    host_data.append(
                        {
                            "node": item,
                            "port": port,
                            "username": username,
                            "password": password,
                        },
                    )
                else:
                    host_data.append(
                        {
                            "node": item,
                            "port": port,
                            "username": username,
                            "private_key": ssh_rsa,
                        },
                    )
            if host_data:
                return host_data
            else:
                result = 0
                return result
        else:
            result = 0
            return result
