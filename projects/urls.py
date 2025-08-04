from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("dashboard/", views.dashboard_home, name="dashboard_home"),
    path("attendance/", views.attendance_home, name="attendance_home"),
    path("team-dashboard/", views.team_dashboard_redirect, name="team_dashboard_redirect"),
    path("projects/", views.project_list, name="project_list"),
    path("projects/create/", views.project_create, name="project_create"),
    path("projects/edit/<int:pk>/", views.project_edit, name="project_edit"),
    path("projects/delete/<int:pk>/", views.project_delete, name="project_delete"),
    path("tree-structure/", views.tree_structure_view, name="tree_structure"),
]