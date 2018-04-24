import datetime
import json
import random
import string,os
import zipfile
from wsgiref.util import FileWrapper   #专门下载文件的模块 #from django.core.servers.basehttp import FileWrapper
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, redirect

from audit import models
from audit.backend import task_handler
from  django.views.decorators.csrf import csrf_exempt
from django import conf

# Create your views here.
@login_required
def index(request):
    return render(request,'index.html')

def acc_login(request):
    error=''
    if request.method=='POST':
        username=request.POST.get("username")
        password=request.POST.get("password")
        user=authenticate(username=username,password=password)  #用户认证
        if user:
            login(request,user)  #登录。前后端取用户都是request.user
            return redirect(request.GET.get('next') or '/')  #实现当用户输入hostlist的时候。登录后就显示hostlist
        else:
            error="Wrong username or password!"

    return render(request,'login.html',{'error':error})
@login_required
def acc_logout(request):
    logout(request)
    return redirect('/login/')

@login_required
def host_list(request):
    return render(request,'hostlist.html')

@login_required
def get_host_list(request):
    gid = request.GET.get("gid")
    if gid:
        if gid=='-1': #未分组
            host_list=request.user.account.host_user_binds.all()
        else:
            group_obj=request.user.account.host_groups.get(id=gid)
            host_list=group_obj.host_user_binds.all()
        data=json.dumps(list(host_list.values('id',
                              'host__hostname',
                              'host__ip_addr',
                              'host__idc__name',
                              'host__port',
                              'host_user__username',
                              'host_user__password',
        )))

        return HttpResponse(data)

@login_required
def get_token(request):
    """生成token并返回"""
    bind_host_id = request.POST.get('bind_host_id')
    time_obj=datetime.datetime.utcnow()-datetime.timedelta(seconds=300) #5mins ago
    exist_token_obj=models.Token.objects.filter(account_id=request.user.account.id,
                                                host_user_bind_id=bind_host_id,
                                                date__gt=time_obj)

    if exist_token_obj:#has token already
        token_data={'token':exist_token_obj.first().val}
    else:
        token_val=''.join(random.sample(string.ascii_lowercase+string.digits,8))
        models.Token.objects.create(
            host_user_bind_id=bind_host_id,
            account=request.user.account,
            val=token_val
        )
        token_data={'token':token_val}

    return HttpResponse(json.dumps(token_data))

@login_required
def multi_cmd(request):
    return render(request,'multi_cmd.html')

@login_required
def multitask(request):
    task_obj= task_handler.Task(request)
    if task_obj.is_valid():
        result=task_obj.run()
        return HttpResponse(json.dumps({'task_id':result}))
    return HttpResponse(json.dumps(task_obj.errors))

@login_required
def multitask_result(request):
    task_id=request.GET.get('task_id')
    task_obj=models.Task.objects.get(id=task_id)
    results=list(task_obj.tasklog_set.values('id','status',
                                'host_user_bind__host__hostname',
                                'host_user_bind__host__ip_addr',
                                'result'))
    return HttpResponse(json.dumps(results))

@login_required
def multi_file_transfer(request):
    random_str = ''.join(random.sample(string.ascii_lowercase + string.digits, 8))
    return render(request,'multi_file_transfer.html',locals()) #本地变量

@login_required
@csrf_exempt
def task_file_upload(request):
    random_str=request.GET.get('random_str')
    upload_to="%s/%s/%s"%(conf.settings.FILE_UPLOADS,request.user.account.id,random_str)
    if not os.path.isdir(upload_to):
        os.makedirs(upload_to,exist_ok=True)
    file_obj=request.FILES.get('file')
    f=open("%s/%s"%(upload_to,file_obj.name),'wb')
    for chunk in file_obj.chunks():
        f.write(chunk)
    f.close()
    return HttpResponse(json.dumps({'status':0}))

@login_required
def task_file_download(request):
    task_id=request.GET.get('task_id')
    task_file_path="%s/%s"%(conf.settings.FILE_DOWNLOADS,task_id)
    return send_zipfile(request,task_id,task_file_path)

def send_zipfile(request,task_id,file_path):
    """
    Create a ZIP file on disk and transmit it in chunks of 8KB,
    without loading the whole file into memory. A similar approach can
    be used for large dynamic PDF files.
    """
    zip_file_name = 'task_id_%s_files' % task_id
    archive = zipfile.ZipFile(zip_file_name , 'w', zipfile.ZIP_DEFLATED)
    file_list = os.listdir(file_path)
    for filename in file_list:
        archive.write('%s/%s' %(file_path,filename),arcname=filename)
    archive.close()
    wrapper = FileWrapper(open(zip_file_name,'rb')) #在内存里面打开包文件
    response = HttpResponse(wrapper, content_type='application/zip')  #渲染页面就是直接下载格式
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % zip_file_name
    response['Content-Length'] = os.path.getsize(zip_file_name)
    #temp.seek(0)
    return response
