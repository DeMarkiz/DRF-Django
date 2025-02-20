from django.contrib import admin
from .models import Course, Lesson, CourseSubscription
from django.apps import apps

app = apps.get_app_config("lms")  # Замените на имя вашего приложения

for model in app.models.values():
    admin.site.register(model)