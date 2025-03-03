import stripe
from rest_framework.exceptions import NotFound
from config import settings
from lms.models import Course, Lesson

stripe.api_key = settings.STRIPE_API_KEY


class StripeCheckout:
    """Класс для интеграции с Stripe API, обеспечивающий создание продуктов, цен и сессий оплаты"""

    def __init__(self, content):
        self.content = self._validate_content(content)
        self.courses_url = "http://127.0.0.1:8000/courses/"
        self.lessons_url = "http://127.0.0.1:8000/lessons/"
        self.product = None
        self.price = None
        self.session = None

    def create_product(self):
        """Создание продукта в Stripe на основе материала полученного при инициализации"""
        self.product = stripe.Product.create(
            name=self.content.name, description=self.content.description
        )
        return self.product

    def create_price(self, amount):
        """Создание цены в Stripe с привязкой к продукту"""
        if self.product is None:
            raise RuntimeError("Не создан продукт в Stripe!")
        amount = round(amount)
        self.price = stripe.Price.create(
            currency="rub", unit_amount=amount * 100, product=self.product.id
        )
        return self.price

    def create_session(self):
        """Создание Stripe сессии для оплаты"""
        if self.price is None:
            raise RuntimeError("не создана цена в Stripe!")

        self.session = stripe.checkout.Session.create(
            success_url=self._get_success_url(),
            line_items=[{"price": self.price.id, "quantity": 1}],
            mode="payment",
        )
        return self.session.id, self.session.url

    @staticmethod
    def _validate_content(content):
        """Валидация контента: Проверяет, что переданный контент является экземпляром класса Course или Lesson"""
        if not isinstance(content, (Course, Lesson)):
            raise ValueError(
                "Переданный объект content должен быть экземпляром класса Course или Lesson"
            )
        return content

    def _get_success_url(self):
        """Определение URL для перенаправления"""
        return (
            self.courses_url if isinstance(self.content, Course) else self.lessons_url
        )


def retrieve_payment_status(session_id):
    """Получение статуса платежа"""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.InvalidRequestError:
        raise NotFound("Сессия с указанным ID не найдена в Stripe")
    return session.payment_status
