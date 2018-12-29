# -*- coding: utf-8 -*-

from mysite import celery_app
import datetime
from taskdo.utils.inventory import BaseInventory
from taskdo.utils.runner import AdHocRunner, CommandRunner, PlayBookRunner
from mysite.utils.insertdb_history import InsertExecHistory
from . import models

@celery_app.task
def adhoc_task(options, runcmd, hosts):
    """
    初始化
    :param options:  {
        "taskname": "",
        "node": "",
        "exc_bash": "",
        "host_data": "",
        "module": "",
        "username": "",
        # "password": "",
        "port": "",
        "script_type": ""
        "taskname": "",
        "action_user": "",
        "action_ip": "",
    }
    """
    # 解决AttributeError: 'Worker' object has no attribute '_config'报错
    from multiprocessing import current_process
    try:
        current_process()._config
    except AttributeError:
        current_process()._config = {'semprefix': '/mp'}

    taskname = options.get('taskname') or ' '
    action_user = options.get('action_user')
    action_ip = options.get('action_ip')
    node = options.get('node')
    exec_bash = runcmd
    module = options.get('module')
    username = options.get('username') or ' '
    port = options.get('port')
    script_type = options.get('script_type')

    inventory = BaseInventory(hosts)
    exec_starttime = datetime.datetime.now()
    if module:
        pass
    else:
        if int(script_type) == 0:
            module = 'shell'
        else:
            module = 'win_command'

    if not port:
        if int(script_type) == 0:
            port = '22'
        else:
            port = '5986'

    # 执行命令之前写入历史数据库
    execinfo = {'INFO': '任务正在执行，请稍等...'}
    options = {
        "identifier": taskname + '_' + str(exec_starttime),
        "exec_starttime": exec_starttime,
        "exec_endtime": exec_starttime,
        "action": "任务",
        "exec_type": "远程命令",
        "action_user": action_user,
        "action_ip": action_ip,
        "exec_state": 'Executing',
        "exec_result": execinfo,
        "exec_module": module,
        "exec_bash": exec_bash,
        "exec_node": node,
        "ssh_user": username,
        # "ssh_passwd": password,
        "ssh_port": port,
        # "ssh_rsa": ssh_rsa,
    }
    runner = InsertExecHistory(options=options)
    runner.run()

    # 执行命令
    # exec_bash = exec_bash.replace('\r\n', ' ; ')
    if len(exec_bash.split('\r\n')) == 0 and module != 'setup':
        runner = CommandRunner(inventory)

        res = runner.execute(exec_bash, 'all', module)
        results = res.results_raw
        # result_stdout = res.results_command['Server']['stdout']
    else:
        runner = AdHocRunner(inventory)

        print(runner)

        run_cmds = []
        for i, line in enumerate(exec_bash.split('\r\n')):
            if len(line.strip()) > 0:
                run_cmds.append(
                    {"action": {"module": module,
                                "args": line
                                },
                     "name": "run_cmd" + str(i + 1)
                     },
                )

        res = runner.run(run_cmds, "all")
        results = res.results_raw

    '''
    写入数据库：执行历史信息表
    '''
    exec_state = ''
    if len(results['failed']) > 0:
        exec_state = 'failed'
    elif len(results['unreachable']) > 0:
        exec_state = 'unreachable'
    elif len(results['skipped']) > 0:
        exec_state = 'skipped'
    else:
        exec_state = 'ok'

    exec_bash = exec_bash.replace('\r\n', ' ; ')
    exec_endtime = datetime.datetime.now()

    options = {
        "identifier": taskname + '_' + str(exec_starttime),
        "exec_starttime": exec_starttime,
        "exec_endtime": exec_endtime,
        "action": "任务",
        "exec_type": "远程命令",
        "action_user": action_user,
        "action_ip": action_ip,
        "exec_state": exec_state,
        "exec_result": results,
        "exec_module": module,
        "exec_bash": exec_bash,
        "exec_node": node,
        "ssh_user": username,
        # "ssh_passwd": password,
        "ssh_port": port,
        # "ssh_rsa": ssh_rsa,
    }
    runner = InsertExecHistory(options=options)
    runner.run()

    # jsonData = json.dumps(results)

