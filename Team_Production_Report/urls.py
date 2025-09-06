"""
URL configuration for Team_Production_Report project.

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
from django.urls import path, include
from . import views as core_views
from resources.views import dashboard as dashboard_view
from projects.views import tree_structure_view

urlpatterns = [
    # auth
    path("", core_views.landing, name="landing"),
    path("login/", core_views.login_view, name="login"),
    path("logout/", core_views.logout_view, name="logout"),

    # role 
    path("user/", core_views.user_home, name="user_home"),
    path("admin-site/", core_views.admin_home, name="admin_home"),
    path("superadmin/", core_views.superadmin_home, name="superadmin_home"),

    # dashboard and tree
    path("dashboard/", dashboard_view, name="dashboard"),
    path("admin-dashboard/", dashboard_view, name="admin_dashboard"),
    path("tree/", tree_structure_view, name="tree_structure"),

    path("admin/", admin.site.urls),

    path("resources/", include("resources.urls")),
    path("projects/", include("projects.urls")),
    path('interns/', include('interns.urls')),
]
    