from django.shortcuts import render, redirect
from django.urls import reverse

from .models import Note
from django.http import HttpResponseRedirect, HttpResponse
from user.models import User

"""
装饰器：
    1. 函数嵌套
    2. 内部函数使用外部函数参数
    3. 外部函数返回内部函数
"""


# Create your views here.
def check_login(fn):
    def wrap(request, *args, **kwargs):
        # 校验用户是否登录
        if 'username' not in request.session or 'uid' not in request.session:
            # 检查　cookies
            c_username = request.COOKIES.get('username')
            c_uid = request.COOKIES.get('uid')
            if not c_username or not c_uid:
                return HttpResponseRedirect('/user/login')
            else:
                # 回写　session
                request.session['username'] = c_username
                request.session['uid'] = c_uid
        return fn(request, *args, **kwargs)

    return wrap


@check_login
def add_note(request):
    """
        增加笔记
    """
    if request.method == "GET":
        return render(request, "note/add_note.html")
    elif request.method == "POST":
        # 获取数据
        uid = request.session['uid']
        title = request.POST['title']
        content = request.POST['content']

        # 插入数据
        Note.objects.create(title=title, content=content, user_id=uid)
        # 给响应
        # return HttpResponseRedirect('/index')
        # return HttpResponse("添加成功")
        return redirect(reverse('all'))


@check_login
def list_view(request):
    """
        页面展示
    """
    # 获取数据
    username = request.session['username']

    # 一查多 【反向属性】
    auser = User.objects.get(username=username)
    # notes = auser.note_set.all()
    notes = auser.note_set.filter(is_active=False)

    # 响应
    return render(request, "note/list_note.html", locals())


@check_login
def mod_view(request, n_id):
    """
        修改文章
    """
    username = request.session['username']
    auser = User.objects.get(username=username)
    anote = Note.objects.get(user=auser, id=n_id)
    if request.method == "GET":
        return render(request, "note/mod_note.html", locals())
    elif request.method == "POST":
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        anote.title = title
        anote.content = content
        anote.save()
        return redirect(reverse('all'))
    return render(request, "note/mod_note.html")


@check_login
def show_view(request, n_id):
    """
        查看单个文章
    """
    username = request.session['username']
    auser = User.objects.get(username=username)
    anote = Note.objects.get(user=auser, id=n_id)
    return render(request, "note/note.html", locals())


@check_login
def del_view(request, n_id):
    """
        删除文章
    """
    username = request.session['username']
    auser = User.objects.get(username=username)
    anote = Note.objects.get(user=auser, id=n_id)
    anote.is_active = True
    anote.save()
    return redirect(reverse('all'))
