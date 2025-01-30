from django.contrib import admin
from .models import Course, Lesson, CourseSubscription


@admin.register(Course)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(Lesson)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "description")

@admin.register(CourseSubscription)
class CourseSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course')
    fields = ('id', 'user', 'course')