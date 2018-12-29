# -*- coding: utf-8 -*-

from taskdo import models
from django.db.models import Q
import json, datetime

class InsertExecHistory:

	def __init__(self, options=None):
		"""
		初始化
		:param options:  {
		    "identifier": "",
		    "exec_starttime": "",
		    "exec_endtime": "",
		    "action_user": "",
		    "action_ip": "",
		    "action": "",
		    "exec_type": "",
			"exec_state": "",
			"exec_result" : "",
			# behind is not must be required
			"exec_module": "",
			"exec_bash" : "",
			"exec_node": [],
		    "ssh_user": "",
		    "ssh_passwd": "",
		    "ssh_port" : "",
			"ssh_rsa" : "",
			"rsa_pass" : ""
		}
		"""
		if options:
			self.options = options
			# self.action_user = request.user.username
			# self.action_ip = ''
			# try:
			# 	if request.META['HTTP_X_FORWARDED_FOR']:
			# 		self.action_ip = request.META['HTTP_X_FORWARDED_FOR']
			# 	else:
			# 		self.action_ip = request.META['REMOTE_ADDR']
			# except Exception as e:
			# 	self.action_ip = request.META['REMOTE_ADDR']
		else:
			print('参数错误！')

	def run(self):
		item = models.ExecHisotry.objects.filter(Q(identifier=self.options.get('identifier')) &
												 Q(action_user=self.options.get('action_user')) &
												 Q(exec_type=self.options.get('exec_type')))
		if item:
			models.ExecHisotry.objects.filter(Q(identifier=self.options.get('identifier')) &
												 Q(action_user=self.options.get('action_user')) &
												 Q(exec_type=self.options.get('exec_type'))
											  ).update(
												exec_endtime=self.options.get('exec_endtime'),
												exec_state=self.options.get('exec_state') or '',
												exec_result=json.dumps(self.options.get('exec_result')))
		else:
			obj = models.ExecHisotry.objects.create(
				identifier = self.options.get('identifier'),
				exec_starttime = self.options.get('exec_starttime'),
				exec_endtime = self.options.get('exec_endtime'),
				action_user = self.options.get('action_user'),
				action_ip = self.options.get('action_ip'),
				action = self.options.get('action'),
				exec_type = self.options.get('exec_type'),
				exec_state = self.options.get('exec_state') or '',
				exec_node = self.options.get('exec_node') or '',
				exec_module = self.options.get('exec_module') or '',
				ssh_user = self.options.get('ssh_user') or '',
				ssh_passwd = self.options.get('ssh_passwd') or '',
				ssh_port = self.options.get('ssh_port') or '',
				ssh_rsa = self.options.get('ssh_rsa') or '',
				rsa_pass = self.options.get('rsa_pass') or '',
				exec_bash = self.options.get('exec_bash') or '',
				exec_result = json.dumps(self.options.get('exec_result'))
			)
			obj.save()
