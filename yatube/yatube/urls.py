from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404, handler500

handler403 = "posts.views.permission_denied"  # noqa
handler404 = "posts.views.page_not_found"  # noqa
handler500 = "posts.views.server_error"  # noqa

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path("", include("posts.urls")),
    path("about/", include("about.urls", namespace="about")),
]
