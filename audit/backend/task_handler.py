#!/usr/bin/env python
# encoding:utf-8
import json
from audit import models
import subprocess
from  django.conf import settings
from django.db.transaction import atomic
class Task(object):
    """处理批量任务，包括命令和文件传输"""

    def __init__(self, request):
        self.request = request
        self.errors=[]
        self.task_data=None

    def is_valid(self):
        """
        1、验证命令、主机列表合法
        :return:

        """
        task_data=self.request.POST.get("task_data")
        if task_data:
            self.task_data=json.loads(task_data)
            if self.task_data.get("task_type") == "cmd":
                if self.task_data.get("cmd") and self.task_data.get("selected_host_ids"):
                    return True
                self.errors.append({'Invalid_argument':'cmd or host_list is empty'})
            elif self.task_data.get("task_type") == 'file_transfer':
                # self.errors.append({'Invalid_argument': 'cmd or host_list is empty'})
                return True
            else:
                self.errors.append({'Invalid_argument': 'task_type is invalid'})
        self.errors.append({"Invalid_data":'task_data is not exist'})


    def run(self):
        """start task and return task id"""
        task_func=getattr(self,self.task_data.get("task_type"))
        task_id=task_func()
        return task_id

    def run_cmd(self):
        pass

    @atomic  #事务。原子操作。如果不成功不生成数据
    def cmd(self):
        """批量任务"""
        print("run multi task")
        task_obj=models.Task.objects.create(
            task_type=0,
            account=self.request.user.account,
            content=self.task_data.get('cmd'),
        )

        host_ids=set(self.task_data.get("selected_host_ids"))
        tasklog_objs = []
        for host_id in host_ids:
            tasklog_objs.append(
                models.TaskLog(task_id=task_obj.id,
                               host_user_bind_id=host_id,
                               status=3
                               )
            )
        models.TaskLog.objects.bulk_create(tasklog_objs,100)
        # #执行任务.如果写在这里，程序只会有两个结果，要么等待所有执行完毕返回，要么直接返回，无论执行成功或者不成功
        # for host_id in self.task_data.get("selected_host_ids"):
        #     t=Thread(target=self.run_cmd(),args=(host_id,self.task_data.get('cmd')))
        #     t.start()
        cmd_str="python %s %s" % (settings.MULTI_TASK_SCRIPT,task_obj.id)
        multitask_obj = subprocess.Popen(cmd_str,
                                         shell=True,stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        # print("task result..." ,multitask_obj.stdout.read(),multitask_obj.stderr.read().decode("gbk"))
        return  task_obj.id

    def file_transfer(self):
        """p批量文件"""
        print("run file transfer ")

        task_obj = models.Task.objects.create(
            task_type=1,
            account=self.request.user.account,
            content=json.dumps(self.task_data)
        )

        host_ids = set(self.task_data.get("selected_host_ids"))
        tasklog_objs = []
        for host_id in host_ids:
            tasklog_objs.append(
                models.TaskLog(task_id=task_obj.id,
                               host_user_bind_id=host_id,
                               status=3
                               )
            )
        models.TaskLog.objects.bulk_create(tasklog_objs, 100)

        cmd_str = "python %s %s" % (settings.MULTI_TASK_SCRIPT, task_obj.id)
        multitask_obj = subprocess.Popen(cmd_str,
                                         shell=True, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        # print("task result..." ,multitask_obj.stdout.read(),multitask_obj.stderr.read().decode("gbk"))
        return task_obj.id
