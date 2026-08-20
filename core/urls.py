from django.urls import path
from . import views
urlpatterns=[
    path("",views.dashboard,name="dashboard"),
    path("appointments/new/",views.appointment_create,name="appointment_create"),
    path("appointments/<int:pk>/status/<str:status>/",views.appointment_status,name="appointment_status"),
]
