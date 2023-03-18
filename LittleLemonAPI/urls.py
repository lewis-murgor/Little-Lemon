from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('category', views.CategoryView.as_view()),
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:id>', views.MenuItem.as_view()),
    path('api-token-auth/', obtain_auth_token),
]