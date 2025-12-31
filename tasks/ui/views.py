import requests
from django.shortcuts import render, redirect

API_BASE = "http://localhost:8000/api"

def tasks_view(request):
    token = request.COOKIES.get("access_token")
    if not token:
        return redirect("/auth/login/")

    headers = {"Authorization": f"Bearer {token}"}

    # ➕ CREATE TASK
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

        return redirect("/tasks/")

    # 📋 GET TASKS
    res = requests.get(
        f"{API_BASE}/tasks/",
        headers=headers,
    )

    try:
        tasks = res.json()
    except ValueError:
        tasks = []

    return render(
        request,
        "tasks/tasks.html",
        {"tasks": tasks},
    )

def update_task_view(request, task_id):
    token = request.COOKIES.get("access_token")
    if not token:
        return redirect("/auth/login/")

    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": request.POST.get("title"),
        "description": request.POST.get("description"),
        "status": request.POST.get("status"),
    }

    requests.put(
        f"{API_BASE}/tasks/{task_id}/",
        json=payload,
        headers=headers,
    )

    return redirect("/tasks/")

def delete_task_view(request, task_id):
    token = request.COOKIES.get("access_token")
    if not token:
        return redirect("/auth/login/")

    headers = {"Authorization": f"Bearer {token}"}

    requests.delete(
        f"{API_BASE}/tasks/{task_id}/",
        headers=headers,
    )

    return redirect("/tasks/")
