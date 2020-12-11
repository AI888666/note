from django.db import models
from user.models import User


# Create your models here.
class Note(models.Model):
    title = models.CharField(verbose_name='标题', max_length=100)
    content = models.TextField(verbose_name="内容")
    created_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    updated_time = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    is_active = models.BooleanField(verbose_name="是否删除", default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
