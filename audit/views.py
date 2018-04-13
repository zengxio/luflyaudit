from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
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