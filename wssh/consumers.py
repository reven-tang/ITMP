from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

import paramiko
import threading
import time, json

from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

class MyThread(threading.Thread):
    def __init__(self, id, chan):
        threading.Thread.__init__(self)
        self.chan = chan

    def run(self):
        while not self.chan.chan.exit_status_ready():
            time.sleep(0.1)
            try:
                data = self.chan.chan.recv(1024)
                async_to_sync(self.chan.channel_layer.group_send)(
                    self.chan.scope['user'].username,
                    {
                        "type": "user.message",
                        "text": bytes.decode(data)
                    },
                )
            except Exception as ex:
                print(str(ex))
        self.chan.sshclient.close()
        return False

class EchoConsumer(WebsocketConsumer):

    def connect(self):
        # 创建channels group， 命名为：用户名，并使用channel_layer写入到redis
        async_to_sync(self.channel_layer.group_add)(self.scope['user'].username, self.channel_name)
        # 返回给receive方法处理
        self.accept()

    def receive(self, text_data):
        try:
            if json.loads(text_data)['node']:
                self.sshclient = paramiko.SSHClient()
                self.sshclient.load_system_host_keys()
                self.sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.sshclient.connect(json.loads(text_data)['node'],json.loads(text_data)['port'],json.loads(text_data)['username'],json.loads(text_data)['password'])
                self.chan = self.sshclient.invoke_shell(term='xterm')
                self.chan.settimeout(0)
                t1 = MyThread(999, self)
                t1.setDaemon(True)
                t1.start()
            else:
                try:
                    self.chan.send(text_data)
                except Exception as ex:
                    print(str(ex))
        except Exception as ex:
            try:
                self.chan.send(text_data)
            except Exception as ex:
                print(str(ex))


    def user_message(self, event):
        # 消费
        self.send(text_data=event["text"])

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.scope['user'].username, self.channel_name)