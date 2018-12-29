from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
from django.db.models import Q
from . import models
import markdown
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

logger = logging.getLogger('repo.view')

# Create your views here.

# 定义知识库页面
# def repo(request):
#     post_list = models.Post.objects.all().order_by('-created_time')
#     return render(request, 'repo/repo.html', locals())

# 定义知识库主页面数据
class RepoView(LoginRequiredMixin, ListView):
    login_url = '/users/login/'
    model = models.Post
    template_name = 'repo/repo.html'
    context_object_name = 'post_list'

    # 在基于类的通用视图：ListView和DetailView中的内容，我们已将视图函数转换成了类视图。而类视图ListView已经帮我们写好了上述的分页逻辑，
    # 我们只需通过指定paginate_by属性来开启分页功能即可，即在类视图中指定paginate_by属性的值
    paginate_by = 10

# 定义知识库详细页面数据
# def detail(request, pk):
#     post = get_object_or_404(models.Post, pk=pk)
#     post.body = markdown.markdown(post.body,
#                                   extensions=[
#                                      'markdown.extensions.extra',
#                                      'markdown.extensions.codehilite',  # 语法高亮拓展
#                                      'markdown.extensions.toc',     # 允许我们自动生成目录
#                                   ])
#     return render(request, 'repo/detail.html', locals())

class RepoDetailView(LoginRequiredMixin, DetailView):
    login_url = '/users/login/'
    model = models.Post
    template_name = 'repo/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
        post = super(RepoDetailView, self).get_object(queryset=None)

        # post.body = markdown.markdown(post.body,
        #                               extensions=[
        #                                   'markdown.extensions.extra',
        #                                   'markdown.extensions.codehilite',
        #                                   'markdown.extensions.toc',
        #                               ],safe_mode=True,enable_attributes=False)

        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.nl2br',
            'markdown.extensions.smarty',
            'markdown.extensions.toc',
        ])
        # 注意：使用过程中发现了一个问题，就是markdown的换行问题，在前端界面换行显示有问题，并没有br标签，
        # 这是因为在markdown语法中两个空格加一个换行才是换行，或者两个换行才是一个换行
        # 可使用article.content.replace(“\r\n”, ’ \n’）解决，把换行符替换成两个空格 + 换行符，这样经过markdown转换后才可以转成前端的br标签
        post.body = md.convert(post.body.replace("\r\n", '  \n'))
        post.toc = md.toc

        return post


# 定义归档信息
# def archives(request, year, month):
#     post_list = models.Post.objects.filter(created_time__year=year,
#                                     created_time__month=month
#                                     ).order_by('-created_time')
#     return render(request, 'repo/repo.html', locals())

class ArchivesView(RepoView):
    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(created_time__year=year,
                                                               created_time__month=month
                                                               )

# 定义分类信息
# def category(request, pk):
#     cate = get_object_or_404(models.Category, pk=pk)
#     post_list = models.Post.objects.filter(category=cate).order_by('-created_time')
#     return render(request, 'repo/repo.html', locals())

class CategoryView(RepoView):
    def get_queryset(self):
        cate = get_object_or_404(models.Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)

# 定义标签云
class TagView(RepoView):
    def get_queryset(self):
        tag = get_object_or_404(models.Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)

# 文章搜索
class SearchView(RepoView):
    def get_queryset(self):
        q = self.request.GET.get('q')
        return super(SearchView, self).get_queryset().filter(Q(title__icontains=q) | Q(body__icontains=q))

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        q = self.request.GET.get('q')
        if not q:
            context['error_msg'] = '请输入关键词!'

        return context

# def search(request):
#     q = request.GET.get('q')
#     error_msg = ''
#
#     if not q:
#         error_msg = "请输入关键词"
#         return render(request, 'repo/repo.html', {'error_msg': error_msg})
#
#     post_list = models.Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
#     return render(request, 'repo/repo.html', {'error_msg': error_msg,
#                                                'post_list': post_list})