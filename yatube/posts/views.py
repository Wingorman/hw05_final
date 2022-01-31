from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.views.decorators.cache import cache_page


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page_obj": page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request, "group_list.html", {"group": group, "page_obj": page}
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    return render(
        request,
        "profile.html",
        {
            "author": author,
            "page_obj": page,
            "following": following,
        },
    )


def post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
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
def create(request):
    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("profile", request.user.username)
        return render(request, "new_post.html", {"form": form, "value": "new"})
    form = PostForm()
    return render(request, "new_post.html", {"form": form, "value": "new"})


@login_required
def post_edit(request, post_id):
    post_object = get_object_or_404(Post, id=post_id)
    if request.user != post_object.author:
        return redirect("post", post_id=post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post_object
    )
    if form.is_valid():
        form.save()
        return redirect("post", post_id=post_id)
    return render(request, "new_post.html", {"form": form, "value": "edit"})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("post", post_id)
    return redirect("post", post_id)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


def permission_denied(request, exception):
    return render(request, "misc/403.html", status=403)


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(
        author__following__user=request.user
    ).select_related("group")
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page_obj": page,
    }
    return render(request, "follow.html", context)


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
    follow_qs = Follow.objects.filter(author=author, user=request.user)
    if follow_qs.exists():
        follow_qs.delete()

    return redirect("profile", username=username)
