from rest_framework import generics, viewsets, views
from users.permissions import IsModer, IsOwner
from django.shortcuts import get_object_or_404

from .models import Course, Lesson, CourseSubscription
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    CourseSubscriptionSerializer,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from lms.pagination import LessonCoursesPaginator
from rest_framework.response import Response


class CourseViewSet(viewsets.ModelViewSet):
    model = Course
    serializer_class = CourseSerializer
    pagination_class = LessonCoursesPaginator

    def get_queryset(self):
        if self.request.user.groups.filter(name="Модератор").exists():
            return Course.objects.all()
        user = self.request.user
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ("list", "retrieve", "update", "partial_update"):
            permission_classes = [IsAuthenticated, IsModer | IsOwner]
        elif self.action in ("create",):
            permission_classes = [IsAuthenticated, ~IsModer]
        elif self.action in ("destroy",):
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class LessonCreateApiView(generics.CreateAPIView):
    """Создать"""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModer]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListApiView(generics.ListAPIView):
    """Список"""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]
    pagination_class = LessonCoursesPaginator

    def get_queryset(self):
        if self.request.user.groups.filter(name="Модератор").exists():
            return Lesson.objects.all()
        user = self.request.user
        return Lesson.objects.filter(owner=user)


class LessonRetrieveApiView(generics.RetrieveAPIView):
    """Получить"""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonUpdateApiView(generics.UpdateAPIView):
    """Обновить"""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonDestroyApiView(generics.DestroyAPIView):
    """Удалить"""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


class CourseSubscriptionApiView(views.APIView):
    serializer_class = CourseSubscriptionSerializer
    queryset = CourseSubscription.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get("course")
        course = get_object_or_404(Course, id=course_id)
        sub_items = self.queryset.filter(user=user, course=course)
        if sub_items.exists():
            sub_items.delete()
            message = "Подписка удалена"
        else:
            CourseSubscription.objects.create(user=user, course=course)
            message = "Подписка активирована"
        return Response({"message": message})
