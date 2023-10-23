from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('signup/', views.signup, name='signup1'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login1'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout1'),
    path('addbot/', views.create_bot, name='addbot'),

]

