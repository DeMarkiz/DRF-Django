from datetime import timedelta
from celery import shared_task
from django.utils.timezone import now
from users.models import CustomUser
from datetime import timedelta



@shared_task
def user_block():
    users = CustomUser.objects.filter(last_login__lt=now() - timedelta(days=30))
    if users.exists():  # Проверяем, есть ли такие пользователи
        users.update(is_active=False)