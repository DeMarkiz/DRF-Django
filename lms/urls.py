from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CourseViewSet, LessonCreateApiView, LessonListApiView,
                    LessonUpdateApiView, LessonDestroyApiView, LessonRetrieveApiView)

from rest_framework.mixins import CreateModelMixin

app_name = 'lms'

router = DefaultRouter()
router.register(r'course', CourseViewSet, basename='course')

urlpatterns = [
    path('lesson/', LessonListApiView.as_view(), name='lesson_list'),
    path('lesson/<int:pk>', LessonRetrieveApiView.as_view(), name='lesson_retrieve'),
    path('lesson/create', LessonCreateApiView.as_view(), name='lesson_create'),
    path('lesson/<int:pk>/update', LessonUpdateApiView.as_view(), name='lesson_update'),
    path('lesson/<int:pk>/delete', LessonDestroyApiView.as_view(), name='lesson_delete'),
] + router.urls
