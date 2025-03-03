from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Course, Lesson, CourseSubscription
from users.models import CustomUser


class LessonTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = CustomUser.objects.create(email="test1@teeestmail.ru")
        self.course = Course.objects.create(name="УКУСИ МЕНЯ ПЧОЛА", owner=self.user)
        self.lesson = Lesson.objects.create(
            name="изучаем питон",
            course=self.course,
            url="https://github.com/MichailFedyaev/52",
            owner=self.user,
        )
        self.course_sub = CourseSubscription.objects.create(
            user=self.user, course=self.course
        )
        self.client.force_authenticate(user=self.user)

    def test_list_lesson(self):
        url = reverse("lms:lesson_list")
        response = self.client.get(url)
        data = response.json()
        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.lesson.pk,
                    "url": "https://github.com/MichailFedyaev/52",
                    "name": "изучаем питон",
                    "preview": None,
                    "description": None,
                    "course": self.course.pk,
                    "owner": self.user.pk,
                }
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

    def test_lesson_retrieve(self):
        url = reverse("lms:lesson_retrieve", args=(self.lesson.pk,))
        response = self.client.get(url)
        data = response.json()
        # print(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.lesson.name)

    def test_lesson_create(self):
        url = reverse("lms:lesson_create")
        data = {
            "name": "utube",
            "url": "https://www.youtube.com",
            "owner": self.user.pk,
        }
        response = self.client.post(url, data)
        print(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_update(self):
        url = reverse("lms:lesson_update", args=(self.lesson.pk,))
        data = {"name": "testy"}
        response = self.client.patch(url, data)
        data = response.json()
        # print(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), "testy")

    def test_lesson_delete(self):
        url = reverse("lms:lesson_delete", args=(self.lesson.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 0)


class CourseSubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            email="ktoto@totam@mail.ru",
        )
        self.course = Course.objects.create(name="метовые гери", owner=self.user)
        self.lesson = Lesson.objects.create(
            name="люблю джанго",
            course=self.course,
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            owner=self.user,
        )
        self.course_subscription = CourseSubscription(
            user=self.user, course=self.course
        )
        self.client.force_authenticate(user=self.user)

    def test_course_subscribe(self):
        url = reverse("lms:course_subscribe")
        data = {"course": self.course.pk}
        response = self.client.post(url, data)
        data = response.json()
        # print(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["message"], "Подписка активирована")

        data = {"course": self.course.pk}
        response = self.client.post(url, data)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["message"], "Подписка удалена")
