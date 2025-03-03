from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course
from lms.tests import LessonTestCase
from users.models import Payment, CustomUser


class PaymentTestCase(APITestCase):
    def setUp(self):
        """Подготовка данных для тестов"""
        self.moderator_user = CustomUser.objects.create(email="moderator@test.com")
        self.moderator_group = Group.objects.create(name="moderators")
        self.moderator_user.groups.add(self.moderator_group)
        self.student = CustomUser.objects.create(email="student@test.com")
        self.new_user = CustomUser.objects.create(email="new_user@test.com")
        self.course = Course.objects.create(
            name="Тестовый курс",
            description="Описание тестового курса",
            owner=CustomUser.objects.create(email="author@test.com"),
        )
        self.create_url = reverse("users:payments-create")
        self.data_for_api = {"amount": 30_000, "paid_course": self.course.pk}
        self.db_data = (
            {
                "amount": 30_000.0,
                "payment_method": Payment.PAYMENT_TRANSFER,
                "user": self.student.pk,
                "paid_course": self.course.pk,
            },
            {
                "amount": 30_000.0,
                "payment_method": Payment.PAYMENT_CASH,
                "user": self.student.pk,
                "paid_course": self.course.pk,
            },
        )

    def test_create_payment(self):
        """Тест создания платежей"""
        # === 1. Тест неавторизованным пользователем ===
        response = self.client.post(self.create_url, data=self.data_for_api)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # === 2. Тест авторизованным пользователем ===
        self.client.force_authenticate(user=self.student)
        # №1 – Успешное создание платежа переводом
        response = self.client.post(self.create_url, data=self.data_for_api)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            **LessonTestCase.select_data_for_comparison(
                result=self.convert_amount_in_response(response),
                expected=self.db_data[0],
                keys=("amount", "payment_method", "user", "paid_course"),
            )
        )
        self.assertTrue(
            response.json().get("link") is not None
            and response.json().get("status") is not None
        )
        # №2 – Успешное создание платежа наличными
        data_for_api = {**self.data_for_api, **{"payment_method": Payment.PAYMENT_CASH}}
        response = self.client.post(self.create_url, data_for_api)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            **LessonTestCase.select_data_for_comparison(
                result=self.convert_amount_in_response(response),
                expected=self.db_data[1],
                keys=("amount", "payment_method", "user", "paid_course"),
            )
        )
        self.assertTrue(
            response.json().get("link") is not None
            and response.json().get("status") is not None
        )
        # === 3. Тест модератором ===
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.post(self.create_url, data=self.data_for_api)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_payment_status(self):
        """Тест проверки статуса"""
        session_id = ""
        retrieve_url = ""
        # === 1. Тест студентом и модератором ===
        for n, user in enumerate((self.student, self.moderator_user)):
            self.client.force_authenticate(user=user)
            if n == 0:  # создание платежа студентом
                session_id = self.client.post(
                    self.create_url, data=self.data_for_api
                ).json()["session_id"]
                retrieve_url = reverse("users:payment-status", args=(session_id,))
            response = self.client.get(retrieve_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                first=response.json(),
                second={
                    "session_id": session_id,
                    "payment_status": Payment.STATUS_UNPAID,
                },
            )
        # === 2. Тест пользователем, который еще не купил курс
        self.client.force_authenticate(user=self.new_user)
        response = self.client.get(retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @staticmethod
    def convert_amount_in_response(response):
        """Преобразование значения amount в ответе к типу Float"""
        result = response.json()
        result["amount"] = float(result["amount"])
        return result
