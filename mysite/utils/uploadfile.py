# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import os
import json, datetime
from mysite.utils.insertdb_history import InsertExecHistory

@csrf_exempt
def upload_file(request, dir_name):
    ##################
    #  kindeditor图片上传返回数据格式说明：
    # {"error": 1, "message": "出错信息"}
    # {"error": 0, "url": "图片地址"}
    ##################
    result = {"error": 1, "message": "上传出错"}
    files = request.FILES.get("imgFile", None)
    if files:
        exec_starttime = datetime.datetime.now()
        result = file_upload(files, dir_name)
        if result['error'] == 0:
            result['url'] = "/app/mysite" + str(result['url'])

            # 获取登陆用户及IP地址
            exec_endtime = datetime.datetime.now()
            action_user = request.user.username
            action_ip = ''
            try:
                if request.META['HTTP_X_FORWARDED_FOR']:
                    action_ip = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    action_ip = request.META['REMOTE_ADDR']
            except Exception as e:
                action_ip = request.META['REMOTE_ADDR']
            options = {
                "identifier": "文件上传" + '_' + str(exec_starttime),
                "exec_starttime": exec_starttime,
                "exec_endtime": exec_endtime,
                "action_user": action_user,
                "action_ip": action_ip,
                "action": "任务",
                "exec_type": "文件上传",
                "exec_state": "ok",
                "exec_result": result,
            }
            runner = InsertExecHistory(options=options)
            runner.run()
    return render(request, 'taskdo/detail.html', {'data': json.dumps(result)})
    # return HttpResponse(json.dumps(result), content_type="application/json")

#目录创建
def upload_generation_dir(dir_name):
    today = datetime.datetime.today()
    dir_name = dir_name + '/%d/%d/' %(today.year,today.month)
    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)
    return dir_name

# 图片上传
def file_upload(files, dir_name):
    #允许上传文件类型
    # allow_suffix =['jpg', 'png', 'jpeg', 'gif', 'bmp']
    allow_suffix = ['jpg', 'png', 'jpeg', 'gif', 'bmp', 'zip', "swf", "flv", "mp3", "wav", "wma", "wmv", "mid", "avi",
                    "mpg", "asf", "rm", "rmvb", "doc", "docx", "xls", "xlsx", "ppt", "htm", "html", "txt", "zip", "rar",
                    "gz", "bz2","sh","bat","ps1"]
    file_suffix = files.name.split(".")[-1]
    if file_suffix not in allow_suffix:
        return {"error": 1, "message": "文件格式不正确"}
    relative_path_file = upload_generation_dir(dir_name)
    path=os.path.join(settings.MEDIA_ROOT, relative_path_file)
    if not os.path.exists(path): #如果目录不存在创建目录
        os.makedirs(path)
    # file_name=str(uuid.uuid1())+"."+file_suffix
    file_name=files.name
    path_file=os.path.join(path, file_name)
    file_url = settings.MEDIA_URL + relative_path_file + file_name
    open(path_file, 'wb').write(files.file.read())
    return {"error": 0, "url": file_url}