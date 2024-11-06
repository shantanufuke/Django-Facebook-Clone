from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="feed"),

    # AJAX URLS
    path("create_post/", views.create_post, name="create_post"),

]