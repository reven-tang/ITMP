from .. import models
from django import template
from django.db.models.aggregates import Count

# Create your views here.

# 最新文章、归档、分类、标签云
register = template.Library()

@register.simple_tag
def get_recent_posts(num=5):
    return models.Post.objects.all().order_by('-created_time')[:num]

@register.simple_tag
def archives():
    return models.Post.objects.dates('created_time', 'month', order='DESC')

@register.simple_tag
def get_categories():
    # 记得在顶部引入 count 函数
    # Count 计算分类下的文章数，其接受的参数为需要计数的模型的名称
    return models.Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)

@register.simple_tag
def get_tags():
    return models.Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)