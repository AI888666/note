# <网络云笔记>

## 项目介绍：
用户可在该系统中 记录 自己的 日常学习/旅游 笔记，用户的数据将被安全的存储在 云笔记平台；用户与用户之间数据为隔离存储（用户只有在登陆后才能使用相关笔记功能，且只能查阅自己的笔记内容）

## 云笔记项目 - 功能拆解

### 用户模块
1. 注册 - 成为平台用户
2. 登陆 - 校验用户身份
3. 退出登陆 - 退出登陆状态

### 笔记模块
1. 查看笔记列表 - 查
2. 创建新笔记 - 增
3. 修改笔记 - 改
4. 删除笔记 - 删

## 项目创建
`tedu_note`
```bash 
django-admin startproject tedu_note
```
```mysql
-- 进入数据库
mysql -uroot -p12345

-- 创建数据库 
create database tedu_note default charset utf8;
```

### 配置常规配置项 -
    禁止掉csrf [POST提交403问题]
    语言更改
    时区更改
    数据库配置 - 数据库名 tedu_note
> 基本项目配置完成之后，我们需要：`migrate`

## 用户模块
创建/注册应用 user
```bash
python3 manage.py startapp user
```

### 模型类
- username CharField(max_length=30, unique=True)
- password CharField(max_length=32)
- created_time DateTimeField(auto_now_add=True)
- updated_time DateTimeField(auto_now=True)

```python
from django.db import models


# Create your models here.
class User(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=30, unique=True)
    password = models.CharField(verbose_name="密码", max_length=32)
    created_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    updated_time = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    def __str__(self):
        return 'username %s' % self.username

```

### 用户注册
- 访问url : /user/reg
- 视图函数：reg_view
- 模板位置：templates/user/register.html
```
业务逻辑分析：
    1. 请求方式：get 
        显示 注册页面
    
    2. 请求方式：post
        处理用户提交数据
        1. 判断两次密码是否一致
        2. 校验 用户名 是否可用
        3. 插入数据[用户名和密码 --> user | 暂时明文存储密码]
```
```python
# file : user/views.py 
from django.http import HttpResponse
from django.shortcuts import render
from .models import User


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
        # 3.插入数据[用户名和密码 --> user | 暂时明文存储密码]
        User.objects.create(username=username, password=password_1)
        return HttpResponse("注册成功！！！")

```
### 注册问题 - 优化

- 密码如何处理？
```python 
哈希算法 -- 给定明文，计算出 一段定长的 不可逆的值；md5, sha-25
特点：
    1. 定长输出： 不算给明文长度是多少，哈希值都是 定长的， md5 - 32位16进制 
    2. 不可逆：无法反向的计算出 对应的明文
    3. 雪崩效应： 输入改变 输出必然改变

使用场景：
    1. 密码处理
    2. 文件完整性校验

如何使用：
import hashlib 

m = hashlib.md5()
m.update(b'12345') # 里面必须为字节串
m.hexdigest() 

import hashlib

m = hashlib.md5()
m.update(b'1')
m.hexdigest() # 'c4ca4238a0b923820dcc509a6f75849b'
# 注意：如果需要重新计算的话，我们必须重新生成新的对象。
```

- 插入问题
> 开发阶段暂时没有遇到，主要是在项目上线之后，并发问题导致。
```python
def reg_view(request):
    ...
    # 3.插入数据[用户名和密码 --> user | 暂时明文存储密码]
    # 3.2 插入数据时 考虑并发 进行异常捕获
    try:
        user = User.objects.create(username=username, password=password_m)
    except Exception as e:
        print("create user error %s" % e)
        return HttpResponse("用户名已经注册！")
    ...
```
- 产品经理要求 注册 则免登陆一天 ，这功能怎么做
> 使用 会话保持技术完成。
```python
def reg_view(request):
    ...
    # 4. 注册 则免登陆一天
    request.session['username'] = username
    request.session['uid'] = user.id
    # 修改 session 存储时间为 1天 settings.py --> SESSION_COOKIE_AGE = 60 * 60 * 24
    ...
```
### 用户登录
- 访问url : /user/login
- 视图函数：login_view
- 模板位置：templates/user/login.html
```
业务逻辑分析：
    1. 请求方式：get
        显示登录页面
    2. 请求方式：post
        1. 获取数据
        2. 数据校验[用户名 和 密码 | 如何和数据库中密码进行校验 md5是不可逆的] 
        3. 记录会话保持
        4. 响应 登录成功。
```
```python
# file : user/views.py 
def login_view(request):
    """
        登录逻辑处理
    """
    # GET 请求
    if request.method == "GET":
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

        # 4.响应登录成功。
        return HttpResponse("登录成功")

```

