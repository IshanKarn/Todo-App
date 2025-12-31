from django.urls import path
from .views import tasks_view, update_task_view, delete_task_view

urlpatterns = [
    path("", tasks_view),
    path("update/<int:task_id>/", update_task_view),
    path("delete/<int:task_id>/", delete_task_view),
]
