#!/usr/bin/env python
#coding:utf-8
from audit.backend import user_interaction
import sys,os

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luflyaudit.settings")
    import django
    django.setup() #手动注册django的app
    obj= user_interaction.UserShell(sys.argv)
    obj.start()