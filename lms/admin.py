from django.contrib import admin
from .models import Course, Lesson


@admin.register(Course)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(Lesson)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'description')
