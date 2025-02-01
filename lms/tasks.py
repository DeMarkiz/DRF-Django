from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from .models import Course, CourseSubscription


@shared_task
def send_course_update_notifications(course_id):
    course = Course.objects.get(id=course_id)
    last_updated_threshold = now() - timedelta(hours=4)

    if course.updated_at < last_updated_threshold:
        return "Курс недавно обновился, обновления не отправлены."

    subscription = CourseSubscription.objects.filter(course=course)
    emails = [sub.user.email for sub in subscription]

    if emails:
        send_mail(
            subject='Обновление курса',
            message=f'Материалы курса {course.title} были обновлены.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails
        )
        return 'Уведомления отправлены'