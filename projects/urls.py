from django.urls import path
from . import views
# from resources.views import tree_structure_view

app_name = "projects"

urlpatterns = [
    # path("", views.dashboard_home, name="home"),
    # path("dashboard/", views.dashboard_home, name="dashboard_home"),
    path("attendance/", views.attendance_home, name="attendance_home"),
    path("projects/", views.project_list, name="project_list"),
    path("projects/create/", views.project_create, name="project_create"),
    path("projects/edit/<int:pk>/", views.project_edit, name="project_edit"),
    path("projects/delete/<int:pk>/", views.project_delete, name="project_delete"),
    # path("tree-structure/", tree_structure_view, name="tree_structure"),
    path("attendance/resource/<int:resource_id>/add/", views.add_resource_attendance, name="add_resource_attendance"),
    path("attendance/project/<int:project_id>/add/", views.add_project_attendance, name="add_project_attendance"),
    path("attendance/project/<int:pk>/edit/",views.edit_project_attendance,name="edit_project_attendance"),
    path("attendance/resource/<int:pk>/edit/",views.edit_resource_attendance,name="edit_resource_attendance"),
    path('attendance/export/pdf/', views.export_attendance_pdf, name='export_attendance_pdf'),
]