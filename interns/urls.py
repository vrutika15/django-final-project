from django.urls import path
from . import views

app_name = 'interns'

urlpatterns = [
    #interns
    path('', views.intern_list, name='intern_list'),
    path('add/', views.intern_create, name='intern_add'),
    path('<int:pk>/edit/', views.intern_edit, name='intern_edit'),
    path('<int:pk>/delete/', views.intern_delete, name='intern_delete'),

    #tech
    path('technologies/', views.technology_list, name='technology_list'),
    path('technologies/add/', views.technology_create, name='technology_add'),
    path('technologies/<int:pk>/edit/', views.technology_edit, name='technology_edit'),
    path('technologies/<int:pk>/delete/', views.technology_delete, name='technology_delete'),

    #navigation cards
    path('resources/',views.resources,name="resources"),
    path("projects/",views.projects,name="projects"),
    path("manageresources",views.manage_resources,name="manage_resources")
]
