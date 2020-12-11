from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import User
import hashlib


# Create your views here.
def reg_view(request):
    """
        处理用户注册
    """
    # GET 请求
    if request.method == "GET":
        return render(request, "user/register.html")
    # POST 请求 处理用户提交数据
    elif request.method == "POST":
        # 获取数据[用户、密码、确认密码]
        username = request.POST['username']
        password_1 = request.POST['password_1']
        password_2 = request.POST['password_2']

        # 1.判断两次密码是否一致
        if password_1 != password_2:
            return HttpResponse("两次密码不一致！")

        # 2.校验用户名是否可用
        old_users = User.objects.filter(username=username)
        if old_users:
            return HttpResponse("用户名已经注册！")

        # 3.1 插入数据时，进行密码加密：
        m = hashlib.md5()
        m.update(password_1.encode())
        password_m = m.hexdigest()

        # 3.插入数据[用户名和密码 --> user | 暂时明文存储密码]
        # 3.2 插入数据时 考虑并发 进行异常捕获
        try:
            user = User.objects.create(username=username, password=password_m)
        except Exception as e:
            print("create user error %s" % e)
            return HttpResponse("用户名已经注册！")

        # 4. 注册 则免登陆一天
        request.session['username'] = username
        request.session['uid'] = user.id
        # 修改 session 存储时间为 1天 settings.py --> SESSION_COOKIE_AGE = 60 * 60 * 24

        return HttpResponseRedirect('/index')


def login_view(request):
    """
        登录逻辑处理
    """
    # GET 请求
    if request.method == "GET":
        """
            用户登录权限验证
        """
        # 1. 检查 session 如果有 那么跳转首页；如果没有session 继续检查cookie
        if request.session.get('username') and request.session.get('uid'):
            # return HttpResponse("您已经登录。")
            return HttpResponseRedirect('/index')

        # 2. 检查 cookie 中的username 和 uid 如果有，重写session
        c_username = request.COOKIES.get('username')
        c_uid = request.COOKIES.get('uid')
        if c_username and c_uid:
            # 重写session
            request.session['username'] = c_username
            request.session['uid'] = c_uid
            # return HttpResponse("您已经登录。")
            return HttpResponseRedirect('/index')

        # 3. 没有 cookie 显示登录页面
        return render(request, "user/login.html")
    # POST 请求
    elif request.method == "POST":
        # 1.获取数据
        username = request.POST['username']
        password = request.POST['password']

        # 2.数据校验[用户名和密码 | 如何和数据库中密码进行校验md5是不可逆的]
        # 方案一：先查询用户，再查询密码(使用方案一：用户名拥有唯一索引，比and 查询快)
        # 方案二：先给密码加密，查询用户和密码
        # 2.1 查询用户
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            print("login user error is %s" % e)
            return HttpResponse("用户名和密码错误！")

        # 2.2 比对密码
        m = hashlib.md5()
        m.update(password.encode())

        if m.hexdigest() != user.password:
            return HttpResponse("用户名和密码错误！")

        # 3.记录会话保持 存入 session
        request.session['username'] = username
        request.session['uid'] = user.id

        # resp = HttpResponse("登录成功")
        resp = HttpResponseRedirect('/index')

        # 判断用户是否 选中 '记住用户名'
        # 如果选中 --> COKKIES 存储 username uid --> 时间3天
        if 'remember' in request.POST:
            resp.set_cookie('username', username, 3600 * 24 * 3)
            resp.set_cookie('uid', user.id, 3600 * 24 * 3)

        # 4.响应登录成功。
        return resp


def logout_view(request):
    """
        退出登录
    """
    # 　删除　session
    if 'username' in request.session:
        del request.session['username']
    if 'uid' in request.session:
        del request.session['uid']

    # 删除　cookies
    resp = HttpResponseRedirect('/index')
    if 'username' in request.COOKIES:
        resp.delete_cookie('username')
    if 'uid' in request.COOKIES:
        resp.delete_cookie('uid')
    return resp
