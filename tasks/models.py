from django.db import models

# class Task(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('completed', 'Completed'),
#     ]

#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     due_date = models.DateField(null=True, blank=True)
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='pending'
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title
