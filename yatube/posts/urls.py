from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("follow/", views.follow_index, name="follow_index"),
    path(
        "profile/<str:username>/follow/",
        views.profile_follow,
        name="profile_follow",
    ),
    path(
        "profile/<str:username>/unfollow/",
        views.profile_unfollow,
        name="profile_unfollow",
    ),
    path("404/", views.page_not_found, name="404"),
    path("500/", views.server_error, name="500"),
    path("group/<slug:slug>/", views.group_posts, name="group"),
    path("new/", views.new_post, name="new_post"),
    path(
        "<str:username>/<int:post_id>/comment/",
        views.add_comment,
        name="add_comment",
    ),
    path("<str:username>/", views.profile, name="profile"),
    path("<str:username>/<int:post_id>/", views.post_view, name="post"),
    path(
        "<str:username>/<int:post_id>/edit/", views.post_edit, name="post_edit"
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
