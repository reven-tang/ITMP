from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import markdown
from django.utils.html import strip_tags
from django.urls import reverse
from mdeditor.fields import MDTextField

# Create your models here.

class Category(models.Model):
    name = models.CharField('分类', max_length=100, unique=True, db_index=True)
    image = models.ImageField(max_length=100, upload_to='repo/image/', default='repo/image/default.png',
                              verbose_name='分类图片')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '分类表'
        verbose_name_plural = "分类表"
        managed = True
        db_table = 't_repo_category'
        unique_together = ('name',)

class Tag(models.Model):
    name = models.CharField('标签',max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '标签表'
        verbose_name_plural = "标签表"
        managed = True
        db_table = 't_repo_tag'
        unique_together = ('name',)

class Post(models.Model):
    title = models.CharField('标题',max_length=70)
    body = models.TextField('内容')
    created_time = models.DateTimeField('创建时间')
    modified_time = models.DateTimeField('修改时间',)
    excerpt = models.CharField('摘要', max_length=200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="分类")
    tags = models.ManyToManyField(Tag, verbose_name="标签")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="作者")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '文章详情表'
        verbose_name_plural = "文章详情表"
        managed = True
        db_table = 't_repo_post'
        ordering = ['-created_time']

    # 自动根据文章内容截取前50个字符生成摘要
    def save(self, *args, **kwargs):
        # 如果没有填写摘要
        if not self.excerpt:
            # 首先实例化一个 Markdown 类，用于渲染 body 的文本
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            # 先将 Markdown 文本渲染成 HTML 文本
            # strip_tags 去掉 HTML 文本的全部 HTML 标签
            # 从文本摘取前 54 个字符赋给 excerpt
            self.excerpt = strip_tags(md.convert(self.body))[:200]

        # 调用父类的 save 方法将数据保存到数据库中
        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('repo:detail', kwargs={'pk': self.pk})
