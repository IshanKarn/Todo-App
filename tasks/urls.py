from django.urls import path
from .views import TaskAPI, TaskDetailAPI

urlpatterns = [
    path("", TaskAPI.as_view()),
    path("<int:task_id>/", TaskDetailAPI.as_view()),
]
