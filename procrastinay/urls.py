"""procrastinay URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from procrastinay.api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/me/', views.me),
    path('users/me/tasks/', views.me_tasks),
    path('users/me/class/', views.me_class),
    path('users/me/guilds/', views.me_guilds),
    path('users/<uuid:user_id>/', views.user_info),
    path('guilds/<uuid:guild_id>/', views.guild_info),
    path('guilds/<uuid:guild_id>/tasks/', views.guild_tasks),
    path('login/', views.login),
    path('classes/', views.classes)
]
