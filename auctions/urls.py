from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("comment", views.comment, name='comment'),
    path("bid", views.bid, name="bid"),
    path('category', views.category, name="category"),
    path('category/<str:name>', views.category, name="category_detail")
]
