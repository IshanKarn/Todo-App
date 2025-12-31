from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from auth_app.api.permissions import IsJWTAuthenticated
from auth_app.authentication import JWTAuthentication

from tasks.logger import tasks_api_logger

from drf_spectacular.utils import extend_schema, OpenApiResponse

class TaskAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsJWTAuthenticated]

    @extend_schema(
        operation_id="tasks_list",
        summary="List tasks",
        description="List all tasks ordered by nearest due date",
        responses={
            200: OpenApiResponse(
                response={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "due_date": {"type": "string", "format": "date"},
                            "status": {"type": "string"},
                        },
                    },
                }
            )
        },
    )
    def get(self, request):
        """Retrieve logged-in user's tasks"""
        user_id = request.user["user_id"]

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, description, due_date, status
                FROM tasks
                WHERE user_id = %s
                """,
                [user_id],
            )
            rows = cursor.fetchall()

        tasks = [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "due_date": row[3],
                "status": row[4],
            }
            for row in rows
        ]

        tasks_api_logger.info(
            f"TASKS_RETRIVED | user_id={user_id}"
        )

        return Response(tasks)

    @extend_schema(
        operation_id="tasks_create",
        summary="Create task",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "due_date": {"type": "string", "format": "date"},
                },
                "required": ["title"],
            }
        },
        responses={
            201: OpenApiResponse(description="Task created"),
        },
    )
    def post(self, request):
        """Create task for logged-in user"""
        user_id = request.user["user_id"]
        data = request.data

        if not data.get("title"):
            return Response({"error": "Title is required"}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tasks (title, description, due_date, status, user_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [
                    data.get("title"),
                    data.get("description"),
                    data.get("due_date"),
                    data.get("status", "pending"),
                    user_id,
                ],
            )

        tasks_api_logger.info(
            f"TASK_CREATED | user_id={user_id} title={data.get('title')}"
        )

        return Response({"message": "Task created"}, status=status.HTTP_201_CREATED)

class TaskDetailAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsJWTAuthenticated]

    @extend_schema(
        operation_id="tasks_retrieve",
        summary="Retrieve task",
        responses={200: OpenApiResponse(description="Task details")},
    )
    def get(self, request, task_id):
        user_id = request.user["user_id"]

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, description, due_date, status
                FROM tasks
                WHERE id = %s AND user_id = %s
                """,
                [task_id, user_id],
            )
            row = cursor.fetchone()

        if not row:
            return Response({"error": "Task not found"}, status=404)

        tasks_api_logger.info(
            f"TASK_RETRIVED | user_id={user_id}"
        )

        return Response({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "due_date": row[3],
            "status": row[4],
        })

    @extend_schema(
        operation_id="tasks_update",
        summary="Update task",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {"type": "string"},
                },
            }
        },
        responses={200: OpenApiResponse(description="Task updated")},
    )
    def put(self, request, task_id):
        user_id = request.user["user_id"]
        data = request.data

        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE tasks
                SET title=%s, description=%s, due_date=%s, status=%s
                WHERE id=%s AND user_id=%s
                """,
                [
                    data.get("title"),
                    data.get("description"),
                    data.get("due_date"),
                    data.get("status"),
                    task_id,
                    user_id,
                ],
            )

            if cursor.rowcount == 0:
                return Response({"error": "Task not found"}, status=404)
        
        tasks_api_logger.info(
            f"TASK_UPDATED | user_id={user_id} task_id={task_id}"
        )

        return Response({"message": "Task updated"})

    @extend_schema(
        operation_id="tasks_delete",
        summary="Delete task",
        responses={200: OpenApiResponse(description="Task deleted")},
    )
    def delete(self, request, task_id):
        user_id = request.user["user_id"]

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM tasks WHERE id=%s AND user_id=%s",
                [task_id, user_id],
            )

            if cursor.rowcount == 0:
                return Response({"error": "Task not found"}, status=404)

        tasks_api_logger.warning(
            f"TASK_DELETED | user_id={user_id} task_id={task_id}"
        )

        return Response({"message": "Task deleted"})

