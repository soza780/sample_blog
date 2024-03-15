from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.http import require_POST
from .models import Post, Comment
from .forms import CommentForm
from taggit.models import Tag


# Create your views here.


def post_list(request,tag_slug=None):
    queryset = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        queryset = queryset.filter(tags__in=[tag])
    paginator = Paginator(queryset, 7)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts,'tag': tag})


def post_detail(request, year, month, day, slug):
    try:
        post = get_object_or_404(Post, status=Post.Status.PUBLISHED, slug=slug, publish__year=year,
                                 publish__month=month, publish__day=day)
        comments = post.comments.filter(active=True)
    except Post.DoesNotExist:
        raise Http404('Post not Found')
    form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments,'form':form})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(request, 'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment})
