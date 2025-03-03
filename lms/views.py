
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, viewsets, views
from users.permissions import IsModer, IsOwner

from .tasks import send_course_update_notifications
from .models import Course, Lesson, CourseSubscription
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    CourseSubscriptionSerializer,
)
from rest_framework.permissions import IsAuthenticated
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

    def perform_update(self, serializer):
        course_id = self.kwargs.get("pk")
        send_course_update_notifications.delay(course_id)
        serializer.save()


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
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSubscriptionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        request_body=CourseSubscriptionSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            )
        },
    )
    def post(self, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get("course")
        course_item = generics.get_object_or_404(Course.objects.all(), pk=course_id)
        subs_item = course_item.subscriptions.filter(user=user)

        # Если подписка у пользователя на этот курс есть - удаляем ее
        if subs_item.exists():
            subs_item.delete()
            message = "подписка удалена"
        # Если подписки у пользователя на этот курс нет - создаем ее
        else:
            CourseSubscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"
        # Возвращаем ответ в API
        return Response({"message": message})
