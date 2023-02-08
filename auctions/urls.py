from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:id>", views.listing_page, name = "listing_page"),
    path("close/<int:id>", views.close, name = "close"),
    path("watchlist", views.watchlist, name = "watchlist"),
    path("<str:method>/<int:id>", views.add_watch, name = "add_watch"),
    path("category", views.category, name = "category"),
    path("category/<str:cat>", views.category_list, name = "category_list")
]
