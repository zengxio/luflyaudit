#!/usr/bin/env python
# coding:utf-8
from django.contrib.auth import authenticate
import subprocess, string, random
from audit import models
from django.conf import settings
from audit.backend import ssh_interactive
import datetime

class UserShell(object):
    """用户登录堡垒机后的shll"""

    def __init__(self, sys_argv):
        self.sys_argv = sys_argv
        self.user = None

    def auth(self):
        count = 0
        while count < 3:
            username = input("username: ").strip()
            password = input("password: ").strip()
            user = authenticate(username=username, password=password)
            # None 认证不成功
            # uer  对象。成功
            if not user:
                count += 1
                print("Invalid username or password!")
            else:
                self.user = user
                return True
        else:
            print("too many attempts")

    def token_auth(self):
        count = 0
        while count < 3:
            user_input=input("input you axxess token.press Enter if doesn't have:").strip()
            if len(user_input)==0:
                return
            if len(user_input)!=8:
                print("token length is 8")
            else:
                time_obj = datetime.datetime.utcnow() - datetime.timedelta(seconds=300)  # 5mins ago
                token_objs=models.Token.objects.filter(val=user_input,date__gt=time_obj)
                if token_objs:
                    token_obj=token_objs.latest()
                    if token_obj.val==user_input:
                        self.user=token_obj.account.user
                        return token_obj

    def start(self):
        """启动交互程序"""

        token_obj=self.token_auth()
        if token_obj:
            ssh_interactive.ssh_session(token_obj, self.user)
            exit()
        if self.auth():
            # print(self.user.account.host_user_binds.all())  #查找该用户的堡垒机账户
            while True:
                host_groups = self.user.account.host_groups.all()
                for index, group in enumerate(host_groups):
                    print("%s \t%s[%s]" % (index, group, group.host_user_binds.count()))
                print("%s.\t未分组机器[%s]" % (len(host_groups), self.user.account.host_user_binds.count()))
                try:
                    choice = input("select group>: ").strip()
                    if choice.isdigit():
                        choice = int(choice)
                        host_bind_list = None
                        if choice >= 0 and choice < len(host_groups):
                            selected_group = host_groups[choice]
                            host_bind_list = selected_group.host_user_binds.all()
                        elif choice == len(host_groups):  # 选择未分组机器
                            host_bind_list = self.user.account.host_user_binds.all()
                        if host_bind_list:
                            while True:
                                for index, host in enumerate(host_bind_list):
                                    print("%s.\t%s" % (index, host,))
                                choice2 = input("select host>: ").strip()
                                if choice2.isdigit():
                                    choice2 = int(choice2)
                                    if choice2 >= 0 and choice2 < len(host_bind_list):
                                        selected_host = host_bind_list[choice2]
                                        ssh_interactive.ssh_session(selected_host, self.user)

                                elif choice2 == 'b':
                                    break
                except KeyboardInterrupt as e:
                    pass
