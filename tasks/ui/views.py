import requests
from django.shortcuts import render, redirect

from tasks.logger import tasks_ui_logger

API_BASE = "http://localhost:8000/api"

def tasks_view(request):
    token = request.COOKIES.get("access_token")
    if not token:
        return redirect("/auth/login/")
    
    tasks_ui_logger.info(
        f"UI_TASKS_VIEW | user_authenticated={bool(token)}"
    )

    headers = {"Authorization": f"Bearer {token}"}

    # CREATE TASK
    if request.method == "POST":
        payload = {
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "due_date": request.POST.get("due_date"),
            "status": "pending",
        }

        requests.post(
            f"{API_BASE}/tasks/",
            json=payload,
            headers=headers,
        )

        tasks_ui_logger.info(
            f"UI_TASK_CREATE | title={request.POST.get('title')} redirect=tasks"
        )

        return redirect("/tasks/")

    # GET TASKS
    res = requests.get(
        f"{API_BASE}/tasks/",
        headers=headers,
    )

    try:
        tasks = res.json()
    except ValueError as e:
        tasks_ui_logger.warning(
            f"UI_TASKS_GET_ERROR | error={str(e)}"
        )
        tasks = []

    tasks_ui_logger.info(
        f"UI_TASKS_GET | success"
    )
    
    return render(
        request,
        "tasks/tasks.html"
    )

def update_task_view(request, task_id):
    token = request.COOKIES.get("access_token")
    if not token:
        return redirect("/auth/login/")
    tasks_ui_logger.info(
        f"UI_TASK_UPDATE_ATTEMPT | user_authenticated={bool(token)}"
    )

    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": request.POST.get("title"),
        "description": request.POST.get("description"),
        "status": request.POST.get("status"),
        "due_date": request.POST.get("due_date"),
    }

    requests.put(
        f"{API_BASE}/tasks/{task_id}/",
        json=payload,
        headers=headers,
    )

    tasks_ui_logger.info(
        f"UI_TASK_UPDATE | task_id={task_id} redirect=tasks"
    )

    return redirect("/tasks/")

def delete_task_view(request, task_id):
    token = request.COOKIES.get("access_token")
    if not token:
        return redirect("/auth/login/")
    
    tasks_ui_logger.info(
        f"UI_TASK_DELETE_ATTEMPT | token={bool(token)}"
    )

    headers = {"Authorization": f"Bearer {token}"}

    requests.delete(
        f"{API_BASE}/tasks/{task_id}/",
        headers=headers,
    )

    tasks_ui_logger.info(
        f"UI_TASK_DELETE_SUCCESS | task_id={task_id} redirect=tasks"
    )

    return redirect("/tasks/")
