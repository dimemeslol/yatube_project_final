from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .utils import pagination
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow


@cache_page(20)
def index(request):
    posts = Post.objects.all()
    page_obj = pagination(request, posts)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related()
    page_obj = pagination(request, posts)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    posts = author.posts.select_related()
    page_obj = pagination(request, posts)
    template = 'users/profile.html'
    count_user_posts = posts.count()
    following = user.is_authenticated and author.following.exists()
    context = {
        'page_obj': page_obj,
        'author': author,
        'count_user_posts': count_user_posts,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    count_user_posts = post.author.posts.count()
    template = 'posts/post_detail.html'
    comments = post.comments.select_related('post')
    form = CommentForm()
    context = {
        'post': post,
        'count_user_posts': count_user_posts,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None,
                        files=request.FILES or None,)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if request.method == 'POST':
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post.id)
        return render(
            request,
            'posts/create_post.html',
            {
                'form': form,
                'is_edit': is_edit,
            }
        )
    form = PostForm(instance=post)
    return render(
        request,
        'posts/create_post.html',
        {
            'form': form,
            'is_edit': is_edit,
        }
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    followed_authors = user.follower.values_list('author', flat=True)
    posts = Post.objects.filter(author__id__in=followed_authors)
    page_obj = pagination(request, posts)
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
        return redirect('posts:profile', username=author)
    return redirect('posts:profile', username=user)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    user = request.user
    if author != user:
        Follow.objects.get(user=user, author=author).delete()
        return redirect('posts:profile', username=author)
    return redirect('posts:profile', username=user)
