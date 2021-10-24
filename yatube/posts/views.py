from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.views.decorators.cache import cache_page


@cache_page(20 * 1)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {"author": author, "page": page})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    post_list = author.posts.all()
    post_count = post_list.count()
    comments = Comment.objects.filter(post=post)
    form = CommentForm(request.POST or None)
    context = {
        "post": post,
        "post_count": post_count,
        "author": author,
        "comments": comments,
        "form": form,
    }
    return render(request, "post.html", context)


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")
        return render(request, "new_post.html", {"form": form, "value": "new"})
    form = PostForm()
    return render(request, "new_post.html", {"form": form, "value": "new"})


@login_required
def post_edit(request, username, post_id):
    post_object = get_object_or_404(
        Post, id=post_id, author__username=username
    )
    if request.user != post_object.author:
        return redirect("post", username=username, post_id=post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post_object
    )
    if form.is_valid():
        form.save()
        return redirect("post", username=username, post_id=post_id)
    return render(request, "new_post.html", {"form": form, "value": "edit"})


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("post", username, post_id)
    return redirect("post", username, post_id)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    followed_posts_list = Post.objects.filter(
        author__following__user=request.user
    )
    context = {"followed_posts_list": followed_posts_list}
    return render(request, "follow.html", context)


# @login_required
# def profile_follow(request, username):
#    author_to_be_followed = get_object_or_404(User, username=username)
#    Follow.objects.create(user=request.user, author=author_to_be_followed)
#    return redirect("profile", username=username)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (
        Follow.objects.filter(author=author, user=request.user).exists()
        or request.user == author
    ):
        return redirect("profile", username=username)
    Follow.objects.create(author=author, user=request.user)

    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=followed_author).delete()
    return redirect("profile", username=username)
