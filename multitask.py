import sys,os
import multiprocessing
import json
import paramiko
def cmd_run(tasklog_id,task_id,cmd_str):

    try:
        import django
        django.setup()
        from audit import models
        tasklog_obj = models.TaskLog.objects.get(id=tasklog_id)
        print("fdasdfasfds",tasklog_obj)
        print("run cmd:", tasklog_obj, cmd_str)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #自动填yes
        ssh.connect(tasklog_obj.host_user_bind.host.ip_addr,
                    tasklog_obj.host_user_bind.host.port,
                    tasklog_obj.host_user_bind.host_user.username,
                    tasklog_obj.host_user_bind.host_user.password,
                    timeout=15
                    )
        stdin, stdout, stderr = ssh.exec_command(cmd_str)
        result=stdout.read()+stderr.read()

        ssh.close()

        tasklog_obj.result=result or 'cmd has no result output.'
        tasklog_obj.status=0
        tasklog_obj.save()
    except Exception as e:
        print("error:",e)

def file_transfer(bind_host_obj):
    pass

#要引用django必须先导入。因为这个脚本运行在django体系外的进程
# 1.根据taskid拿到任务对象，
# 2.拿到任务关联的所有主机
# 3.根据任务类型调用多进程，执行不同的方法(利用多核)
# 4.每个子任务执行完毕后，自己把结果写入数据库

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 找到luflyaudit
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luflyaudit.settings")
    import django
    django.setup()
    from audit import models

    task_id=sys.argv[1]
    task_obj=models.Task.objects.get(id=task_id)
    pool=multiprocessing.Pool(processes=10)
    if task_obj.task_type==0:
        task_func=cmd_run
    else:
        task_func=file_transfer
  
    for bind_host in task_obj.tasklog_set.all():
        pool.apply_async(task_func,args=(bind_host.id,task_obj.id,task_obj.content))

    pool.close()
    print("---",task_obj)
    pool.join()


