"""
URL configuration for django_multitenant_rbac project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    DashboardView, RoleListView, RoleCreateView, RoleDeleteView, 
    RoleDetailView, MemberListView, MemberUpdateView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('login/', LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('<int:tenant_id>/dashboard/', DashboardView.as_view(), name='tenant_dashboard'),
    
    # Roles
    path('<int:tenant_id>/roles/', RoleListView.as_view(), name='role_list'),
    path('<int:tenant_id>/roles/crear/', RoleCreateView.as_view(), name='role_create'),
    path('<int:tenant_id>/roles/<int:pk>/', RoleDetailView.as_view(), name='role_detail'),
    path('<int:tenant_id>/roles/<int:pk>/eliminar/', RoleDeleteView.as_view(), name='role_delete'),

    # Members
    path('<int:tenant_id>/members/', MemberListView.as_view(), name='member_list'),
    path('<int:tenant_id>/members/<int:pk>/editar/', MemberUpdateView.as_view(), name='member_update'),
]