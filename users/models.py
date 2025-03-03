from django.contrib.auth.models import AbstractUser
from django.db import models
from lms.models import Course, Lesson


class CustomUser(AbstractUser):
    """Модель пользователя"""

    username = None

    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    phone = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Телефон"
    )
    city = models.CharField(max_length=30, blank=True, null=True, verbose_name="Город")
    avatar = models.ImageField(
        upload_to="avatar", blank=True, null=True, verbose_name="Аватар"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    PAYMENT_CASH = "cash"
    PAYMENT_TRANSFER = "transfer"

    PAYMENT_CHOICES = [
        (PAYMENT_CASH, "Наличные"),
        (PAYMENT_TRANSFER, "Перевод на счет"),
    ]

    PAYMENT_CASH = "cash"
    PAYMENT_TRANSFER = "transfer"

    PAYMENT_CHOICES = [
        (PAYMENT_CASH, "Наличные"),
        (PAYMENT_TRANSFER, "Перевод на счет"),
    ]

    STATUS_UNPAID = "unpaid"
    STATUS_PAID = "paid"

    STATUS_CHOICES = [
        (STATUS_UNPAID, "не оплачено"),
        (STATUS_PAID, "оплачено"),
    ]

    METHOD_CHOICES = [(PAYMENT_CASH, "Наличные"), (PAYMENT_TRANSFER, "Перевод")]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    payment_date = models.DateField(auto_now_add=True, verbose_name="Дата оплаты")
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="payments_for_course",
        verbose_name="Курс",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="payments_for_lesson",
        verbose_name="Урок",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма платежа"
    )
    method = models.CharField(
        max_length=8,
        choices=PAYMENT_CHOICES,
        default=PAYMENT_TRANSFER,
        verbose_name="Способ оплаты",
    )

    session_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="ID сессии"
    )
    link = models.URLField(
        max_length=400, blank=True, null=True, verbose_name="ссылка на оплату"
    )
    status = models.CharField(
        max_length=6,
        choices=STATUS_CHOICES,
        default=STATUS_UNPAID,
        verbose_name="статус платежа",
    )

    def __str__(self):
        return f"Платеж {self.user} за {self.course if self.course else self.lesson}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
