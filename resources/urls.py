from django.urls import path
from . import views

app_name = "resources"

urlpatterns = [
    path("", views.resource_list, name="resource_list"),  
    path("create/", views.resource_create, name="resource_create"),
    path("update/<int:pk>/", views.resource_update, name="resource_update"),
    path("delete/<int:pk>/", views.resource_delete, name="resource_delete"),
    # path("dashboard/",views.dashboard,name="dashboard"),
    path("<int:resource_id>/monthly_data/create/", views.monthly_data_create, name="monthly_data_create"),
    path("monthly_data/<int:pk>/edit/", views.monthly_data_update, name="monthly_data_update"),
]