@celery_app.task
def playbook_task(options, hosts):
    """
    初始化
    :param options:  {
        "taskname": "",
        "node": "",
        "module": "",
        "username": "",
        # "password": "",
        "port": "",
        "action_user": "",
        "action_ip": "",
    }
    """
    # 解决AttributeError: 'Worker' object has no attribute '_config'报错
    from multiprocessing import current_process
    try:
        current_process()._config
    except AttributeError:
        current_process()._config = {'semprefix': '/mp'}

    taskname = options.get('taskname') or ' '
    action_user = options.get('action_user')
    action_ip = options.get('action_ip')
    node = options.get('node')
    module = options.get('module')
    username = options.get('username') or ' '
    port = options.get('port')
    script_type = options.get('script_type')
    module_path = str(models.ModuleConf.objects.filter(module_name=module).values_list('module_path', flat=True)[0])
    exec_bash = module_path

    inventory = BaseInventory(hosts)
    exec_starttime = datetime.datetime.now()

    if not port:
        if int(script_type) == 0:
            port = '22'
        else:
            port = '5986'

    # 执行命令之前写入历史数据库
    execinfo = {'INFO': '任务正在执行，请稍等...'}
    options = {
        "identifier": taskname + '_' + str(exec_starttime),
        "exec_starttime": exec_starttime,
        "exec_endtime": exec_starttime,
        "action": "任务",
        "exec_type": "远程命令",
        "action_user": action_user,
        "action_ip": action_ip,
        "exec_state": 'Executing',
        "exec_result": execinfo,
        "exec_module": module,
        "exec_bash": exec_bash,
        "exec_node": node,
        "ssh_user": username,
        # "ssh_passwd": password,
        "ssh_port": port,
        # "ssh_rsa": ssh_rsa,
    }
    runner = InsertExecHistory(options=options)
    runner.run()

    # 执行playbook
    runner = PlayBookRunner(playbook_path=module_path, inventory=inventory)
    results = runner.run()

    '''
    写入数据库：执行历史信息表
    '''
    # 处理执行返回状态
    exec_state = ''
    is_failed = 0
    is_unreachable = 0
    is_skipped = 0
    is_change = 0
    is_ok = 0
    for item in node:
        if results['status'][item]['failures'] > 0:
            is_failed = 1
        elif results['status'][item]['unreachable'] > 0:
            is_unreachable = 1
        elif results['status'][item]['skipped'] > 0:
            is_skipped = 1
        elif results['status'][item]['changed'] > 0:
            is_change = 1
        else:
            is_ok = 1
    if is_failed > 0:
        exec_state = 'failed'
    elif is_unreachable > 0:
        exec_state = 'unreachable'
    elif is_skipped > 0:
        exec_state = 'skipped'
    elif is_change == 0:
        exec_state = 'unchange'
    else:
        exec_state = 'ok'

    exec_bash = exec_bash.replace('\r\n', ' ; ')
    exec_endtime = datetime.datetime.now()

    options = {
        "identifier": taskname + '_' + str(exec_starttime),
        "exec_starttime": exec_starttime,
        "exec_endtime": exec_endtime,
        "action": "任务",
        "exec_type": "模块部署",
        "action_user": action_user,
        "action_ip": action_ip,
        "exec_state": exec_state,
        "exec_result": results,
        "exec_module": module,
        "exec_bash": module_path,
        "exec_node": node,
        "ssh_user": username,
        # "ssh_passwd": password,
        "ssh_port": port,
        # "ssh_rsa": ssh_rsa,
    }
    runner = InsertExecHistory(options=options)
    runner.run()

    # jsonData = json.dumps(results)